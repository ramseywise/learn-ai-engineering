# /// script
# requires-python = ">=3.10,<3.14"
# dependencies = ["numpy", "pandas", "matplotlib", "scipy", "scikit-learn", "sequenzo==0.1.42"]
# ///
"""Chapter 8: which journeys lead to a second order, and what is a customer in each state worth?

Run from this folder with: uv run ch08_states_sequences.py
"""
import contextlib
import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import adjusted_rand_score, silhouette_score

import chartstyle as cs
from retail import CHANNELS, END, JOURNEY_STATES, load_journeys, load_orders, load_truth

with contextlib.redirect_stdout(io.StringIO()):      # sequenzo prints a banner on import
    from sequenzo import SequenceData, get_distance_matrix

cs.apply()
STATES = JOURNEY_STATES
INDEX = {s: i for i, s in enumerate(STATES)}
pd.set_option("display.width", 120)

# %% load
journeys, truth = load_journeys(), load_truth("journeys")
print(len(journeys), "rows,", journeys.customer_id.nunique(), "customers,", journeys.month_index.nunique(), "months each")
print(journeys[["customer_id", "channel", "month_index", "state", "orders", "revenue"]].iloc[18:22].to_string(index=False))
print(journeys.state.value_counts().reindex(STATES).to_string())
print(journeys.groupby("state").revenue.mean().reindex(STATES).round(2).to_string())

wide = journeys.pivot(index="customer_id", columns="month_index", values="state")
letters = wide.apply(lambda row: "".join(s[0].upper() for s in row), axis=1)
print(letters.value_counts().head(6).to_string())


# %% order_log
def states_from_orders(orders, silent_months=4, months=18):
    """Turn an order log into monthly states. `churned` here is a rule, not a recorded event."""
    orders = orders.assign(month=orders.order_date.dt.to_period("M"))
    first = orders.groupby("customer_id").month.min()
    first = first[first + months - 1 <= pd.Timestamp(END).to_period("M")]
    active = set(zip(orders.customer_id, orders.month))
    rows = []
    for customer, start in first.items():
        silent = 0
        for m in range(months):
            if m == 0:
                state = "new"
            elif (customer, start + m) in active:
                state, silent = "active", 0
            else:
                silent += 1
                state = "churned" if silent >= silent_months else "lapsed"
            rows.append((customer, m, state))
    return pd.DataFrame(rows, columns=["customer_id", "month_index", "state"])


def transition_counts(frame):
    frame = frame.sort_values(["customer_id", "month_index"])
    next_state = frame.groupby("customer_id").state.shift(-1)
    pairs = frame.assign(next_state=next_state).dropna(subset=["next_state"])
    return pd.crosstab(pairs.state, pairs.next_state).reindex(index=STATES, columns=STATES, fill_value=0)


def transition_matrix(frame, absorb=True):
    counts = transition_counts(frame).to_numpy(dtype=float).copy()
    if absorb:
        counts[3] = [0, 0, 0, 1]                     # churned stays churned
    return counts / counts.sum(axis=1, keepdims=True)


from_log = states_from_orders(load_orders())
print(from_log.customer_id.nunique(), "customers from the order log with 18 months of history")
print(pd.DataFrame(transition_matrix(from_log, absorb=False), index=STATES, columns=STATES).round(3).to_string())

# How often was the rule wrong? Customers it called churned who then bought again.
order_month = from_log.sort_values(["customer_id", "month_index"])
called = order_month[order_month.state == "churned"].groupby("customer_id").month_index.min()
came_back = order_month[order_month.state == "active"].groupby("customer_id").month_index.max()
print(f"{len(called)} customers ever called churned; {(came_back.reindex(called.index) > called).sum()} of them later ordered again ({(came_back.reindex(called.index) > called).mean():.1%})")

# %% transition
P = transition_matrix(journeys)
print(pd.DataFrame(P, index=STATES, columns=STATES).round(3).to_string())
print(f"largest gap to the generator's realised matrix: {np.abs(P - np.array(truth['realised_pooled_transition'])).max():.4f}")

# %% fundamental
# Grinstead and Snell's drunkard's walk, section 11.2: states 0..4 with 0 and 4 absorbing, so we know the answer.
Q_check = np.array([[0, .5, 0], [.5, 0, .5], [0, .5, 0]])
N_check = np.linalg.inv(np.eye(3) - Q_check)
print("drunkard's walk N:", N_check.round(3).tolist(), " t:", N_check.sum(axis=1).round(3).tolist())

Q = P[:3, :3]
N = np.linalg.inv(np.eye(3) - Q)
print(pd.DataFrame(N, index=STATES[:3], columns=STATES[:3]).round(2).abs().to_string())
months_to_churn = N.sum(axis=1)
print("months to churn, pooled chain:", {s: round(float(m), 2) for s, m in zip(STATES[:3], months_to_churn)})
share = truth["realised_type_share"]
true_months = sum(share[t] * truth["by_type"][t]["months_to_churn"]["new"] for t in share)
print(f"months to churn for a new customer, truth: {true_months:.2f}")

# %% value
DISCOUNT = truth["monthly_discount"]


def rewards(frame):
    return frame.groupby("state").revenue.mean().reindex(STATES).fillna(0).to_numpy()


def chain_value(matrix, reward, discount=DISCOUNT):
    """V = R + P V / (1 + d), solved in one step rather than simulated."""
    return np.linalg.solve(np.eye(4) - matrix / (1 + discount), reward)


R = rewards(journeys)
pooled_value = chain_value(P, R)
print("pooled chain value by state:", {s: round(float(v), 2) for s, v in zip(STATES, pooled_value)})
print(f"true value of a new customer: {truth['true_value_of_new_customer']:.2f}")

rows = []
for t in share:
    part = journeys[journeys.true_journey_type == t]
    v = chain_value(transition_matrix(part), rewards(part))[0]
    rows.append({"type": t, "share": share[t], "value_estimated": v, "value_true": truth["by_type"][t]["value"]["new"], "lapsed_true": truth["by_type"][t]["value"]["lapsed"],
                 "second_order_true": truth["by_type"][t]["p_second_order"], "months_to_churn": truth["by_type"][t]["months_to_churn"]["new"]})
types = pd.DataFrame(rows).set_index("type")
print(types.round(3).to_string())
print(f"mixture of type chains: {(types.share * types.value_estimated).sum():.2f}")

channel_values = {}
for channel in CHANNELS:
    part = journeys[journeys.channel == channel]
    channel_values[channel] = (part.customer_id.nunique() / journeys.customer_id.nunique(), chain_value(transition_matrix(part), rewards(part))[0])
print({c: round(float(v[1]), 1) for c, v in channel_values.items()})
print(f"mixture of channel chains: {sum(w * v for w, v in channel_values.values()):.2f}")

# Resample customers to see how far 18 months of data pin these numbers down.
def customer_arrays(frame, last_month=17):
    """Per customer: transition counts, visits to each state, and revenue earned in each state."""
    frame = frame.sort_values(["customer_id", "month_index"])
    codes_long = frame.state.map(INDEX).to_numpy().reshape(-1, 18)[:, :last_month + 1]
    revenue_long = frame.revenue.to_numpy().reshape(-1, 18)[:, :last_month + 1]
    n = np.arange(len(codes_long))[:, None]
    counts, seen, money = np.zeros((len(n), 4, 4)), np.zeros((len(n), 4)), np.zeros((len(n), 4))
    np.add.at(counts, (n, codes_long[:, :-1], codes_long[:, 1:]), 1)
    np.add.at(seen, (n, codes_long), 1)
    np.add.at(money, (n, codes_long), revenue_long)
    return counts, seen, money


pair_counts, visits, earned = customer_arrays(journeys)
kind = journeys.sort_values(["customer_id", "month_index"]).true_journey_type.to_numpy()[::18]
n_customers = len(pair_counts)


def value_from(counts, visit, earn):
    counts = counts.copy()
    counts[3] = [0, 0, 0, 1]
    matrix = counts / counts.sum(axis=1, keepdims=True)
    return chain_value(matrix, earn / np.maximum(visit, 1))[0]


rng = np.random.default_rng(8)
draws = []
for _ in range(500):
    pick = rng.integers(0, n_customers, n_customers)
    c, v, e, k = pair_counts[pick], visits[pick], earned[pick], kind[pick]
    by_kind = {t: value_from(c[k == t].sum(axis=0), v[k == t].sum(axis=0), e[k == t].sum(axis=0)) for t in share}
    draws.append((value_from(c.sum(axis=0), v.sum(axis=0), e.sum(axis=0)), sum((k == t).mean() * by_kind[t] for t in share), by_kind["steady"]))
low, high = np.percentile(draws, [2.5, 97.5], axis=0)
print(f"95% intervals: pooled {low[0]:.0f} to {high[0]:.0f}; mixture of type chains {low[1]:.0f} to {high[1]:.0f}; steady alone {low[2]:.0f} to {high[2]:.0f}")
steady = journeys[journeys.true_journey_type == "steady"]
print("steady, active row estimated:", transition_matrix(steady)[1].round(3).tolist(), " true:", np.round(truth["transition"]["steady"][1], 3).tolist())

# %% seeds
def plain_value(frame):
    return chain_value(transition_matrix(frame), rewards(frame))[0]


rows = []
for seed in range(100, 112):
    other, known = load_journeys(seed=seed), load_truth("journeys", seed=seed)
    weights = known["realised_type_share"]
    rows.append({"truth": known["true_value_of_new_customer"], "pooled": plain_value(other),
                 "type_chains": sum(weights[t] * plain_value(other[other.true_journey_type == t]) for t in weights)})
print(pd.DataFrame(rows).agg(["mean", "min", "max"]).round(1).to_string())

# %% second_order
ever = journeys.groupby("customer_id").agg(orders=("orders", "sum"), channel=("channel", "first"), kind=("true_journey_type", "first"))
ever["second"] = ever.orders >= 2


def p_second(matrix):
    return matrix[0, 1] + matrix[0, 2] * matrix[2, 1] / (1 - matrix[2, 2])


true_second = sum(share[t] * truth["by_type"][t]["p_second_order"] for t in share)
print(f"second order within 18 months: {ever.second.mean():.3f}; truth with no time limit {true_second:.3f}; pooled chain says {p_second(P):.3f}")
print(ever.groupby("channel").second.mean().loc[CHANNELS].round(3).to_string())
print(ever.groupby("kind").second.mean().loc[list(share)].round(3).to_string())

# What a lapse does: chance of coming back, by how long the customer has been silent.
ordered = journeys.sort_values(["customer_id", "month_index"]).copy()
ordered["next_state"] = ordered.groupby("customer_id").state.shift(-1)
ordered["prev_state"] = ordered.groupby("customer_id").state.shift(1)
run = (ordered.state != ordered.state.shift()).cumsum()
ordered["run_length"] = ordered.groupby(run).cumcount() + 1
lapsed = ordered[(ordered.state == "lapsed") & ordered.next_state.notna()]
back = lapsed.groupby(lapsed.run_length.clip(upper=5)).next_state.agg(n="size", returned=lambda x: (x == "active").mean(), churned=lambda x: (x == "churned").mean())
print(back.round(3).to_string())

# %% markov_check
active = ordered[(ordered.state == "active") & ordered.next_state.notna()]
print("P(active next | active now), by the month before:")
print(active.groupby("prev_state").next_state.agg(n="size", stay=lambda x: (x == "active").mean()).round(3).to_string())
print("the same within one type (steady):")
print(active[active.true_journey_type == "steady"].groupby("prev_state").next_state.agg(n="size", stay=lambda x: (x == "active").mean()).round(3).to_string())

# %% holdout
SPLIT = 8
train = journeys[journeys.month_index <= SPLIT]
late = journeys[journeys.month_index >= SPLIT]
P_early, P_late = transition_matrix(train), transition_matrix(late)
print("fitted on months 0-8:")
print(pd.DataFrame(P_early, index=STATES, columns=STATES).round(3).to_string())
print("fitted on months 8-17:")
print(pd.DataFrame(P_late, index=STATES, columns=STATES).drop("new").round(3).to_string())


def curves(matrix, reward, months=18):
    start = np.array([1.0, 0, 0, 0])
    alive, revenue = [], []
    for _ in range(months):
        alive.append(1 - start[3])
        revenue.append(start @ reward)
        start = start @ matrix
    return np.array(alive), np.array(revenue)


observed_alive = journeys.groupby("month_index").state.apply(lambda s: (s != "churned").mean()).to_numpy()
observed_revenue = journeys.groupby("month_index").revenue.mean().to_numpy()
pooled_alive, pooled_revenue = curves(P_early, rewards(train))
mix_alive, mix_revenue = np.zeros(18), np.zeros(18)
for t in share:
    part = train[train.true_journey_type == t]
    a, r = curves(transition_matrix(part), rewards(part))
    mix_alive += share[t] * a
    mix_revenue += share[t] * r
print(f"{'':30s}{'alive at 17':>12s}{'revenue, months 9-17':>22s}")
print(f"{'observed':30s}{observed_alive[17]:12.3f}{observed_revenue[9:].sum():22.2f}")
print(f"{'pooled chain, months 0-8':30s}{pooled_alive[17]:12.3f}{pooled_revenue[9:].sum():22.2f}")
print(f"{'type chains, months 0-8':30s}{mix_alive[17]:12.3f}{mix_revenue[9:].sum():22.2f}")

# %% mixture
def fit_mixture(counts, visits_each, earned_each, k=4, iterations=300, seed=8):
    """EM for a mixture of Markov chains: no labels needed, each customer is only ever weighted by the chains' likelihood."""
    rng = np.random.default_rng(seed)
    resp = rng.dirichlet(np.ones(k), len(counts))
    for _ in range(iterations):
        weights = resp.mean(axis=0)
        chains = np.einsum("ni,nab->iab", resp, counts) + .5
        chains /= chains.sum(axis=2, keepdims=True)
        log_like = np.log(weights) + np.einsum("nab,iab->ni", counts, np.log(chains))
        resp = np.exp(log_like - log_like.max(axis=1, keepdims=True))
        resp /= resp.sum(axis=1, keepdims=True)
    chains[:, 3] = [0, 0, 0, 1]
    reward = np.einsum("ni,na->ia", resp, earned_each) / np.maximum(np.einsum("ni,na->ia", resp, visits_each), 1)
    return resp.mean(axis=0), chains, reward, log_like


early, early_visits, early_earned = customer_arrays(journeys, last_month=SPLIT)
em_weights, em_chains, em_reward, _ = fit_mixture(early, early_visits, early_earned)
em_alive, em_revenue = np.zeros(18), np.zeros(18)
for w, c, r in zip(em_weights, em_chains, em_reward):
    a, rev = curves(c, r)
    em_alive += w * a
    em_revenue += w * rev
print(f"{'mixture of 4 chains, no labels':30s}{em_alive[17]:12.3f}{em_revenue[9:].sum():22.2f}")

rows = []
for k in (2, 3, 4, 5):
    w8, c8, r8, _ = fit_mixture(pair_counts, visits, earned, k=k)
    rows.append({"k": k, "value_new": sum(w * chain_value(c, r)[0] for w, c, r in zip(w8, c8, r8))})
print(pd.DataFrame(rows).round(1).to_string(index=False), f"  truth {truth['true_value_of_new_customer']:.1f}")
found = [sum(w * chain_value(c, r)[0] for w, c, r in zip(*fit_mixture(*customer_arrays(load_journeys(seed=seed)))[:3])) for seed in range(100, 112)]
known = [load_truth("journeys", seed=seed)["true_value_of_new_customer"] for seed in range(100, 112)]
print(f"12 other seeds: mixture mean {np.mean(found):.1f}, range {min(found):.1f} to {max(found):.1f}; truth mean {np.mean(known):.1f}")
w4, c4, r4, _ = fit_mixture(pair_counts, visits, earned)
print(pd.DataFrame({"share": w4, "stay_active": c4[:, 1, 1], "active_to_churn": c4[:, 1, 3], "lapsed_to_churn": c4[:, 2, 3], "value_new": [chain_value(c, r)[0] for c, r in zip(c4, r4)]}).sort_values("value_new").round(3).to_string(index=False))

# %% chart_holdout
fig, ax = plt.subplots()
x = np.arange(18)
ax.plot(x, observed_alive * 100, color=cs.INK, lw=2.5)
ax.plot(x, pooled_alive * 100, color=cs.ORANGE)
ax.plot(x, mix_alive * 100, color=cs.BLUE, ls="--")
ax.axvline(SPLIT, color=cs.BASELINE, lw=1)
ax.text(SPLIT + .15, 62, "Fitted to the left of this line,\nscored to the right of it", color=cs.SECONDARY, va="top")
ax.text(17.2, observed_alive[17] * 100 - 2.4, "observed", color=cs.INK, va="center")
ax.text(17.2, pooled_alive[17] * 100, "pooled chain", color=cs.ORANGE, va="center")
ax.text(17.2, mix_alive[17] * 100 + 1.4, "one chain per type", color=cs.BLUE, va="center")
ax.set_xlim(0, 21)
ax.set_ylim(0, 100)
ax.set_xticks(range(0, 18, 3))
ax.set_xlabel("Months since first order")
ax.set_ylabel("Not yet churned (%)")
ax.set_title("One chain for everyone runs out of customers too fast")
cs.save(fig, "applied-sequence-holdout.png")


# %% needleman_wunsch
def edit_distance(a, b, sub, indel):
    """Needleman-Wunsch: cheapest set of insertions, deletions and substitutions turning a into b."""
    grid = np.zeros((len(a) + 1, len(b) + 1))
    grid[:, 0] = np.arange(len(a) + 1) * indel
    grid[0, :] = np.arange(len(b) + 1) * indel
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            grid[i, j] = min(grid[i - 1, j - 1] + sub[a[i - 1], b[j - 1]],
                             grid[i - 1, j] + indel,
                             grid[i, j - 1] + indel)
    return grid[-1, -1]


def trate_costs(counts):
    """Substitution cost 2 - p(i|j) - p(j|i): states that often follow each other are cheap to swap."""
    rates = counts / counts.sum(axis=1, keepdims=True)
    cost = 2 - rates - rates.T
    np.fill_diagonal(cost, 0)
    return cost


to_index = lambda s: [INDEX[x] for x in s]
pair_a, pair_b = wide.loc[1].tolist(), wide[wide.apply(lambda r: r.tolist().count("active"), axis=1) == 17].iloc[0].tolist()
print("".join(s[0].upper() for s in pair_a))
print("".join(s[0].upper() for s in pair_b))
constant = 2 * (1 - np.eye(4))
print("hand distance, substitution 2, indel 1:", edit_distance(to_index(pair_a), to_index(pair_b), constant, 1))

# %% om_distance
columns = [f"m{i:02d}" for i in wide.columns]
frame = wide.copy()
frame.columns = columns
frame = frame.reset_index()


def om_matrix(table, sm, indel=1):
    with contextlib.redirect_stdout(io.StringIO()):
        data = SequenceData(table, time=[c for c in table.columns if c != "customer_id"], states=STATES, id_col="customer_id")
        distance = get_distance_matrix(data, method="OM", sm=sm, indel=indel, norm="none")
    distance = np.asarray(distance, dtype=float)
    return (distance + distance.T) / 2


cost = trate_costs(transition_counts(journeys).to_numpy(dtype=float))
print(pd.DataFrame(cost, index=STATES, columns=STATES).round(3).to_string())

D = om_matrix(frame, "TRATE")
D_constant = om_matrix(frame, "CONSTANT")
rng = np.random.default_rng(8)
pairs = rng.integers(0, len(frame), size=(300, 2))
by_position = wide.to_numpy()
hand_constant = np.array([edit_distance(to_index(by_position[i]), to_index(by_position[j]), constant, 1) for i, j in pairs])
hand_trate = np.array([edit_distance(to_index(by_position[i]), to_index(by_position[j]), cost, 1) for i, j in pairs])
print(f"300 random pairs, largest gap between hand and sequenzo: constant {np.abs(hand_constant - D_constant[pairs[:, 0], pairs[:, 1]]).max():.4f}, TRATE {np.abs(hand_trate - D[pairs[:, 0], pairs[:, 1]]).max():.4f}")
print(f"{letters.nunique()} distinct sequences among {len(letters)} customers; mean distance {D[np.triu_indices_from(D, 1)].mean():.2f}")

# %% cluster
np.fill_diagonal(D, 0)
Z = linkage(squareform(D, checks=False), "ward")
true_type = journeys.groupby("customer_id").true_journey_type.first().loc[wide.index]
print("k  silhouette  adjusted Rand against the true types")
for k in (2, 3, 4, 5, 6, 8):
    labels = fcluster(Z, k, "maxclust")
    print(f"{k}  {silhouette_score(D, labels, metric='precomputed'):.3f}       {adjusted_rand_score(true_type, labels):.3f}")

K = 4
cluster = pd.Series(fcluster(Z, K, "maxclust"), index=wide.index, name="cluster")
ranking = journeys.groupby("customer_id").revenue.sum().groupby(cluster).mean().sort_values().index       # A earns least, D most
cluster = cluster.map(dict(zip(ranking, "ABCD")))
print(pd.crosstab(cluster, true_type)[list(share)].to_string())

summary = pd.DataFrame({"n": cluster.value_counts().sort_index(), "second_order": ever.second.groupby(cluster).mean(), "orders": ever.orders.groupby(cluster).mean(),
                        "revenue_18m": journeys.groupby("customer_id").revenue.sum().groupby(cluster).mean()})
medoids = {}
for c in sorted(cluster.unique()):
    members = np.where(cluster.values == c)[0]
    medoids[c] = letters.iloc[members[D[np.ix_(members, members)].sum(axis=1).argmin()]]
summary["medoid"] = pd.Series(medoids)
summary["channel_paid_social"] = (ever.channel == "paid_social").groupby(cluster).mean()
print(summary.round(3).to_string())

# %% chart_typical_sequences
order = list("ABCD")
colours = ListedColormap([cs.YELLOW, cs.BLUE, cs.AQUA, "#e1e0d9"])
codes = wide.replace(INDEX).astype(int).to_numpy()
fig, axes = plt.subplots(1, K, figsize=(9, 4.2), sharex=True)
for ax, c in zip(axes, order):
    rows = np.where(cluster.values == c)[0]
    ax.imshow(codes[rows][np.lexsort(codes[rows].T[::-1])], aspect="auto", cmap=colours, vmin=0, vmax=3, interpolation="nearest")
    ax.set_title(f"{c}: {len(rows)} customers", fontsize=10, fontweight="normal")
    ax.set_yticks([])
    ax.set_xticks([0, 6, 12, 17])
    ax.grid(False)
    ax.set_xlabel("Month")
fig.suptitle("Four journey shapes, from one order and gone to never leaving", x=.01, ha="left", fontsize=12, fontweight="bold")
handles = [plt.Rectangle((0, 0), 1, 1, color=colours(i)) for i in range(4)]
fig.legend(handles, STATES, ncol=4, loc="lower center", frameon=False)
fig.tight_layout(rect=(0, .08, 1, .96))
cs.save(fig, "applied-sequence-typical.png")

# %% cluster_chains
rows = []
for c in order:
    part = journeys[journeys.customer_id.isin(cluster.index[cluster == c])]
    counts = transition_counts(part).to_numpy(dtype=float) + 1     # one pseudo-count, because some clusters never visit a state
    counts[3] = [0, 0, 0, 1]
    matrix = counts / counts.sum(axis=1, keepdims=True)
    rows.append({"cluster": c, "share": (cluster == c).mean(), "value": chain_value(matrix, rewards(part))[0], "stay_active": matrix[1, 1]})
by_cluster = pd.DataFrame(rows).set_index("cluster")
print(by_cluster.round(3).to_string())
print(f"mixture of cluster chains: {(by_cluster.share * by_cluster.value).sum():.2f}   truth {truth['true_value_of_new_customer']:.2f}   pooled {pooled_value[0]:.2f}")
