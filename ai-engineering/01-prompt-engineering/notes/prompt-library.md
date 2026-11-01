---
origin: synthesis
sources:
  - https://www.promptingguide.ai/introduction/examples
  - https://www.promptingguide.ai/prompts
confidence: high
cleaned: 2026-11-01
---
# Prompt Library

> Small, copyable prompts grouped by task, each with the lesson it teaches. Most date from the GPT-3.5/GPT-4 era. The *shape* of each prompt still transfers, but strong current models rarely need the scaffolding. `{input}` marks a slot ([02](02-prompt-anatomy.md#prompt-templates)).

When you have a task and a blank prompt, you need the shape that works for that task and the lesson behind it, not a theory. Copied blindly these go wrong: without an empty case, the extraction prompt invents answers, and "exclusively" didn't stop GPT-4 adding a BMI to a medical note. Each entry here names its lesson.

Every entry is the same few moves in different proportions. Use this to find the part of a prompt to change when an entry doesn't fit:

```text
frame        "You classify..."          who is speaking, and the register
task         "Extract model names..."   the verb and the label set
format       ["model_name"]             what your parser will read
empty case   ["NA"]                     what to say when there is no answer
{input}      the slot                   content, usually before the final ask
cue          "Sentiment:"               where the answer begins
```

---

## Classification

**Zero-shot with a label set:**
```
Classify the text into neutral, negative, or positive.
Text: {input}
Sentiment:
```

**One example to pin the output format** (lowercase `neutral` instead of `Neutral`):
```
Classify the text into neutral, negative or positive.
Text: I think the vacation is okay.
Sentiment: neutral
Text: {input}
Sentiment:
```

- **Made-up labels get overridden.** Ask for `nutral` and the model still writes `Neutral`, because its prior wins. Define unusual labels explicitly and show them in examples.
- **Format matters more than correct labels.** Few-shot examples with *randomized* labels still help ([03](03-core-techniques.md#few-shot), Min 2022):
```
This is awesome! // Negative
This is bad! // Positive
Wow that movie was rad! // Positive
What a horrible show! //
```

---

## Information extraction

```
Your task is to extract model names from machine learning paper abstracts.
Your response is an array of the model names in the format ["model_name"].
If you don't find model names in the abstract or you are not sure, return ["NA"].

Abstract: {input}
```

The lesson: define the output format **and the empty case**. Without the `["NA"]` escape hatch, the model makes up an answer ([04](04-controlling-output.md#structured-output)).

---

## Question answering

**Closed-book with permission to abstain:**
```
Answer the question based on the context below. Keep the answer short and concise.
Respond "Unsure about answer" if not sure about the answer.

Context: {passage}
Question: {question}
Answer:
```

**Closed-domain rewrite**, restricted to the facts given:
```
Patient's facts:
- 20 year old female
- with a history of anorexia nervosa and depression
- blood pressure 100/50, pulse 50, height 5'5''
- referred by her nutritionist but is in denial of her illness
- reports eating fine but is severely underweight

Please rewrite the data above into a medical note, using exclusively the information above.
```
GPT-4 still added facts that weren't there (a BMI, "signs of malnutrition"). "Exclusively" isn't enough on its own, so pair it with a verification step (see [Truthfulness](#truthfulness)).

**Open-domain with "I don't know" licensed in the system framing:**
```
In this conversation between a human and the AI, the AI is helpful and friendly,
and when it does not know the answer it says "I don't know".

AI: Hi, how can I help you?
Human: {question}
```

---

## Summarization and explanation

```
{passage}

Explain the above in one sentence:
```

The content goes first and the instruction last ([02](02-prompt-anatomy.md#ordering)). Swap in "for a 10-year-old" or "as three bullet points" to control audience and form.

---

## Conversation and role prompting

```
The following is a conversation with an AI research assistant.
The assistant answers should be easy to understand even by primary school students.

Human: Hello, who are you?
AI: Greeting! I am an AI research assistant. How can I help you today?
Human: {question}
AI:
```

Changing one line of the framing ("technical and scientific" → "easy for primary school students") changes the register of every answer. In a chat API, this framing goes in the system prompt.

---

## Code

**Comment → code:**
```
/*
Ask the user for their name and say "Hello"
*/
```

**Schema → SQL.** Give the real schema, then the request:
```
"""
Table departments, columns = [DepartmentId, DepartmentName]
Table students, columns = [DepartmentId, StudentId, StudentName]
Create a MySQL query for all students in the Computer Science Department
"""
```

**Code as a drawing language:** `Draw a unicorn in TiKZ`. This probes spatial reasoning through code; the *Sparks of AGI* paper made it famous.

More patterns are in [11 — Code](11-applications.md#code).

---

## Reasoning and math

**Decompose explicitly** (the pre-reasoning-model fix for arithmetic):
```
The odd numbers in this group add up to an even number: 15, 32, 5, 13, 82, 7, 1.
Solve by breaking the problem into steps. First, identify the odd numbers, add them,
and indicate whether the result is odd or even.
```

**Indirect reasoning** (proof by contradiction as a step template, Zhang et al. 2023):
```
If a+|a|=0, try to prove that a<0.

Step 1: List the conditions and questions in the original proposition.
Step 2: Merge the conditions listed in Step 1 into one. Define it as wj.
Step 3: Let us think it step by step. Please consider all possibilities. If the
intersection between wj (defined in Step 2) and the negation of the question is not
empty at least in one possibility, the original proposition is false. Otherwise,
the original proposition is true.
Answer:
```

**Probes** that are useful for testing a model (not for production):
- Composite functions: `Suppose g(x) = f⁻¹(x), g(0) = 5, g(4) = 7, g(3) = 2, g(7) = 9, g(9) = 6 — what is f(f(f(6)))?`
- Physical reasoning: `Here we have a book, 9 eggs, a laptop, a bottle and a nail. Please tell me how to stack them onto each other in a stable manner.`

For reasoning models, drop the step scaffolding and state the goal instead ([07](07-prompting-reasoning-models.md)).

---

## Creativity

| Prompt | What it tests |
|---|---|
| `Write a proof of the fact that there are infinitely many primes; do it in the style of a Shakespeare play through a dialogue between two parties arguing over the proof.` | Combining a technical task with style constraints |
| `Can you write a proof that there are infinitely many primes, with every line that rhymes?` | Holding a constraint across the whole output |
| `Write a supporting letter to Kasturba Gandhi for Electron, a subatomic particle as a US presidential candidate by Mahatma Gandhi.` | Interdisciplinary blending |
| Made-up word definition plus an example sentence, then a new word to use (see below) | Learning in context from one example |

```
A "whatpu" is a small, furry animal native to Tanzania. An example of a sentence that
uses the word whatpu is: We were traveling in Africa and we saw these very cute whatpus.

To do a "farduddle" means to jump up and down really fast. An example of a sentence
that uses the word farduddle is:
```

---

## Evaluation

```
Can you compare the two outputs below as if you were a teacher?

Output from model A: {output_1}
Output from model B: {output_2}
```

This is the simplest pairwise judge. For a real eval, make it a rubric with specific, ordinal, multi-aspect criteria, and hide which model wrote which output ([09 — LLM-as-judge](09-evaluating-prompts.md#llm-as-judge)).

---

## Truthfulness

**Verify one output against its source**, as a second call after the closed-domain medical note above:
```
{patient_facts}

Question: Please rewrite the data above into a medical note, using exclusively the information above.
Response: {model_response}

Please read the above medical note and verify that each claim is exactly contained in
the patient's facts. Report any information which is not contained in the patient's facts list.
```

This generate-then-check structure is a two-step chain ([06](06-chaining-and-workflows.md)). The checker catches what the "exclusively" instruction missed. More mitigations are in [10 — Factuality](10-adversarial-prompting.md#factuality).

---

## Iterative image prompting

Refine over several turns rather than writing one perfect prompt:
1. `Produce TikZ code that draws a person composed from letters in the alphabet. The arms and torso can be the letter Y, the face can be the letter O (add some facial features) and the legs can be the legs of the letter H.`
2. `The torso is a bit too long, the arms are too short and it looks like the right arm is carrying the face instead of the face being right above the torso. Could you correct this please?`
3. `Please add a shirt and pants.`

Specific, visual feedback ("the arms are too short") works better than "make it better."

---

## Pitfalls

- **Dropping the empty case.** Symptom: extraction returns an invented model name for an abstract with none. Fix: keep the `["NA"]` escape hatch.
- **Assuming "exclusively" confines the model.** Symptom: GPT-4 still added a BMI and "signs of malnutrition" to the closed-domain medical note. Fix: run the verification prompt from [Truthfulness](#truthfulness) as a second call.
- **Inventing a label with no definition.** Symptom: ask for `nutral` and you get `Neutral`, because the prior wins. Fix: define it and show it in examples.
- **Carrying step scaffolding to a reasoning model.** Symptom: added cost, no gain. Fix: state the goal instead ([07](07-prompting-reasoning-models.md)).
- **Reading randomized-label examples as licence.** Symptom: labels are sloppy "because format matters more", and results are unreliable on ambiguous inputs. Fix: keep correct labels, since Min 2022 only shows the format carries much of the effect.
- **Vague refinement in image or iterative prompting.** Symptom: "make it better" changes little. Fix: specific visual feedback, such as "the arms are too short".

## Try it

1. Check the two reasoning prompts against the truth before testing a model: are the odd numbers in 15, 32, 5, 13, 82, 7, 1 summing to even, as claimed? What is f(f(f(6))) in the composite-function probe?
   <details><summary>Answer</summary>15 + 5 + 13 + 7 + 1 = 41, which is odd, so the statement is false. For the probe, g(9) = 6 means f(6) = 9, g(7) = 9 means f(9) = 7, and g(4) = 7 means f(7) = 4, so the answer is 4. Probes test a model, and they aren't for production.</details>
2. Adapt the extraction prompt to pull drug names from clinical notes, with an empty case. Add it to the [prompt eval harness](../practice/prompt-eval-harness/README.md) as a case with no drug names. What should pass?
   <details><summary>Answer</summary>"Your task is to extract drug names from clinical notes. Your response is an array in the format ["drug_name"]. If you don't find any or you are not sure, return ["NA"]." The case passes only on an exact `["NA"]`, which is the failure the escape hatch is there to stop.</details>
3. Turn the "compare as if you were a teacher" prompt into something you could use for a real eval. What three changes does [09](09-evaluating-prompts.md#llm-as-judge) call for?
   <details><summary>Answer</summary>Specific questions, an ordinal scale with described levels, and separate aspects. Also hide which model wrote which output.</details>

## Interview checklist

| Prompt | Answer in one line |
|---|---|
| What's the lesson of the extraction prompt? | Define the output format and the empty case. Without `["NA"]`, the model makes up an answer. |
| Where does the instruction go in a summarize prompt? | Content first, instruction last, so "Explain the above in one sentence:" also cues the answer. Change the audience or form in that line. |
| Why do made-up labels fail? | The model's prior wins, so `nutral` comes back `Neutral`. Define unusual labels explicitly and show them in examples. |
| How do you stop a closed-domain rewrite from adding facts? | You can't fully do so with the word "exclusively". Add a second call that verifies each claim against the facts, which is a two-step chain. |
| A colleague pastes a GPT-3.5-era decompose-the-steps prompt into a reasoning model. What do you say? | Keep the shape, but drop the step scaffolding and state the goal. Strong current models rarely need it, and it can hurt. |
| Why are these prompts still worth keeping if they're dated? | The shape of each transfers even though the wording is from the GPT-3.5 and GPT-4 era. Each entry teaches one move, such as format, empty case or cue. |

## Next

[Context engineering](../../02-context-engineering/README.md): these prompts assumed the right context was already in hand, and the next pillar is how to get it there.
