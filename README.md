# knvectis

**knvectis** is a modular traversal and knowledge execution engine built around structured object hierarchies such as `Tree`, `Branch`, `Leaf`, `Node`, `Layer`, and `Matrix`.
It provides a flexible execution layer for navigating and querying hierarchical or graph-based object networks.

It is designed for:

* Structured knowledge graphs
* Tree / DAG traversal
* Hybrid semantic + structural matching
* Rule-based node hunting
* Engine-style extensible reasoning
* Bidirectional traversal
* Pluggable match logic
* Context-aware hunting
* Scoring + metadata enrichment
* Engine-style orchestration

Designed for knowledge systems, semantic architectures, and AI memory frameworks.

---

## ✨ Core Concepts

knvectis separates structure from execution:

| Layer      | Responsibility                                          |
| ---------- | ------------------------------------------------------- |
| `_objects` | Structural primitives (Tree, Node, Layer, Matrix, etc.) |
| `_states`  | Traversal modes and relationship semantics              |
| `_engine`  | Traversal, hunting, scoring, orchestration              |

---

## 🚀 Installation

```bash
git clone https://github.com/berithjeshurun/knvectis.git
cd knvectis
pip install -e .
```

---

## 🧠 Core Abstractions

knvectis models knowledge as structured layers:

* **Matrix** → Global container
* **Layer** → Logical separation
* **Net** → Network grouping
* **Tree** → Hierarchical root
* **Branch** → Intermediate structure
* **Leaf** → Terminal knowledge unit
* **Entity / Node** → Core object abstraction

Execution is handled by:

* `KTraverser`
* `KHunter`
* `KEngine`
* `KMatchContext`

---

## 🔥 Usage Demo (Tree / Branch / Leaf)

### 1️⃣ Create a Knowledge Tree

```python
from knvectis import Tree, Branch, Leaf
# Create tree
tree = Tree(id="Knowledge Root")

# Create branches
ai_branch = Branch(id="Artificial Intelligence")
math_branch = Branch(id="Mathematics")

tree.add_branch(ai_branch)
tree.add_branch(math_branch)

# Add leaves
leaf1 = Leaf(id="Neural Networks", data={"type": "deep learning"})
leaf2 = Leaf(id="Graph Theory", data={"type": "discrete math"})
leaf3 = Leaf(id="Reinforcement Learning", data={"type": "machine learning"})

ai_branch.add_leaf(leaf1)
ai_branch.add_leaf(leaf3)
math_branch.add_leaf(leaf2)
```

You now have a structured knowledge hierarchy:

```
Tree
 ├── Branch (AI)
 │     ├── Leaf (Neural Networks)
 │     └── Leaf (Reinforcement Learning)
 └── Branch (Mathematics)
       └── Leaf (Graph Theory)
```

---

### 2️⃣ Define a Hunter

We’ll search for all leaves containing `"learning"` in their name.

```python
def learning_predicate(node):
    return hasattr(node, "name") and "learning" in node.name.lower()

hunter = KHunter(predicate=learning_predicate)
```

---

### 3️⃣ Execute the Engine

```python
traverser = KTraverser(
    children_resolver=children_resolver,
    parent_resolver=parent_resolver
)

engine = KEngine(traverser)
engine.add_hunter(hunter)

for match in engine.run(tree):
    print(match.node.name)
```

### ✅ Output

```
Reinforcement Learning
```

---

## 🧪 Advanced Example — Scoring + Context

```python
def scorer(node):
    return len(node.name)

def on_match(ctx):
    ctx.enrich(category="ai-topic")

hunter = KHunter(
    predicate=lambda n: isinstance(n, Leaf),
    scorer=scorer,
    on_match=on_match
)
```

Each match now includes:

* Score
* Traversal path
* Metadata
* Matched node reference

---

## 🔍 Traversal Semantics

knvectis supports multiple traversal patterns via resolvers:

```python
KTraverser(
    children_resolver=...,
    parent_resolver=...,
    transversal_resolver=...
)
```

This enables:

* Root → Leaves (causal flow)
* Leaves → Root (dependency analysis)
* Cross-branch traversal
* Custom graph logic

---

## 🏗️ Engine Architecture

```
Tree / Branch / Leaf (Structure)
          ↓
Resolvers (Traversal abstraction)
          ↓
KTraverser (Navigation engine)
          ↓
KHunter (Matching logic)
          ↓
KEngine (Execution orchestrator)
```

The engine does not assume domain logic — it executes intent.

---

## 🧩 Example Applications

### 🔹 Knowledge Graph Systems

Hierarchical knowledge modeling with contextual querying.

### 🔹 AI Memory Architectures

Layered memory structures (Matrix → Layer → Tree → Leaf).

### 🔹 Rule-Based Reasoning

Attach multiple hunters as rule evaluators.

### 🔹 Dependency Analysis

Reverse traversal for impact tracing.

### 🔹 Hybrid Semantic Search

Combine structural traversal with vector similarity scoring.

---

## 🎯 Why knvectis?

Most graph libraries focus purely on structure.

knvectis focuses on:

* Intent-driven traversal
* Context-aware matching
* Engine composability
* Execution-oriented architecture

It is designed to serve as a reasoning substrate inside larger AI systems.

---

## 📌 Roadmap

* TraversalMode enforcement
* MatchLevel integration
* Relationship-aware traversal
* Vector similarity modules
* Performance tuning for large graphs
* Retention / pruning policies

---

## License

knvectis is licensed under the MIT.

See the LICENSE file for details.
