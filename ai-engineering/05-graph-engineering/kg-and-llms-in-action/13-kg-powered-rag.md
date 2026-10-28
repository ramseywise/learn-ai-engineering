---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Ch 13: Knowledge graph–powered retrieval-augmented generation"
confidence: high
cleaned: 2026-07-29
---

# Ch 13 — Knowledge Graph–Powered Retrieval-Augmented Generation

## AI Agents

**AI agents** are autonomous entities that perform complex tasks by interacting with their
environment, exhibiting autonomy, adaptability, and decision-making — unlike traditional
software following predetermined instructions. A trivial question like "What is the capital
of France?" doesn't justify the cost of a large model; agents earn their keep on tasks
requiring at least one of:

- **Advanced multistep reasoning** — deduction tasks (math puzzles) or adaptive plans that
  adjust based on intermediate outputs.
- **Understanding of deep relational patterns among concepts** — e.g., identifying
  influencers in a social network, or pinpointing bottlenecks in a supply chain.
- **Access to the latest, often external and nonpublic data, not seen during training** —
  the **knowledge cutoff** problem: models are too large to retrain often enough to answer
  questions like "What is tomorrow's forecast?" or handle sensitive internal data with
  multiple access-right personas.

A multiagent system (e.g., Researcher, multiple Writers, Reviewer for a content pipeline)
is like a role-playing game: specialized agents (players) communicate to achieve a goal.

## Chatting with the LLM (Baseline Agent)

The simplest agent is a chatbot with only two ingredients: a pretrained LLM and memory
(the running list of question/answer turns) for conversational continuity.

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

_ = load_dotenv()

class Agent:
    def __init__(self, model: str = "gpt-4o-mini", system: str = None):
        self.model = model
        self.system = system
        self.messages = list()  # instance variable as memory: holds full message history
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

        if self.system is None or len(self.system) == 0:
            self.system = "You are an AI assistant providing straightforward, concise answers."
        self.messages.append({"role": "system", "content": self.system})

    def __call__(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})  # question appended to memory
        answer = self.execute()
        self.messages.append({"role": "assistant", "content": answer})  # answer appended before return
        return answer

    def execute(self) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=self.messages)
        return completion.choices[0].message.content
```

Asked "Who are the top influencers of cyclotron funding?" the out-of-the-box model gives a
correct but **generic** answer (NIH, DOE, NSF, private foundations). A follow-up
"And in the context of the 1930s, related to the Rockefeller Foundation?" surfaces two
names familiar from the book's earlier KG (chapters 5–6): Ernest O. Lawrence and Vannevar
Bush. Out-of-the-box models cannot give specific answers unless grounded in the data the
expected answer is based on.

## Challenges in the Production Environment

- **Hallucinations ("making stuff up")** — LLMs predict the most likely next token, which
  makes them susceptible to plausible-sounding but fabricated facts, especially outside
  their training data. The model still performs the task it was trained for, generating
  coherent, convincing, but partially or completely inaccurate output.
- **Freshness (knowledge cutoff)** — retraining happens only once or twice a year, so LLMs
  can't reflect recent developments.
- **Transparency** — a coherent answer arrives with no insight into how it was generated:
  information sources, reliability, reasoning process, confidence level.
- **Data privacy** — training on personal/sensitive data risks leakage; organizations also
  need differentiated access privileges across user groups.
- **Cost** — training, deploying, and maintaining top models is financially and
  environmentally expensive (high energy consumption, large carbon footprint), though
  smaller specialized LLMs are reducing this.
- **Ethical concerns and biases** — models trained on prejudiced or harmful content can
  reproduce or amplify stereotypes, misinformation, and discriminatory viewpoints.

The fix: move beyond "question in, response out" by equipping the agent with **tools** to
retrieve external, up-to-date information — weather APIs, news, or a knowledge graph.

## Chatting with the AI About Private Data

**Use case**: the Rockefeller Archive Center KG (built in chapters 5–6) tracks
grant-awarding at the Rockefeller Foundation in the 1930s — grant amounts, research topics,
universities, researchers, and behind-the-scenes conversations between Foundation
representatives and applicants (who talked with whom about what). This influence network,
built from proprietary data never published in its entirety, can accurately answer
questions like "Who were the influencers of cyclotron research funding?"

Chapters 5–6 delivered this via graph visualization and dashboards requiring Cypher
fluency. The goal now: an AI interface that delivers the same value without requiring users
to write Cypher, read charts, or navigate graph structures — via an LLM-driven agent with
context-retrieval tools, a process called **retrieval-augmented generation (RAG)**.

### Retrieval-Augmented Generation

**RAG** is a technique developed to address pretrained-model limitations (hallucination,
freshness, transparency, data privacy) by combining the LLM's knowledge and language
understanding with additional context relevant to the question, retrieved from an external
data source — structured database or unstructured dataset (text, images).

A RAG agent = LLM + a prompt guiding its steps + one or more **tools** (functions that
retrieve question-relevant external information). The model generates the answer from the
combination of the user's question and the retrieved context.

> RAG is a grounding technique: instead of letting the model go wild (hallucinations), we
> limit its scope for answer generation to the provided context, thus significantly
> reducing the chance that it will make things up.

**NOTE** (verbatim): "We can never fully get around the fact that these models are
probabilistic. They're trained to predict the most probable next token in a sequence, so
even if we use a technique like RAG, they can still go astray. This is important to keep in
mind when designing intelligent systems: instead of replacing humans, the systems should
augment them. We believe that keeping humans in the loop through a feedback validation or
supervision mechanism is essential for any product we build."

### Vector-Search-Based RAG

In early RAG, context came almost exclusively from a database of textual documents.
Documents are chunked into smaller portions (e.g., paragraphs) and mapped into fixed-length
vectors called **embeddings**, which capture semantics. Embeddings are stored and indexed
in a vector database. At query time, the question is embedded with the same model and the
most similar chunks are retrieved via cosine similarity.

```python
import os
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

_ = load_dotenv()

if __name__ == "__main__":
    vector_index = Neo4jVector.from_existing_graph(  # creates embeddings + vector index
        embedding=OpenAIEmbeddings(),
        url=os.environ['NEO4J_URL'],
        username=os.environ['NEO4J_USER'],
        password=os.environ['NEO4J_PWD'],
        database=os.environ['NEO4J_DB'],
        index_name='embeddings',
        node_label="Page",
        text_node_properties=['text'],
        embedding_node_property='embedding'
    )

    q = "What is known about cyclotron research?"
    resp = vector_index.similarity_search_with_score(q, k=2)  # top-2 semantic matches
    for r in resp:
        print(f"------\nScore: {r[1]}")
        print(r[0].page_content)
```

This uses LangChain's `Neo4jVector` to embed `Page` node text, store vectors back on the
Neo4j nodes, and retrieve the top-k most similar chunks for a question. Example output for
"What is known about cyclotron research?" returns a highly relevant 1939 diary excerpt
(score 0.918) about cyclotron reproduction costs, and a second-ranked document (score
0.916) that merely resembles a sales pitch for a competing generator — illustrating that
high similarity doesn't guarantee true relevance.

### Vector-Based RAG Limitations

- **Limited reasoning due to context fragmentation** — treating retrieved chunks
  independently misses multihop relationships across documents and entities. Chunking
  strategy itself is exposed: if needed information spans a chunk boundary, both pieces
  must be retrieved, in the right order, and ranked high — unlikely with simple chunking.
- **Scalability** — computationally expensive at scale, often forcing approximate
  (less-accurate) search algorithms.
- **Embedding limitations** — compressing a document's semantics into one dense vector
  oversimplifies, losing fine-grained/domain-specific nuance; sparsity in the embedding
  model's training data (underrepresented terms) further degrades retrieval accuracy;
  static precomputed vectors don't adapt to new or evolving nomenclature.
- **Noise in retrieval** — vector search can return loosely related or irrelevant
  documents, causing **distraction**: too much noise in longer contexts confuses the model
  and degrades output quality. Aim for context with the highest density of relevant
  information possible.
- **Misses in retrieval** — the flip side of noise: failure to include the most relevant
  documents. If not all facts are provided, no model quality can compensate. Aggregate
  questions ("What are the key research topics in this dataset?") are especially prone to
  misleading answers because similarity search optimizes for semantic closeness, not
  comprehensiveness.

**Worked example**: "How is Lauritsen related to cyclotron research?" Intuitively the top
match should mention Lauritsen by name — but embeddings encode overall meaning, not
entity presence guarantees.

| Document (excerpt) | Cosine similarity | Mentions "Lauritsen" | Mentions "cyclotron" |
|---|---|---|---|
| Karl Lark-Horovitz / Van de Graaff machine at Purdue | 0.906 | True | True |
| Irving Langmuir / Dorothy Wrinch funding discussion | 0.903 | False | True |
| Dorothy M. Wrinch (continued) / X-ray structure problem | 0.902 | False | True |

Only one of the top three documents mentions "Lauritsen" at all — the other two share
nearly the same similarity score while being irrelevant to the actual question.

### Graph RAG

The graph-based approach to RAG is commonly called **Graph RAG**. Beyond mitigating
vector-RAG's shortcomings, a KG acts as a central knowledge repository integrating raw
text, document metadata, and high-confidence structured sources (tables, CSVs, ontologies),
unlocking a wider range of use cases. Because KGs represent knowledge in a
human-accessible format, they're easy to keep current, and domain experts can validate or
add knowledge directly — improving output quality and increasing user confidence.

The Rockefeller Archive Center KG is an **LLM-augmented KG**: built via prompt engineering
on top of ChatGPT, which extracted entities/relations and completed identified information
using the model's internal knowledge. The result combines:

- **Text-attributed graph** — nodes and relationships carry textual (and other) attributes.
- **Text-paired graph** — nodes, relationships, and (sub)graphs are traceable back to the
  documents they originate from.

This combined design (entities/relations subgraph + document metadata subgraph, linked)
enables a Graph RAG system that exploits several data/knowledge-modeling aspects:

- **Metadata** — publication date, type, source, author, etc. are available as KG
  properties/relationships and can drive context retrieval — e.g., communities of
  documents represented by a summary or by the most recent document (like the latest
  version of a regulation).
- **KG retriever** — condensed, accurate, up-to-date nodes and typed relationships an LLM
  can use directly. A model can take the question plus KG schema and generate a Cypher
  query, or a KG retriever tool can take the entities the user asked about and return a
  connecting subgraph (e.g., via all shortest paths), leaving it to the final LLM to decide
  what's relevant.
- **KG-enhanced document retriever** — if the KG is text-paired, use it as a more accurate
  document retriever than vector search: e.g., retrieve only documents mentioning **all**
  entities asked about, eliminating a vector-search failure mode; or retrieve only
  documents mentioning a specific relationship, avoiding the distraction phenomenon.
- **Combined retrieval** — questions spanning multiple data sources can be split: one part
  retrieves from the KG, another uses that result to search a separate document store,
  merging contexts before the final answer. Example: "What are this year's transactions of
  the head of criminal group X?" — extract "Head of X"'s actual name from a
  law-enforcement KG, then search a financial-documents database with that name.

## Building a KG-Powered Graph RAG System

The example Graph RAG agent has three tools: the **KG retriever**, the **KG-enhanced
document retriever**, and a **semantic retriever** (vector search) as a fallback when the
other tools don't return valuable context.

### KG-Enhanced Document Retriever Tool

Implemented as a parametrized tool for finding documents discussing a specific relation
between two entities — answering questions like "What did person X say about person Y?"

```python
from pydantic import BaseModel, Field
from langchain_community.graphs import Neo4jGraph

RE_SELECTOR_QUERY = """MATCH (p:Page)-[:MENTIONS_ENTITY]->(m1:Ent...
WHERE e1.name = "{e1}" ...
...
RETURN DISTINCT p.id AS id, p.text AS text
"""  # precanned document selection query

graph = Neo4jGraph(
    url=os.environ['NEO4J_URL'],
    username=os.environ['NEO4J_USER'],
    password=os.environ['NEO4J_PWD'],
    database=os.environ['NEO4J_DB']
)

class REDiarySelectorInput(BaseModel):  # input schema (function args) for the tool
    entity_source: str = Field(description="Source entity of the relationship as mentioned in the question.")
    entity_source_class: str = Field(description=
        "Class of the source entity of the relationship. "
        "Available option is only one, 'Person'.")
    entity_target: str = Field(description="Target entity of the relationship as mentioned in the question.")
    entity_target_class: str = Field(description=
        "Class of the target entity of the relationship. "
        "Available options are Person, Organization, Occupation and Title")
    relationship: str = Field(description=
        "Relationship class between source and target entity. "
        "Available options: TALKED_ABOUT, TALKED_WITH, WORKS_WITH, WORKS_HAS_TITLE")

def kg_doc_selector(entity_source: str, entity_source_class: str,
                     entity_target: str, entity_target_class: str,
                     relationship: str) -> List[AnyStr]:  # KG-enhanced document retriever
    query = RE_SELECTOR_QUERY.format(e1=entity_source,
        e1_class=entity_source_class,
        e2=entity_target, e2_class=entity_target_class,
        rel_class=relationship)
    print(f"kg_doc_selector's query:\n{query}\n")
    try:
        res = graph.query(query)
        print(f"kg_doc_selector found {len(res)} matching documents")
    except Exception as e:
        print(f"Cypher execution exception: {e}")
        return []
    return [x['text'] for x in res[:3]]
```

The tool takes the two entities mentioned in the question, their classes (e.g., `Person`),
and the relationship type — provided by the agent based on the user's question — and
completes a precanned Cypher query executed against Neo4j.

**NOTE** (verbatim): "We could also design a more generic tool in which the document
retriever Cypher query is generated automatically based on the question. However, doing so
would introduce another possible point of failure when the Cypher queries are complex.
That's why numerous Graph RAG systems in production contain a variety of KG-related tools,
many of which are based on precanned Cypher queries for types of questions that are
frequently repeated."

### Reasoning Agents (ReAct)

LangChain provides precanned agents; since there are multiple tools with no clear
execution order, the system uses a **ReAct (Reason and Act)** agent, which integrates
reasoning and acting in an iterative feedback loop: plan the next tool to execute, run it,
observe the outcome, and act again with another tool if unsatisfactory — ending the loop
once it has sufficient context.

```python
from langchain.tools import StructuredTool
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from tools import REDiarySelectorTool, kg_doc_selector, REDiarySelectorInput
from definitions import KG_SCHEMA

tools = [  # collects all tool definitions
    StructuredTool.from_function(
        func=kg_doc_selector,
        name="KG-based-document-selector",
        args_schema=REDiarySelectorInput,
        description=f"Use it for document (diary entries) retrieval when the question asks "
                    f"for detailed information regarding interaction between two entities "
                    f"... Full KG schema:\n{KG_SCHEMA}"
    ),
    <KG_RETRIEVER>,   # structured tool for questions not requiring original texts
    <VECTOR_SEARCH>   # vector search-based tool (backup)
]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = hub.pull("hwchase17/structured-chat-agent")

agent = create_structured_chat_agent(llm, tools, prompt)  # binds model, prompt, tools
agent_executor = AgentExecutor(agent=agent, tools=tools, max_iterations=...,
                                return_intermediate_steps=True, verbose=True)

question = "What did August Krogh say about Lawrence Irving?"
response = agent_executor.invoke({"input": question})
```

The structured ReAct agent supports multiple input parameters per tool. Tool names and
descriptions guide which tool the model selects for which situation — writing these well
significantly improves stability and predictability. Don't hesitate to overwrite default
LangChain prompts if the system doesn't behave consistently; test repeatedly, even with the
same setup and question, since this process reveals improvement opportunities. This
example is an illustration only — not a production-ready system. Possible improvements:
document re-ranking after vector search, a Cypher self-correction loop for the KG
retriever, or additional tools for other typical user questions.

### Example: Chatting with the KG

Question: "What did her fellow researchers say about Dorothy M. Wrinch?" The agent's
internal steps (Thought → Action → Observation, repeated):

1. **Thought** — should look for interactions/discussions involving her; the KG might list
   people who talked about her, then the KG-based-document-selector can get details.
2. **Action** — Tool: KnowledgeGraph-reader ("Who talked about Dorothy M. Wrinch?").
3. **Observation** — returns three names: Eric Ponder, Pascu, Irving Langmuir.
4. **Thought** — need to use KG-based-document-selector, starting with Eric Ponder.
5. **Action** — Tool: KG-based-document-selector (repeated per name).
6. **Answer** — "Eric Ponder, Pascu, and Irving Langmuir are the researchers who talked
   about Dorothy M. Wrinch. Eric Ponder's remarks were about the context of her work and
   her situation during the war... Pascu discussed Wrinch's scientific hypotheses,
   particularly in relation to protein structures..."

The agent correctly determines the best course of action on its own — first retrieve the
list of people from the KG, then use the specialized document retriever for details — in a
total of four Thought/Action/Observation steps. The final answer is factual and clearly
grounded in the private documents.

Two more examples:

| Question | Graph RAG answer |
|---|---|
| "What did August Krogh say about Lawrence Irving?" | "August Krogh spoke with enthusiasm about Scholander's work on the physiology of respiration of deep diving animals in Norway and expressed the importance of getting Scholander and Lawrence Irving together. Krogh noted that Irving had done excellent work and could provide Scholander with facilities in the United States that were not available in Norway. They explored the possibility of working at Boothbay Harbor, Maine, and potentially with porpoises at aquatic zoos in Florida." |
| "Are there any shared research topics between Harvard University and Johns Hopkins University?" | "The shared research topics between Harvard University and Johns Hopkins University are astronomy and climatology." |

The first question could go directly to the KG-enhanced document retriever since two
specific people are named — an out-of-the-box LLM would either claim no information exists
or hallucinate.

The second is an **aggregate question spanning multiple documents**: some diary entries
discuss Harvard research, others Johns Hopkins, but none directly compares them. A pure
vector-search approach would require feeding a large document set as context and hoping it
contains the full answer. The KG retriever instead generates a correct (if slightly clumsy)
Cypher query directly, producing a straightforward, accurate answer. KGs excel at
connecting the dots across multiple documents, and as a side benefit reduce distraction and
hallucination risk while making predictions faster and cheaper (less context data needed).

Further reliability improvements mentioned: **self-correction loops** (have the model
double-check and correct its own generated Cypher query in a follow-up step), and
**document re-ranking** after initial context selection to improve relevance and limit
context size.

## Takeaways

- **AI agents** = LLM (brain) + guiding prompt + tools; they earn their cost on multistep
  reasoning, relational-pattern analysis, or fresh/private-data access — not trivial Q&A.
- **RAG** grounds LLMs by retrieving question-relevant external context (structured or
  unstructured) before generation, directly addressing hallucination, freshness,
  transparency, and data-privacy limitations — but the model remains probabilistic, so
  human-in-the-loop validation stays essential.
- **Vector-based RAG** treats chunks independently, which causes context fragmentation,
  scalability limits, embedding oversimplification, retrieval noise (distraction), and
  retrieval misses — especially for aggregate, multihop questions.
- **Graph RAG** integrates KGs with LLMs to add structured, relational, multihop reasoning
  and transparent, human-validatable context; the most effective KGs combine
  **text-attributed** and **text-paired** graph design to unify curated structured
  knowledge with traceable source documents.
- A practical Graph RAG agent composes multiple tools — KG retriever, KG-enhanced document
  retriever, vector-search fallback — under a **ReAct** loop, with well-written tool
  descriptions and precanned Cypher queries (to avoid the failure risk of freeform
  Cypher generation) driving reliable tool selection.
