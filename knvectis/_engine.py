# knvectis/_engine.py
from __future__ import annotations
from dataclasses import dataclass, field
from ._states import TraversalMode, PruneType, RelationshipType, MatchLevel, NotifyMode, PruneFrom
from ._base import KMatcher, KObject, KRetentionPolicy
from ._objects import Matrix, Layer, Net, Node, Tree, Branch, Leaf, Entity, VAR_GEN_ID, gen_id, _GEN_IDS
from typing import (
    Iterable, Iterator, Callable, Any, Optional, List, Dict, Set
)
from collections import deque

@dataclass
class KMatchContext:
    """
    Describes WHAT we are searching for.
    This class contains no logic — only intent and helpers.
    """
    node: Any
    id: Optional[str] = None
    data: Optional[Any] = None
    hash: Optional[str] = None
    shash: Optional[str] = None
    score: float = 0.0
    path: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    predicate: Optional[Callable[[KObject], bool]] = None

    def matches(self, obj: KObject) -> bool:
        """
        Very conservative default matching.
        No ranking, no scoring, no guessing.
        """
        if self.id is not None and obj.id != self.id:
            return False

        if self.hash is not None and obj.hash != self.hash:
            return False

        if self.shash is not None and obj.shash != self.shash:
            return False

        if self.data is not None:
            if not hasattr(obj, "data"):
                return False
            if obj.data != self.data:
                return False

        if self.predicate and not self.predicate(obj):
            return False

        return True
    

    def enrich(self, **kwargs):
        self.metadata.update(kwargs)
        return self

    def bump(self, value: float):
        self.score += value
        return self

class KTraverser:
    def __init__(
        self,
        *,
        children_resolver: Optional[Callable[[Any], Iterable[Any]]] = None,
        parent_resolver: Optional[Callable[[Any], Optional[Any]]] = None,
        transversal_resolver: Optional[Callable[[Any], Iterable[Any]]] = None,
    ):
        self.children_resolver = children_resolver
        self.parent_resolver = parent_resolver
        self.transversal_resolver = transversal_resolver

    def traverse(self, start: Any, mode=None):
        visited: Set[int] = set()
        queue = deque([(start, [])])

        while queue:
            node, path = queue.popleft()
            node_id = id(node)

            if node_id in visited:
                continue

            visited.add(node_id)
            yield node, path

            new_path = path + [node]

            # Forward (children)
            if self.children_resolver:
                for child in self.children_resolver(node) or []:
                    queue.append((child, new_path))

            if self.parent_resolver:
                parent = self.parent_resolver(node)
                if parent:
                    queue.append((parent, new_path))

            if self.transversal_resolver:
                for link in self.transversal_resolver(node) or []:
                    queue.append((link, new_path))

@dataclass
class KHuntResult:
    obj: KObject
    depth: int
    path: List[KObject]

    matched: bool
    signals: Dict[str, Any] = field(default_factory=dict)

class KHunter:
    def __init__(
        self,
        predicate: Callable[[Any], bool],
        *,
        scorer: Optional[Callable[[Any], float]] = None,
        on_match: Optional[Callable[[KMatchContext], None]] = None
    ):
        self.predicate = predicate
        self.scorer = scorer
        self.on_match = on_match

    def hunt(self, node: Any, path: list):
        if not self.predicate(node):
            return None

        ctx = KMatchContext(
            node=node,
            path=path
        )

        if self.scorer:
            ctx.bump(self.scorer(node))

        if self.on_match:
            self.on_match(ctx)

        return ctx
class KEngine:
    def __init__(self, traverser: KTraverser):
        self.traverser = traverser
        self.hunters: list[KHunter] = []

    def add_hunter(self, hunter: KHunter):
        self.hunters.append(hunter)

    def run(self, start: Any):
        for node, path in self.traverser.traverse(start):
            for hunter in self.hunters:
                ctx = hunter.hunt(node, path)
                if ctx:
                    yield ctx

def children_resolver(obj):
    return getattr(obj, "children", None)

def parent_resolver(obj):
    return getattr(obj, "parent", None)

def score_signal(obj):
    return {
        "depth_score": 1 / (len(obj.path) + 1)
    }

