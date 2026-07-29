---
origin: book
source: "Knowledge Graphs and LLMs in Action (Manning) — Appendix B: Neo4j"
confidence: high
cleaned: 2026-07-29
---

# Appendix B — Neo4j

This appendix gives the minimum needed to get started with **Neo4j** in the book: what it
is, how to install it, the **Cypher** query language, and the two plugins used throughout
the examples (APOC and GDS).

## B.1 Introduction to Neo4j

The book's examples, code, and exercises are all built on one specific graph database:
Neo4j. The authors state the theories, algorithms, and code can be adapted to any graph
database, but they chose Neo4j because:

- They know it inside and out.
- It is a **native graph database** (storage and processing designed around graph
  structures, not layered on top of another storage model — see appendix A for graph
  representations).
- It has a broad community of experts.

Per DB-Engines ranking (`https://db-engines.com/en/ranking_trend/graph+dbms`), Neo4j has
been the most popular graph DBMS for years. DB-Engines scoring blends multiple signals:
website mentions, frequency of technical questions on Stack Overflow / DBA Stack
Exchange, and number of job postings referencing the system.

### Core characteristics

Neo4j is available as a GPL3-licensed **open source Community Edition**; Neo4j Inc. also
sells a closed-source **Enterprise Edition** with backup, scaling extensions, and other
enterprise-grade features. It is implemented in Java and reachable over the network via a
transactional HTTP endpoint or the binary **Bolt protocol** (`https://boltprotocol.org/`).

Widely adopted due to:

- It implements a **labeled property graph** database.
- Native graph storage based on **index-free adjacency** (see appendix A).
- Native graph querying via **Cypher** (`www.opencypher.org`), which defines how the
  database describes, plans, optimizes, and executes queries.
- Every architecture layer — from Cypher queries down to files on disk — is optimized
  for storing and retrieving graph data.
- An easy-to-use developer workbench with a graph visualization interface.

### ACID support

Neo4j is a full-strength, industrial-grade database with transactional support — this
differentiates it from many NoSQL solutions. It provides full **ACID** support:

- **(A) Atomicity** — Multiple database operations can be wrapped in a single
  transaction and executed atomically. If one operation fails, the entire transaction is
  rolled back.
- **(C) Consistency** — When data is written, every client accessing the database is
  guaranteed to read the latest data.
- **(I) Isolation** — Operations in a single transaction are isolated from one another,
  so writes in one transaction won't affect reads in another transaction.
- **(D) Durability** — Neo4j writes data to disk, and it remains available after a
  database restart or a server crash.

This ACID guarantee eases the transition for anyone used to relational-database
guarantees, making graph data both safe and convenient to work with.

### Other architectural qualities

Beyond ACID, other factors matter when choosing a database for an architectural stack:

- **Recoverability** — the database's ability to set things right after a failure.
  Verbatim quote: "*… are susceptible to bugs in their implementation, in the hardware
  they run on, and in that hardware's power, cooling, and connectivity. Though diligent
  engineers try to minimize the possibility of failure in all of these, at some point
  it's inevitable that a database will crash. And when a failed server resumes
  operation, it must not serve corrupt data to its users, irrespective of the nature or
  timing of the crash. When recovering from an unclean shutdown, perhaps caused by a
  fault or even an overzealous operator, Neo4j checks in the most recently active
  transaction log and replays any transactions it finds against the store. It's possible
  that some of those transactions may have already been applied to the store, but
  because replaying is an idempotent action, the net result is the same: after recovery,
  the store will be consistent with all transactions successfully committed prior to the
  failure* [1]."
  Neo4j also offers an online backup procedure to recover the database when the original
  data is lost; recovery in that case goes only to the last committed transaction, but
  that beats losing all the data.
- **Availability** — increases the chance of recoverability. Verbatim quote: "*A good
  database needs to be highly available to meet the increasingly sophisticated needs of
  data-heavy applications. The database's ability to recognize and, if necessary, repair
  an instance after crashing means that data quickly becomes available again without
  human intervention. And of course, more live instances increases the overall
  availability of the database* … *to process queries.*" It's uncommon to want
  individual disconnected database instances in production; instead instances are
  clustered for high availability. Neo4j uses a **master/slave cluster** arrangement so a
  complete replica of the graph is stored on each machine. Writes replicate from the
  master to the slaves at frequent intervals; at any point the master and some slaves
  will have a fully up-to-date copy, while other slaves catch up (typically milliseconds
  behind) [1].
- **Capacity** — the amount of data storable in the database. The adoption of
  dynamically sized pointers in Neo4j 3.0 and higher allows the database to scale up to
  run any size of graph workload with an upper limit "in the quadrillions" of nodes [3].

Recommended further reading: *Graph Databases* [1] and *Neo4j: The Definitive Guide* [2].
At time of writing, the latest Neo4j version was **2025.x**, and all code/queries in the
book were tested against this version.

## B.2 Installing Neo4j

Neo4j ships in two editions: **Community** (free, GPLv3, usable indefinitely for
noncommercial purposes — `https://www.gnu.org/licenses/gpl-3.0.en.html`) and
**Enterprise** (available as a limited-time trial requiring a proper license). The book's
code works fully with the Community Edition, which is the recommended choice. Neo4j is
also available packaged as a Docker image.

### B.2.1 Installing a Neo4j server

On Linux or Mac:

1. Ensure **Java 21** (or later) is installed.
2. Open a terminal/shell.
3. Extract the archive: `tar xf <filecode>`, e.g.
   ```
   tar xf neo4j-community-2025.08.0-unix.tar.gz
   ```
4. Place the extracted files in a permanent home directory on the server — referred to
   as **NEO4J_HOME**.
5. To run Neo4j:
   - As a console application: `<NEO4J_HOME>/bin/neo4j console`
   - As a background process: `<NEO4J_HOME>/bin/neo4j start`
6. Visit `http://localhost:7474` in a web browser.
7. Connect using username `neo4j` and default password `neo4j`. You'll be prompted to
   change the password on first login.

On Windows, the procedure is similar: unzip the downloaded file and proceed as above.
After connecting, the **Neo4j browser** appears — a simple web-based application for
interacting with a Neo4j instance, submitting queries, and performing basic
configuration.

### B.2.2 Neo4j Desktop installation

**Neo4j Desktop (v2)** (`https://neo4j.com/docs/desktop/current/`) is a developer
environment that manages many local projects/database servers and can also connect to
remote Neo4j servers. It ships with a free developer's license for the Enterprise
Edition. Quick setup on macOS:

1. In Downloads, double-click the `.dmg` file to start the installer.
2. Drag the Neo4j Desktop icon into the Applications folder.
3. Locate the Neo4j icon in Applications and double-click to launch Desktop.
4. Once activated, click **Create instance** to create your first local instance. An
   "instance" is a local database management system (DBMS) capable of managing multiple
   databases.
5. Specify the instance name, the Neo4j version, and the password for the `neo4j` user
   (password must be at least 8 characters).
6. A default database named `neo4j` is created together with the `system` database.
7. Start/stop the instance using the button next to the instance name.
8. Click **Connect** to use the instance via the Neo4j browser (**Query**) or the
   exploration interface (**Explore**). This lands you in the same browser interface
   as the server install path.

Alternatively, **Neo4j Aura** (`https://neo4j.com/product/auradb/`) is a cloud-hosted
version with a free tier for experimentation. For the book's exercises, running Neo4j
locally (or wherever the Python code runs) is recommended over Aura for a smoother
learning curve.

## B.3 Cypher

Neo4j uses **Cypher** (`https://neo4j.com/developer/cypher/`) as its query language.
Like SQL (which inspired it), Cypher lets users store and retrieve data from a graph
database — easy to learn, understand, and use, while incorporating the power of other
standard data-access languages.

Cypher is a **declarative language** for describing visual patterns in graphs using
**ASCII Art syntax**. It lets you describe a graph pattern visually and logically. Cypher
patterns are used to search the graph or to create/select/insert/update/delete data
without specifying exactly how to do it (the database plans and optimizes execution).

### The simplest query (Listing B.1)

Search for all nodes of type `Person`:

```cypher
MATCH (p:Person)
RETURN p
```

Cypher is open source. The **openCypher** project (`www.opencypher.org`) provides an
open language specification, technical compatibility kit, and a reference
implementation of the parser, planner, and runtime for Cypher. It's backed by several
database-industry companies and allows implementors/clients to freely benefit from, use,
and contribute to the language's development.

## B.4 Installing plugins

Neo4j is easy to extend. Developers can customize it in many ways: enrich Cypher with
new procedures and functions callable when querying the graph, customize security with
authentication/authorization plugins, and enable new HTTP API surfaces via server
extensions.

Two plugins are used throughout the book's examples:

- **The Awesome Procedures on Cypher library (APOC)** — a standard utility library
  containing common procedures and functions. It is the most widely used extension
  library for Neo4j, providing functionality for utilities, conversions, graph updates,
  and more. Well supported, easy to run as a separate function or inline in Cypher
  queries — lets developers reuse a standard library for common procedures and write
  only their own business logic.
- **The Graph Data Science library (GDS)** — Neo4j's analytics engine, for addressing
  complex questions about system dynamics and group behavior. Exploits the predictive
  power of relationships and network structures to answer previously intractable
  questions and increase prediction accuracy. Provides a customized, flexible data
  structure for global computations and a repository of powerful, robust algorithms to
  quickly compute results over tens of billions of nodes.

Install both before starting chapter 3, where Cypher queries begin in earnest.

### B.4.1 Installing APOC Core

Download the plugin from the GitHub release page
(`https://github.com/neo4j/apoc/releases`) matching your Neo4j version (2025.07.x,
2025.08.x, etc.). Copy it into the `plugins` directory under `NEO4J_HOME`. Then edit
`conf/neo4j.conf`, adding or adjusting:

```
dbms.security.procedures.unrestricted=apoc.*
dbms.security.procedures.allowlist=apoc.*
```

Restart Neo4j and open the browser. Verify installation:

### Checking whether APOC is correctly installed (Listing B.2)

```cypher
CALL dbms.procedures() YIELD name
WHERE name STARTS WITH "apoc"
RETURN name
```

You should see a list of APOC procedures returned.

For Neo4j Desktop: after creating the database (section B.2.2, through step 4/instance
creation), open the instance, click the three dots at upper right, select **Plugins**,
choose the plugins to install, and restart the instance.

Full details: `https://neo4j.com/labs/apoc/`.

### B.4.2 GDS installation

Similar procedure. If using the server version, download the plugin from
`https://github.com/neo4j/graph-data-science/releases`. Copy the `*-standalone.jar` file
into the `plugins` directory under `NEO4J_HOME`. Edit `conf/neo4j.conf`:

```
dbms.security.procedures.unrestricted=apoc.*,gds.*
dbms.security.procedures.allowlist=apoc.*,gds.*
```

Restart Neo4j and verify:

### Checking whether GDS is correctly installed (Listing B.3)

```cypher
RETURN gds.version()
```

You should see the version of GDS you downloaded.

For Neo4j Desktop: same plugin-install flow as APOC, but select the **Graph Data
Science** plugin.

## B.5 Cleaning

Sometimes the database needs to be cleaned up. This can be done using functions from the
APOC library.

### Deleting everything (Listing B.4)

```cypher
CALL apoc.periodic.iterate('MATCH (n) RETURN n',
    'DETACH DELETE n', {batchSize:1000})
```

### Dropping all constraints (Listing B.5)

```cypher
CALL apoc.schema.assert({}, {})
```

## Takeaways

- Neo4j is a native, labeled-property-graph database using index-free adjacency,
  queried via the declarative, ASCII-art-pattern language **Cypher**; it offers full
  ACID guarantees (atomicity, consistency, isolation, durability).
- Two install paths: a raw server (`NEO4J_HOME`, `neo4j console`/`neo4j start`, browser
  at `localhost:7474`) or **Neo4j Desktop**, a GUI that manages local instances and
  databases; **Aura** is the cloud-hosted option but local install is preferred for
  learning.
- The simplest Cypher query pattern, `MATCH (p:Person) RETURN p`, generalizes to
  select/insert/update/delete via pattern matching rather than imperative steps.
- Two plugins are required for the book's examples: **APOC** (general-purpose utility
  procedures/functions) and **GDS** (graph algorithms and analytics at scale) — both
  installed by dropping a jar into `plugins/` and allowlisting `apoc.*`/`gds.*` in
  `conf/neo4j.conf`, or via the Desktop Plugins panel.
- `CALL dbms.procedures() YIELD name WHERE name STARTS WITH "apoc" RETURN name` and
  `RETURN gds.version()` are the standard smoke tests after plugin installation.
- `apoc.periodic.iterate(...)` with `DETACH DELETE n` clears all graph data in batches;
  `apoc.schema.assert({}, {})` drops all constraints — both used for resetting a
  database between exercises.
