---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 2: Intelligent systems: A hybrid approach"
confidence: high
cleaned: 2026-07-29
---

# Ch 2 — Intelligent Systems: A Hybrid Approach

## What Is Intelligence?

**Intelligence** is the ability to acquire and apply knowledge: to learn from experience,
solve problems, and interact with the environment. To design an intelligent system, this
natural process must be decomposed into explicit tasks and components.

An intelligent agent decomposes into two components that accomplish the most relevant
activities:

- **Knowledge representation** — the "language" AI systems use to structure, encode, and
  communicate domain information. AI systems need it to reason or predict, and to
  interpret the results they produce. The choice of representation significantly affects
  the system's capabilities and limitations.
- **Reasoning** — the cognitive process of analyzing information, applying rules, and
  drawing conclusions from evidence or premises. Types include deductive and inductive
  reasoning, each suited to different problem-solving and decision-making purposes. KGs
  and LLMs, combined, are increasingly adept at mimicking and enhancing this skill.

A generic intelligent system architecture (fig. 2.1) shows multiple instances of both
component types coexisting: reasoning engines can run in sequence or parallel, and the
same knowledge representation can serve multiple reasoning engines or act as a
communication channel among models. The output of one process can feed another, creating
a **feedback loop** for knowledge refinement — e.g., reinforcement learning from human
feedback (RLHF) aligns an agent with user preferences via a reward mechanism.

There is often a trade-off between how **expressive** a knowledge representation is and
how **efficiently** it can be processed. Effective representation depends on domain and
task; representation and reasoning are interconnected and influence each other.

**Core argument of the chapter**: KGs serve as fundamental data structures for
efficiently representing knowledge, deriving fresh insights, and laying groundwork for
precise reasoning. Combined with LLMs, they improve how data sources are converted into
knowledge and how tasks are interpreted and answered.

A basic intelligent system should:

- Gather and effectively represent knowledge
- Autonomously reason using that knowledge
- Answer questions and support informed decisions

## Designing an Intelligent System

### Definition

> **DEFINITION** — Following Geoff Hulten: **Intelligent systems** connect users to AI
> and ML to achieve meaningful objectives. An intelligent system is one in which
> intelligence evolves and improves over time, particularly by watching how users
> interact with the system.

This definition centers the user. The primary objective is to support users in
accomplishing complex tasks — **not to replace them**, but to enhance their
decision-making. Example: an autonomous medical diagnosis system assists physicians
rather than replacing their expertise, contrasting with systems like self-driving cars
where the goal is to function independently of the user.

An intelligent system must learn from user interactions and explicit feedback, and
utilize contextual information, continuously developing and maintaining an evolving
knowledge base — driven both by data sources and by ongoing user interaction.

The system "perceives" the world by accessing many different data sources and formats
(unstructured data, vector-based data, relational sources, emails/chats, domain experts,
environment). As a result of internal processing, it can:

- Provide results to end users
- Communicate with other agents
- Act in the environment and make autonomous decisions

### Categories of Intelligent Systems

Two main categories, distinguished by whether the system supports users or acts on their
behalf:

| Type | Role | Key features |
|---|---|---|
| **Intelligent autonomous system** | Performs tasks independently, replacing the user in decision-making and execution | **Full automation** (operates without/minimal human input); **real-time decision-making** (must analyze and decide live); **adaptability** (adapts to changing environments and unexpected situations) |
| **Intelligent advisory system (IAS)** | Provides information and recommendations | **Decision support** (insights/suggestions, doesn't execute); **context awareness** (tailors advice using user preferences/scenario); **user interaction** (easy exploration, questions, detailed explanations) |

In both cases the system supports or helps the end user — it is not meant to replace
them; even autonomous systems inform the user once a task completes.

The book **focuses primarily on IASs**, since their features align with the strengths of
KGs: enhanced decision support, deep context awareness, and interactive user experience.
IASs let practitioners fully exploit KG capabilities as more powerful decision-support
tools.

Example domains for IASs:

- **Law enforcement** — predictive policing systems analyze crime data to identify
  potential hotspots or forecast where crimes are likely to occur.
- **Financial services** — IASs analyze transaction patterns, flagging suspicious
  activities that could indicate fraud.
- **Biomedical scenarios** — systems provide a list of potential diagnoses and recommend
  treatment options based on available data.

In all cases, the systems offer valuable insights, but **humans make the final
decisions** about what actions to take.

### Characteristics of an Intelligent System

Four key characteristics that should drive design and implementation:

- **A meaningful objective** — the system should exist for a specific, achievable purpose
  meaningful to end users; this must drive the entire development process.
- **The intelligent experience** — outputs must be presented in ways that achieve desired
  outcomes: interfaces that adapt based on predictions, maximize value when intelligence
  is correct, and minimize costs when mistakes occur. The interface must also facilitate
  implicit and explicit user feedback.
- **Knowledge creation and update** — intelligent behavior requires building,
  maintaining, and reasoning with knowledge continuously. Combining LLMs and KGs enables
  proper handling of evolving knowledge and user feedback.
- **Orchestration** — multiple algorithms/tools work together, with one's output becoming
  another's input; this includes managing how the system acquires knowledge from
  sources, controls risk, and maintains quality across its lifecycle.

Architectural decisions that follow from this design process:

- **Focus on autonomous advisor systems** — the system should suggest actions rather than
  accomplish them on behalf of the user.
- **Use an established knowledge base** — research papers, existing ontologies, and
  structured data sources rather than generic knowledge; the system shouldn't provide
  generic answers but should use domain-specific understanding refined by experts.
- **Learn from experience** — the system should extend its knowledge base using feedback
  from the results of suggested actions.

The two key processes of an intelligent system, elaborated in the rest of the chapter:

- **Knowledge acquisition** — collecting information from data sources, the environment,
  or domain experts.
- **Reasoning** — converting acquired knowledge into actionable expertise.

## Knowledge Acquisition and Representation

Knowledge acquisition lets an IAS "learn" from data available in its deployment domain,
from user feedback, and from the environment. It converts raw data into structured
knowledge representations tailored to the system's requirements, used during reasoning.
The result is stored in one or more **knowledge bases**. How knowledge is acquired,
represented, and stored depends on the underlying reasoning mechanism — this is where KGs
and LLMs diverge significantly.

### Knowledge Acquisition for KGs

For KGs, knowledge acquisition typically transforms raw, structured, or semistructured
data into a graph-based format, where entities become nodes and relationships become
edges. The structure and semantics of the domain — defined by **ontologies or schemas** —
are essential in guiding this transformation.

- The process often involves a **domain expert** to help understand data semantics and
  intrinsic relationships among entities.
- Converting heterogeneous sources into a unified, explicit schema demands meticulous
  work to ensure the resulting KG accurately reflects the domain.
- This preparation pays off in **flexibility**.
- Domain experts can manually create/formalize the knowledge base, validate it (KGs are
  human-understandable), and the KG can source embeddings, deductive reasoning, and more.
- Some ML-based reasoning engines require the KG data to be converted into predictive
  models (e.g., NLP and similarity computations).

### Knowledge Acquisition for LLMs

In contrast, LLMs acquire knowledge by ingesting vast amounts of unstructured text data,
encoded into dense, high-dimensional vector spaces during training.

- Unlike KGs, LLMs do not require extensive data preparation, and training is mostly
  **unsupervised** — the main effort is selecting and cleaning data sources.
- Domain experts can help with supervised training, but at the acquisition stage they can
  only validate the model's output or support custom fine-tuning.
- Information is encoded as statistical patterns rather than explicit, schema-defined
  relationships.
- This implicit approach lets LLMs grasp subtle contextual meanings and complex
  linguistic relationships, but makes the knowledge **opaque and difficult to inspect or
  modify**.
- Data sources are mostly unstructured or interpreted as text (unstructured data,
  emails/chats, environment).

### KG vs. LLM: Key Differences

| Dimension | Knowledge Graphs | LLMs |
|---|---|---|
| **Access** | Explicit representation via nodes, relationships, and properties — directly interpretable by both humans and machines | Implicit representation via billions of parameters in continuous vector spaces — opaque and inaccessible to humans |
| **Updates** | Add, remove, or modify nodes and relationships | Far more complex — requires retraining or fine-tuning the model |
| **Capabilities** | Depend heavily on how developers design access patterns and domain schemas | Inherently adept at understanding and generating human language |

Although each method has clear advantages and limitations, they are **complementary**. A
**hybrid approach** overcomes the limitations of both and empowers each to solve a wider
range of tasks. This new paradigm embraces a broader spectrum of computational tasks and
knowledge representations — from structured data models to numerical parameters — so
reasoning is no longer confined to formal inference but also includes probabilistic,
contextual, pattern-based computation that LLMs excel at. AI systems can reason with
explicit, structured knowledge (as in traditional expert systems) and, simultaneously,
with unstructured, ambiguous, contextual knowledge derived from language and experience.

## Reasoning

In an IAS, the reasoning engine delivers insights and suggestions from user input (a
request containing desired goals and further context).

Open questions that reasoning must address:

- **How do we deal with uncertainty?** Not all information is true, accurate, or
  unequivocal — reasoning accuracy depends on the certainty of initial statements.
- **How can we infer some of the knowledge we need?** Under some circumstances we can
  derive new information from available data.
- **How can we abstract from what we have seen to a broader understanding of the
  domain?**

### Deductive and Inductive Reasoning

- **Deductive reasoning** is a basic form of reasoning: it begins with a general
  statement or hypothesis and examines the possibilities to reach a specific, logical
  conclusion. Example: "All men are mortal. Alessandro is a man. Therefore, Alessandro is
  mortal." The hypothesis must be correct — if the premises are true, the conclusion is
  logical and true.
- **Inductive reasoning** makes broad generalizations from specific observations. It
  starts with samples of reality and draws conclusions. Example: "The coin I pulled from
  the bag is a penny. The second and third coins from the bag are pennies. Therefore, all
  the coins in the bag are pennies." Even if all premises are true, inductive reasoning
  can lead to false conclusions — e.g., "Harold is a grandfather. Harold is bald.
  Therefore, all grandfathers are bald" does not follow logically.

A naive spam filter illustrates the gap: a program that memorizes emails labeled spam and
matches new emails against that store is not a proper learning process — it can't
generalize to label unseen emails. Generalizing beyond stored examples into a broader
model is **inductive reasoning** (or **inductive inference**).

### LLM Reasoning Limitations — A Worked Example

Because tools like ChatGPT mimic human conversation, people often overestimate their
reasoning capabilities. The authors tested Claude.ai (3.5 Sonnet at the time) with a
simplified river-crossing puzzle (farmer, sheep, boat — omitting the wolf and lettuce
found in the classic version).

> **NOTE** — the authors expect the same experiment to produce different results by the
> time the book is printed, given the pace of LLM improvement.

Because the simplified problem closely resembles a well-known puzzle in the training
data, the expectation was that the model would reproduce the *full* problem's solution
pattern rather than "understand" the simplified constraints — and that's what happened.
Claude.ai produced a 3-trip solution (farmer takes sheep across, returns alone, crosses
again) that includes unnecessary back-and-forth — reasoning that doesn't make sense for a
problem solvable in fewer steps once the wolf/lettuce constraint is removed. The
**proposed solution is "probabilistically" the closest** match to training data, not a
genuine reasoning result.

This is consistent with broader findings: Wu et al. tested 11 tasks (coding, drawing,
logic, spatial, chess, arithmetic) with **counterfactual variants** that deviate from
default/well-known task forms. Performance degraded substantially and consistently
compared to default conditions. Current LLMs possess some abstract task-solving skills
but often rely on **narrow, non-transferable procedures**.

**Complementary framing**: use KGs for tasks needing precise, rule-based reasoning and
explicit knowledge representation; use LLMs for tasks involving pattern recognition,
context understanding, and handling ambiguous or incomplete information, including
reasoning about graph structures and their derived metrics. Neither approach inherently
has common-sense reasoning comparable to humans, and both can fail to make intuitive
leaps or grasp implicit context obvious to a person — motivating a hybrid IAS.

## Reasoning Engines

A **reasoning engine** is generic — it can implement a single reasoning strategy
(deductive, inductive, or otherwise) or a combination. It reads from the knowledge base
and **writes back to it**: actions/suggestions influence the environment, which produces
new observations, which the engine processes to build new knowledge — an iterative
feedback loop that improves the system's response to environmental change over time.

### Limitations of a Pure Deductive Reasoning Engine

Example: an automated medical diagnosis IAS proposing a sequence of actions (tests,
treatments, queries). The sequence is computed from a knowledge base containing costs and
outcomes of potential actions, probabilistic relationships between diseases/symptoms, and
patient preferences. In an idealized scenario where the knowledge base encodes all
necessary data, a deductive reasoner can logically infer optimal actions and can
outperform other reasoning methods.

**Major limitation**: deductive reasoning requires a highly complete and accurate
knowledge base, which is rarely available in practice. The knowledge base is built by
transforming data sources (EHRs, research literature, medical best practices, protein
gene/disease datasets) into a format directly usable by the deductive engine — a
one-directional transformation; the deductive reasoner doesn't store results back into
the knowledge base.

### Using Inductive Reasoning and ML

Inductive reasoning, powered by ML, addresses deductive reasoning's limitations in two
key ways:

- By learning and building relevant ontologies and relationships, ML expands the
  knowledge base, enabling it to handle a broader range of cases.
- By providing inference under uncertainty, ML lets the system generalize from
  incomplete data and make predictions even when not all information is available.

An inductive reasoner works in two steps:

1. Transform raw data into a structured format — often via NLP powered by LLMs,
   converting unstructured text into structured data that extends the KG (e.g.,
   extracting entities/relationships from research papers, reports, other text).
2. Use this knowledge to make predictions or generate actions through inductive
   reasoning, which **abstracts patterns** from available observations — e.g.,
   recommending treatments for diseases not included in the original knowledge base.

In traditional ML approaches, this often requires manually selecting features from the
knowledge base to train prediction models — tedious and sometimes infeasible in complex
domains.

### The Role of LLMs in the Reasoning Engine

Unlike purely deductive systems requiring complete knowledge bases and explicit rules,
LLMs use probabilistic reasoning to generate contextually relevant suggestions even when
critical information is missing. Example: a patient presenting nonspecific symptoms
(stress vs. serious neurological conditions) with incomplete records — deductive
reasoning struggles here, but an LLM can draw on patterns learned from vast medical
literature to evaluate multiple diagnostic possibilities simultaneously, weighing
likelihoods and recommending a **prioritized diagnostic approach** rather than a single
definitive answer.

This probabilistic capability lets LLMs **bridge knowledge gaps** that would halt a
purely deductive process. Integrated with KG-based reasoning engines, an LLM acts as a
reasoning layer that interprets ambiguous inputs and provides nuanced recommendations
accounting for uncertainty — enabling hybrid IASs to function effectively in real-world
environments where information is often incomplete or uncertain.

## A KG Approach to IASs

Where do KGs fit in IAS development? "The short answer is, **everywhere**." Academia and
industry use KGs extensively as structured human knowledge representation, alongside
graph-based reasoning and analysis algorithms.

The idea of using a graph to support decision-making is not new: Stokman and de Vries
anticipated that knowledge-based systems could construct computer programs advising
professional users with limited domain expertise, speculating: *"The structuring of
knowledge in a graph can be seen as the construction of a knowledge-based system
integrating knowledge from different sources."*

In recent years, KGs have become a standard approach to merge distributed data into a
single connected **source of truth**, and with generative AI/LLMs, KGs can mitigate
hallucinations and provide up-to-date data, among other benefits.

### Bottom-Up vs. Purpose-Driven KG Construction

Simply viewing KGs as knowledge aggregators overlooks their real goal: building
intelligent systems. A **bottom-up approach** to KG construction begins with data from
various sources, consolidates it into a single source of truth, and initiates discovery
without any clear idea of what the end user is looking for — the schema is defined only
after data is fully loaded, making it hard to change. Iterations then serve different
downstream tasks (KG exploration, semantic applications, etc.) on top of the (mostly
fixed) graph.

The authors' experience: **bottom-up approaches often lead to KG adoption failure.**
Reasons:

- Too many data sources, each with different structures and identifiers.
- Significant effort required to normalize data into a single homogeneous structure.
- Much of the content is task-specific and therefore not relevant to global/general use.

### Purpose-Driven Construction via CRISP-DM

Developing intelligent agents requires representing knowledge (as a KG) in a way that is
effective and captures the domain's intrinsic complexity, driven by **business
objectives rather than available data**. Building on the established ML methodology
**CRISP-DM**, a purpose-driven approach places the KG at the center of the process:

- **Business understanding** — everything starts here; goals drive data understanding.
- **Data understanding** — starts from existing data and selects only data relevant to
  defined goals (rather than blindly importing all sources).
- **Data preparation** — takes the relevant portion of current scope; this also drives
  the definition of the next portion of the KG.
- **Modeling** — defining the algorithms for the ML tasks; KG model creation/update.
- **Evaluation** — results are evaluated against the goals.
- **Deployment** — incorporate the graph schema/model, ingestion/post-processing
  pipelines, algorithms, and pretrained models into a product.
- **Start/restart** — a new round begins, but not from an empty KG.

This determines requirements for defining the KG's content and structure. The KG
represents a **self-sufficient, domain-specific, customizable source of truth** that
copies and transforms the data needed.

- During **acquisition**, LLMs extract relevant entities and relationships from
  unstructured data and provide generic understanding (e.g., sentiment analysis, topic
  identification).
- During **modeling**, one or more algorithms are used and tested to reach specific
  goals; results are evaluated in the next phase.
- LLMs can be involved in **reasoning on top of KGs** to understand users' questions and
  provide answers in natural language.
- Output of these phases: a set of algorithms, a set of trained/pretrained models, and a
  report describing test results and overall model quality.

In a second round, work proceeds by **difference and extension** — ensuring prior
iteration results aren't affected. A **schemaless** approach to the graph allows
extensions with new nodes and relationship types without compromising existing data or
functionality.

> **DEFINITION** — A **predictive model** is a formula for estimating an unknown value of
> interest: the *target*. It represents, in an efficient format, the result of the
> learning process on the training dataset, and is accessed to perform the actual
> prediction.

> **DEFINITION** — **Schemaless** refers to the flexibility of storing data in a database
> or generic data structure with fewer (or no) constraints on how data items are
> formatted and related to each other. Graph databases are generally considered
> schemaless because their elements (nodes and relationships) and attributes can store
> practically anything.

The book frequently uses schemas to drive the process between scenarios and use cases;
these schemas are repurposed across chapters, with different phases highlighted as
examples of how this process works in practice.

## Takeaways

- Intelligence is fundamentally about acquiring and applying knowledge; **knowledge
  representation** and **reasoning** are the core components of intelligent system
  architecture.
- Intelligent systems split into **autonomous systems** (act independently) and
  **advisory systems / IASs** (support human decision-making) — the book focuses on IASs
  because they align with KG strengths.
- **KGs** acquire knowledge via explicit, structured representation requiring domain
  expertise but offering interpretability; **LLMs** acquire knowledge via implicit
  statistical patterns that capture language understanding but lack transparency.
- **Deductive reasoning** needs a complete, accurate knowledge base (rare in practice);
  **inductive reasoning** (ML-powered) generalizes from incomplete data and expands the
  knowledge base, but can produce false conclusions even from true premises.
- LLMs bridge knowledge gaps in reasoning engines by interpreting ambiguous input and
  weighing probabilistic possibilities, making hybrid IASs more robust under incomplete
  or uncertain information — but neither KGs nor LLMs alone provide human-like
  common-sense reasoning.
- **Purpose-driven KG construction** (CRISP-DM-based, starting from business objectives)
  outperforms **bottom-up** data-first KG integration, which frequently fails due to
  source heterogeneity and irrelevant task-specific content.
