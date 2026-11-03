---
origin: synthesis
sources:
  - "Jakob Nielsen, Usability 101 (Nielsen Norman Group) — https://www.nngroup.com/articles/usability-101-introduction-to-usability/"
  - "Jakob Nielsen, 10 Usability Heuristics for User Interface Design (Nielsen Norman Group) — https://www.nngroup.com/articles/ten-usability-heuristics/"
  - "Jakob Nielsen, Response Times: The 3 Important Limits (Nielsen Norman Group) — https://www.nngroup.com/articles/response-times-3-important-limits/"
  - "Katie Sherwin, Progress Indicators Make a Slow System Less Insufferable (Nielsen Norman Group) — https://www.nngroup.com/articles/progress-indicators/"
  - "Tim Neusesser and Evan Sunwall, Error-Message Guidelines (Nielsen Norman Group) — https://www.nngroup.com/articles/error-message-guidelines/"
  - "Raluca Budiu, Memory Recognition and Recall in User Interfaces (Nielsen Norman Group) — https://www.nngroup.com/articles/recognition-and-recall/"
  - "Megan Chan, Mental Models (Nielsen Norman Group) — https://www.nngroup.com/articles/mental-models/"
  - "Jakob Nielsen, Why You Only Need to Test with 5 Users (Nielsen Norman Group) — https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/"
concepts: [usability-components, usability-heuristics, response-time-limits, system-status, mental-models, recognition-over-recall, error-messages, interface-states, usability-testing, heuristic-review]
confidence: medium
cleaned: 2026-11-02
---
# 4 — UX principles

> Backend engineers can judge an API because they have been hurt by bad ones, and they usually can't say the same for a screen. A small set of tested ideas fixes that: how long people will wait and what to show them meanwhile, what they believe your system does, how an error should read, and how few people you need to watch before you learn something. None of this requires taste. You can apply all of it in a code review.

---

## What usability means

Nielsen's [Usability 101](https://www.nngroup.com/articles/usability-101-introduction-to-usability/) splits usability into five parts, which gives you more to say than "it feels clunky".

| Component | The question |
|-----------|-------------|
| Learnability | How easily can someone do a basic task the first time? |
| Efficiency | Once they've learned it, how quickly? |
| Memorability | After a period away, how fast do they get back? |
| Errors | How many, how bad, and how easily recovered from? |
| Satisfaction | Is it pleasant? |

Those parts trade off against each other. A keyboard-driven internal tool can be efficient and hard to learn, and that's the right call for an analyst using it all day. A refund form used once a year should be the other way round. So the first question in judging an interface is who uses it, how often, and for what. Everything else below follows from that.

## Waiting: three numbers

The [three response time limits](https://www.nngroup.com/articles/response-times-3-important-limits/) are old, and they rest on how attention works, so they have aged well. Under 0.1 s feels instant. Under 1 s keeps someone's flow, though they notice the delay. Past 10 s attention wanders, and they need progress and a way to stop.

```text
 0 s        0.1 s            1 s                          10 s
 |------------|---------------|----------------------------|----------▶
   feels         notices it,     needs a sign that it is     needs progress,
   instant       flow intact     working                     and a way to stop
```

For a backend engineer this converts latency numbers directly into interface requirements. Look at your p95 and find its band.

```ts
function needs(p95Seconds: number): string {
  if (p95Seconds < 0.1) return "nothing: show the result";
  if (p95Seconds < 1) return "nothing special: keep the page from jumping";
  if (p95Seconds < 10) return "a busy indicator, from early on";
  return "progress, a way to cancel, and a result that survives leaving the page";
}

for (const [what, s] of [["autocomplete", 0.05], ["save", 0.4], ["RAG answer, first token", 2.5], ["RAG answer, whole", 18], ["report export", 90]] as const) {
  console.log(`${what.padEnd(24)} ${String(s).padStart(5)} s  ${needs(s)}`);
}
```

```text
autocomplete              0.05 s  nothing: show the result
save                       0.4 s  nothing special: keep the page from jumping
RAG answer, first token    2.5 s  a busy indicator, from early on
RAG answer, whole           18 s  progress, a way to cancel, and a result that survives leaving the page
report export               90 s  progress, a way to cancel, and a result that survives leaving the page
```

The durations in that table are made-up illustrations, so substitute yours. NN/g's [article on progress indicators](https://www.nngroup.com/articles/progress-indicators/) adds that feedback should be immediate, and that an indicator earns its place for actions over about a second. Any shorter and it flickers. A team fixing perceived slowness can often do better by showing the right thing at 1 s than by shaving 200 ms off the server.

## The heuristics, as a review checklist

Nielsen's [ten heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) are the standard vocabulary. Four do most of the work for the kind of interface engineers build.

**Visibility of system status.** Tell people what's happening, promptly. In the code this means a real status per state, and no state with a blank screen.

**User control and freedom.** People make mistakes, so they need what the article calls a clearly marked emergency exit. Undo, Cancel, and Stop on a long-running job are all this.

**Recognition rather than recall.** Show options instead of making people remember them. [Budiu](https://www.nngroup.com/articles/recognition-and-recall/) explains why: recognition is easier because the interface supplies cues, and recall works from few. A menu is recognition, and a command line is recall. This bears directly on AI products, because **a blank prompt box is a recall interface.** Someone must generate the query from nothing, with no view of what's possible. Suggested questions and visible examples turn part of that into recognition.

**Help users recognise, diagnose and recover from errors.** Plain language, the precise problem, a constructive way forward.

## Mental models

A [mental model](https://www.nngroup.com/articles/mental-models/) is what someone believes about your system, and NN/g's point is that this belief is what steers their behaviour, whether or not it's accurate. People build it in large part from other products they've used. Mismatches are common, especially with new designs.

Here is a case you'll recognise (a hypothetical example): a dashboard shows a "Refresh" button. The engineer knows it re-queries a cache updated hourly, while the analyst believes it fetches live data. They click, see the same number and conclude that nothing is wrong, while the number is 50 minutes old. The code is correct and the system is doing just what it should, but the interface has taught something false. The fix is to display the model: "Data as of 09:00, updates hourly." The same gap matters more with AI products, where people come with beliefs from search engines and from talking to other people, and [chapter 5](05-ai-interfaces.md#setting-expectations) covers how to handle that.

## Every screen has more than one state

Mock-ups show the happy path. A real screen has several more states, and each is a piece of design that someone must do. If nobody does it, an engineer does it by accident at 5pm. This is my framing and not a cited taxonomy, but it's the most useful thing to check in a frontend code review.

| State | What goes wrong if nobody designs it |
|-------|-------------------------------------|
| Empty, first use | A blank box that says nothing about what belongs there |
| Empty, no results | Looks identical to "still loading" |
| Loading | A spinner forever, with no difference between slow and dead |
| Partial | Some of it arrived. Is the rest coming, or has it failed? |
| Error | "Something went wrong", with the user's input gone |
| Stale | Old data shown as if current |
| Full | 10,000 rows, or a long unbroken string |
| Ideal | The one in the mock-up |

A union type from [chapter 2](02-react-and-state.md#modelling-state-this-is-where-you-already-have-the-skills) forces this conversation: the compiler makes each state handle its own branch.

## Writing an error

NN/g's [error-message guidelines](https://www.nngroup.com/articles/error-message-guidelines/) are specific enough to apply mechanically: place the message near its source, make it noticeable by more than colour, write it for people instead of machines, offer constructive advice, don't blame, keep what the user entered, and reduce the effort of fixing it. Also, don't show an error prematurely, such as when someone merely moves focus out of an empty field, though inline errors can suit inputs people rarely get right first time.

| Before | After | What changed |
|--------|-------|--------------|
| `Error 503` | The service is busy right now. Try again in about 2 seconds. | Plain words, an action, a time |
| `Invalid input` | The file is 40 MB. The limit is 25 MB. | The precise problem, with numbers |
| `Something went wrong` | The connection was lost. Your text is still here. Retry | What happened, what's safe, what's next |
| `You entered an invalid date` | Enter the date as 2026-11-02 | No blame, shows the form |

If you log a code, keep it visible for support but secondary. An error is also a good test of your backend. If the API can only say "500", the interface can't say anything useful either, so this is an API design point as much as a UI one.

## Testing with a few people

Watching someone use your interface teaches more than almost anything else in this chapter, and engineers skip it because it sounds expensive. Nielsen's well-known [argument for five users](https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/) is a simple model: if each user reveals a share `L` of the problems, then `n` users reveal `1 - (1 - L)^n`, with `L` = 31% in his averaged projects.

```ts
const L = 0.31;
for (const n of [1, 2, 3, 5, 10, 15]) {
  const found = 1 - (1 - L) ** n;
  console.log(`n = ${String(n).padStart(2)}: ${(found * 100).toFixed(0).padStart(3)}%  ${"#".repeat(Math.round(found * 40))}`);
}
```

```text
n =  1:  31%  ############
n =  2:  52%  #####################
n =  3:  67%  ###########################
n =  5:  84%  ##################################
n = 10:  98%  #######################################
n = 15: 100%  ########################################
```

His real claim is about how to spend a budget: three rounds of five, with fixes between them, beat one round of fifteen, and the first user teaches far more than the rest. Be careful with the number, though. This code prints 84% at five users where the article rounds to 85%. The article dates from 2000 and the model from 1993, and it comes from averaged projects, so `L` differs for your product. It assumes the users come from one group. Nielsen himself says that quantitative studies need around 20 people, and that distinct user groups each need their own participants. Five users is a rule of thumb for finding problems. It won't measure anything.

What to do with it: give someone a real task, [ask them to think aloud](https://www.nngroup.com/articles/mental-models/), and then [stay quiet](https://www.nngroup.com/articles/usability-101-introduction-to-usability/). Don't explain or help. When they get stuck, ask what they expected to happen, which is where the mental model shows itself. Someone who's a stranger to the product is enough to begin with, and [zero users gives you zero insights](https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/).

## A fifteen-minute review

For a screen someone's asked you to judge, this list uses the chapter's ideas. Do it in order, and write down what you actually saw.

1. **Whose task?** Name the person, how often they do this and what success looks like. Without that, the rest is opinion.
2. **Do the task yourself**, without help, and note each moment of hesitation.
3. **Force the other states.** Empty, slow (throttle the network in DevTools), failed (block the request), long content.
4. **Time it against the three limits.** What's on screen at 1 s and at 10 s?
5. **Check the exits.** Can you cancel or undo? What happens to your input on a failure?
6. **Read every error aloud.** Would it make sense to someone who hasn't seen the code?
7. **Keyboard and zoom.** [Chapter 3's](03-accessibility.md#a-manual-pass-that-fits-in-ten-minutes) manual pass.
8. **Mental model.** What would a new user believe this does, and is that true?

A review like this finds problems. It doesn't tell you which ones matter most to real people, and heuristics can't settle a real argument about a design. That takes data, either usage figures or a test with people.

## Pitfalls

**Designing only the happy path.** *Symptom:* a demo looks great, and production has blank panels and endless spinners. Enumerate the states in the type and in the review.

**Spinner with no limit.** *Symptom:* a dead connection looks exactly like a slow one. Give it a timeout, and change the message when it's been longer than usual.

**Losing the user's input on failure.** *Symptom:* a long form or prompt vanishes on error, and people stop trusting it. Keep the input through the error path.

**Treating a heuristic as a verdict.** *Symptom:* "this violates heuristic 6" ends a discussion with no evidence. A heuristic tells you where to look. Watch someone.

**Quoting "five users" for everything.** *Symptom:* someone cites five users for a comparison of two designs. That's a quantitative question, and it needs more people.

**Testing with colleagues only.** *Symptom:* nobody struggled, and the launch went badly. They share your mental model. Find someone who doesn't.

**Fixing latency only in the server.** *Symptom:* 200 ms saved and nobody noticed. Check which limit you were on either side of the change, and what was on screen meanwhile.

## Try it

1. Take the [mock chat](../practice/README.md) with `npm start`, and walk the fifteen-minute review over it in the `busy-always` and `stalled` scenarios. Write down two things you would change. The lab isn't perfect, and it hasn't been tested on any real user.
2. Rewrite these for a person: `ECONNRESET`, `422 Unprocessable Entity`, `null`.
3. Your API's p95 is 4 s, and the product manager asks for a loading spinner. Using the limits, what else do you say?

<details>
<summary>Answers</summary>

1. Yours to judge. One candidate: `busy-always` keeps offering Retry although it asks for a 30-second wait, so a stronger design would disable the button until the time passes.
2. "The connection dropped before we got a reply. Try again." "We couldn't read the date in that field. Enter it as 2026-11-02." (Which assumes you know the field. The API must say which one.) `null` shows that a value wasn't handled at all, so find the case and write its message: for example, "Not set yet."
3. A spinner is right up to 10 s, but that's the p95, so one request in twenty takes longer and needs a message and a way out. Show it immediately, change the message after a few seconds, and let people stop. Then ask whether a part of the result could appear sooner.

</details>

## Interview checklist

| Question | Answer |
|----------|--------|
| Name the three response time limits. | 0.1 s feels instant, 1 s keeps flow, 10 s is the limit of attention. |
| What are the parts of usability? | Learnability, efficiency, memorability, errors, satisfaction. |
| Why is recognition better than recall? | The interface supplies the cues, so memory has less to do. |
| What's a mental model? | What the user believes the system does. It steers behaviour whether or not it's true. |
| What makes a good error message? | Near the source, plain language, the precise problem, what to do next, no blame, input kept. |
| Why five users? | Nielsen's model has them finding about 85% of problems in one group. It's for finding problems in rounds, not for measurement. |
| How would you review a screen fast? | Name the user and task, do it, force the bad states, time it, check the exits, read the errors, try the keyboard. |

## Next

- [Chapter 5, AI interfaces](05-ai-interfaces.md): all of this, for a system that can be confidently wrong.
- [Scoping an AI product](../../../generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product.md), for what to build before how it should look.
