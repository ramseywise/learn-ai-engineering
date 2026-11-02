"""Scoping arithmetic for a HYPOTHETICAL support-drafting assistant. Offline, standard library only.

Every volume, wage and saving below is an assumption made up for the example, not a measurement.
The prices are list prices read from each vendor's pricing page on 2026-11-02. Check them again before using this.

Run: python3 cost_model.py
"""
from dataclasses import dataclass

PRICES_AS_OF = "2026-11-02"


# %% prices
@dataclass(frozen=True)
class Price:
    """US dollars per million tokens."""
    input: float
    output: float
    cache_read: float | None = None
    cache_write: float | None = None


PRICES = {
    "Claude Haiku 5.5": Price(0.10, 0.50, 0.01, 0.125),  # prompts up to 100k tokens
    "Claude Sonnet 5.5": Price(2.00, 10.00, 0.10, 2.50),
    "Claude Opus 5.5": Price(4.00, 20.00, 0.20, 5.00),
    "OpenAI gpt-6-luna": Price(0.10, 0.50, 0.01),
    "OpenAI gpt-6.1-terra": Price(1.00, 5.00, 0.05),
    "OpenAI gpt-6.1-sol": Price(2.00, 10.00, 0.10),
    "Gemini 3.8 Flash": Price(0.75, 3.75, 0.075),  # rises to 1.50 / 7.50 on 2027-01-01
}
BATCH_DISCOUNT = 0.5
RESIDENCY_UPLIFT = 1.1


# %% one_ticket
@dataclass(frozen=True)
class Call:
    """One model call: tokens it sends that are new, and tokens it generates."""
    new_input: int
    output: int


STABLE_PREFIX = 3_000 + 1_200 + 286  # system prompt and policy, tool definitions, tool-use system prompt
TICKET = [
    Call(new_input=800, output=120),    # the customer's thread; the model asks to look up the order
    Call(new_input=400, output=150),    # the order record; the model asks to search help articles
    Call(new_input=4_000, output=500),  # the retrieved articles; the model writes the draft
]


def input_per_call(ticket=TICKET, prefix=STABLE_PREFIX):
    """Each call resends everything so far: prefix, earlier inputs, earlier outputs, its own new input."""
    sent, history = [], 0
    for call in ticket:
        sent.append(prefix + history + call.new_input)
        history += call.new_input + call.output
    return sent


def ticket_cost(price, ticket=TICKET, prefix=STABLE_PREFIX, cached_prefix=False):
    """Dollars for one ticket. `cached_prefix` reads only the shared prefix from cache; the write is added separately."""
    sent = input_per_call(ticket, prefix)
    output = sum(call.output for call in ticket)
    if cached_prefix:
        fresh = sum(sent) - prefix * len(sent)
        return (fresh * price.input + prefix * len(sent) * price.cache_read + output * price.output) / 1e6
    return (sum(sent) * price.input + output * price.output) / 1e6


sent = input_per_call()
print("input tokens per call:", sent, "total", f"{sum(sent):,}", "; output tokens", sum(c.output for c in TICKET))
print(f"{'model':<22}{'per ticket':>11}{'per 1,000':>11}")
for name, price in PRICES.items():
    cost = ticket_cost(price)
    print(f"{name:<22}{cost:>11.5f}{cost * 1000:>11.2f}")

# %% caching
CHOSEN = PRICES["Claude Sonnet 5.5"]
plain = ticket_cost(CHOSEN)
cached = ticket_cost(CHOSEN, cached_prefix=True)
print(f"Sonnet 5.5 no cache {plain:.5f}; prefix read from cache {cached:.5f}; saving {1 - cached / plain:.0%}")

# The 5-minute cache must be written again after any quiet gap. Worst case: one write every 5 minutes of a working day.
HOURS, DAYS = 10, 22
writes_per_month = HOURS * 12 * DAYS
write_premium = writes_per_month * STABLE_PREFIX * CHOSEN.cache_write / 1e6
print(f"worst-case writes a month {writes_per_month:,}, cost ${write_premium:.2f}")

# %% volume
TICKETS_PER_MONTH = 60_000
AGENTS = 40
MINUTES_PER_TICKET = 12
WAGE_PER_HOUR = 36.0
print(f"tickets per working minute {TICKETS_PER_MONTH / (HOURS * 60 * DAYS):.1f}")
print(f"agent hours a month {TICKETS_PER_MONTH * MINUTES_PER_TICKET / 60:,.0f}, "
      f"per agent {TICKETS_PER_MONTH * MINUTES_PER_TICKET / 60 / AGENTS:,.0f}")
print(f"handling cost a month ${TICKETS_PER_MONTH * MINUTES_PER_TICKET / 60 * WAGE_PER_HOUR:,.0f}")


# %% real_bill
def monthly_inference(share=1.0, cost_per_ticket=cached, tickets=TICKETS_PER_MONTH, retry_rate=0.03, tokenizer=1.0,
                      residency=1.0, eval_share=0.02):
    """A month's model bill: live tickets plus retries, plus an eval sample of all tickets at the batch discount."""
    live = tickets * share * cost_per_ticket * (1 + retry_rate)
    evals = tickets * eval_share * cost_per_ticket * BATCH_DISCOUNT
    return (live + evals + write_premium) * tokenizer * residency


rows = [("naive: tickets x sticker, no cache", TICKETS_PER_MONTH * plain),
        ("with prefix cache", TICKETS_PER_MONTH * cached),
        ("plus retries, evals and cache writes", monthly_inference()),
        ("plus a token count 30% above the estimate", monthly_inference(tokenizer=1.3)),
        ("plus regional processing at 1.1x", monthly_inference(tokenizer=1.3, residency=RESIDENCY_UPLIFT)),
        ("same, on Opus 5.5", monthly_inference(cost_per_ticket=ticket_cost(PRICES["Claude Opus 5.5"], cached_prefix=True),
                                                tokenizer=1.3, residency=RESIDENCY_UPLIFT)),
        ("same, on Haiku 5.5", monthly_inference(cost_per_ticket=ticket_cost(PRICES["Claude Haiku 5.5"], cached_prefix=True),
                                                 tokenizer=1.3, residency=RESIDENCY_UPLIFT))]
for label, dollars in rows:
    print(f"{label:<44}${dollars:>10,.2f}")
BILL = monthly_inference(tokenizer=1.3, residency=RESIDENCY_UPLIFT)

# %% roi
BUILD_COST = 2 * 6 * 15_000  # two engineers, six months, at a loaded $15,000 a month
RUN_COST = 0.5 * 15_000      # half an engineer on evals, prompts and incidents, every month
USED_SHARE = 0.6             # tickets where the agent actually works from the draft


def monthly_value(uplift, used_share=USED_SHARE):
    """Dollars of agent time released. An uplift of u means u more tickets an hour, so each takes 1 / (1 + u) of the time."""
    minutes_saved = MINUTES_PER_TICKET * (1 - 1 / (1 + uplift))
    return TICKETS_PER_MONTH * used_share * minutes_saved / 60 * WAGE_PER_HOUR


print(f"{'uplift':>7}{'minutes saved':>15}{'value/month':>13}{'net/month':>11}{'payback months':>16}{'3-yr ROI':>10}")
for uplift in (0.03, 0.07, 0.14, 0.25):
    value = monthly_value(uplift)
    net = value - BILL - RUN_COST
    payback = BUILD_COST / net if net > 0 else float("inf")
    roi = (net * 36 - BUILD_COST) / BUILD_COST
    minutes = MINUTES_PER_TICKET * (1 - 1 / (1 + uplift))
    print(f"{uplift:>7.0%}{minutes:>15.2f}{value:>13,.0f}{net:>11,.0f}{payback:>16.1f}{roi:>10.0%}")


def break_even_uplift(horizon_months=None):
    """Smallest uplift where the value covers running costs, and optionally the build too, over the horizon."""
    target = BILL + RUN_COST + (BUILD_COST / horizon_months if horizon_months else 0)
    minutes_needed = target * 60 / (TICKETS_PER_MONTH * USED_SHARE * WAGE_PER_HOUR)
    return 1 / (1 - minutes_needed / MINUTES_PER_TICKET) - 1


print(f"break-even uplift: running costs only {break_even_uplift():.1%}; "
      f"build repaid in 12 months {break_even_uplift(12):.1%}; in 36 months {break_even_uplift(36):.1%}")

model_share = BILL / monthly_value(0.14)
print(f"model bill is {model_share:.1%} of value at a 14% uplift; "
      f"a 30% wrong guess at usage moves value by ${monthly_value(0.14) - monthly_value(0.14, USED_SHARE * 0.7):,.0f} a month")

# %% build_buy
SEAT_PRICE = 150  # a hypothetical vendor's price per agent per month; not a real quote
INTEGRATION = 20_000
buy_month = AGENTS * SEAT_PRICE
build_month = BILL + RUN_COST
print(f"buy ${buy_month:,.0f}/month after ${INTEGRATION:,} integration; build ${build_month:,.0f}/month after ${BUILD_COST:,}")
for months in (12, 24, 36):
    print(f"  {months} months: buy ${INTEGRATION + buy_month * months:>9,.0f}   build ${BUILD_COST + build_month * months:>9,.0f}")


def scale_break_even(seat_price=SEAT_PRICE, horizon=36):
    """Agents at which build matches buy over the horizon, with tickets and the model bill growing with agents."""
    unit_bill = BILL / AGENTS
    fixed = (BUILD_COST - INTEGRATION) / horizon + RUN_COST
    return fixed / (seat_price - unit_bill)


print(f"agents at which build matches buy over 36 months: {scale_break_even():.0f}")

# Serving your own model: a hypothetical fixed cost for GPUs and half an engineer, against this bill.
SELF_HOST_MONTH = 20_000 + 0.5 * 15_000
print(f"self-hosting at ${SELF_HOST_MONTH:,.0f}/month matches the API at {SELF_HOST_MONTH / BILL:.1f}x this volume, "
      f"about {SELF_HOST_MONTH / BILL * TICKETS_PER_MONTH:,.0f} tickets a month")

# %% rollout
PHASES = [  # name, months, share of tickets through the model, share of those tickets where a draft is used
    ("shadow", 1, 1.00, 0.00),
    ("canary", 1, 0.05, 0.30),
    ("ramp", 2, 0.25, 0.45),
    ("general", 2, 1.00, 0.60),
]
UPLIFT = 0.07
cumulative = -BUILD_COST
month = 0
print(f"{'phase':<9}{'month':>6}{'bill':>9}{'value':>9}{'run':>8}{'net':>9}{'cumulative':>12}")
for name, months, share, used in PHASES:
    for _ in range(months):
        month += 1
        bill = monthly_inference(share=share, tokenizer=1.3, residency=RESIDENCY_UPLIFT)
        value = monthly_value(UPLIFT, used_share=share * used)
        net = value - bill - RUN_COST
        cumulative += net
        print(f"{name:<9}{month:>6}{bill:>9,.0f}{value:>9,.0f}{RUN_COST:>8,.0f}{net:>9,.0f}{cumulative:>12,.0f}")
steady = monthly_value(UPLIFT) - BILL - RUN_COST
print(f"steady net ${steady:,.0f}/month; repaid in month {month + (-cumulative) / steady:.1f}")

# %% adoption
FUNNEL = [("ticket is in a supported category", 0.70), ("draft appears in time", 0.95), ("agent opens it", 0.80), ("agent works from it", 0.75)]
share = 1.0
for step, rate in FUNNEL:
    share *= rate
    print(f"{step:<36}{rate:>5.0%}{share:>8.1%}")
print(f"value at 7% uplift: planned at 60% used ${monthly_value(UPLIFT):,.0f}; at this funnel ${monthly_value(UPLIFT, share):,.0f}")
print(f"released hours a month at 7%: {monthly_value(UPLIFT, share) / WAGE_PER_HOUR:,.0f}, "
      f"or {monthly_value(UPLIFT, share) / WAGE_PER_HOUR / (TICKETS_PER_MONTH * MINUTES_PER_TICKET / 60 / AGENTS):.1f} agents")
