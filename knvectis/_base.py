# knvectis/_base.py
from ._states import PruneType, PruneFrom, NotifyMode
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Protocol, Callable
import abc, hashlib
import math

__all__ = [
    "KObject",
    "KVector",
    "KRetentionPolicy",
    "KObjectFactory",
    "KVectorizer",
    "KMatcher",
    "KVectorStore",
    "KVectorIndex"
]

@dataclass
class KObject(abc.ABC):
    id: str
    parent: Optional["KObject"] = field(default=None, repr=False)
    metadata: Dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def allowed_children(self) -> tuple[type, ...]:
        """Override in subclasses to define which child types are allowed."""
        return ()

    def __repr__(self):
        return f"{self.kind}(id={self.id})"
    def __eq__(self, other):
        if not isinstance(other, KObject):
            return NotImplemented
        return self.hash == other.hash
    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented
        return not eq
    def __lt__(self, other):
        if not isinstance(other, KObject):
            return NotImplemented
        return len(self.path) < len(other.path)
    def __le__(self, other):
        return self < other or self == other
    def __gt__(self, other):
        return len(self.path) > len(other.path)
    def __ge__(self, other):
        return self > other or self == other
    def __add__(self, other):
        if not isinstance(other, KObject):
            return NotImplemented

        if self.allowed_children and not isinstance(other, self.allowed_children):
            raise TypeError(
                f"{type(self).__name__} cannot have child of type {type(other).__name__}"
            )

        children = self.metadata.setdefault("children", [])
        if other not in children:
            other.parent = self
            children.append(other)

        return other


    def __sub__(self, other):
        if other.parent is self:
            other.parent = None
            self.metadata.get("children", []).remove(other)
        return other
    def __mul__(self, n: int):
        if not isinstance(n, int):
            return NotImplemented
        return [self.clone() for _ in range(n)]
    def __truediv__(self, parts: int):
        if parts <= 0:
            raise ValueError("parts must be > 0")
        return self.partition(parts)
    def __enter__(self):
        self.on_load()
        return self
    def __exit__(self, exc_type, exc, tb):
        self.on_unload()
    def __iter__(self):
        return iter(self.metadata.get("children", []))
    
    @property
    def kind(self) -> str:
        return self.__class__.__name__

    @property
    def path(self) -> List["KObject"]:
        node, p = self, []
        while node:
            p.append(node)
            node = node.parent
        return list(reversed(p))

    @property
    def root(self) -> "KObject":
        path = self.path
        return path[0] if path else self

    def on_load(self): 
        pass

    def on_unload(self): 
        pass

    @property
    @abc.abstractmethod
    def hash(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def shash(self) -> str:
        ...

class KVector:
    def __init__(self, values: List[float]):
        self.values = values

    def __repr__(self):
        return f"KVector({self.values})"

    def __len__(self):
        return len(self.values)

    def dot(self, other: "KVector") -> float:
        return sum(a * b for a, b in zip(self.values, other.values))

    def norm(self) -> float:
        return math.sqrt(self.dot(self))

    def cosine(self, other: "KVector") -> float:
        return self.dot(other) / (self.norm() * other.norm())

    def __add__(self, other: "KVector"):
        return KVector([a + b for a, b in zip(self.values, other.values)])

    def __mul__(self, scalar: float):
        return KVector([v * scalar for v in self.values])

@dataclass
class KRetentionPolicy:
    max_size: int
    prune_from: PruneFrom
    prune_type: PruneType
    notify: NotifyMode = NotifyMode.SUPPRESS
    callback: Optional[Callable[[List[KObject]], None]] = None

    retained: List[KObject] = field(default_factory=list, init=False)

    def apply(self, container: KObject):
        children = container.metadata.get("children", [])
        overflow = len(children) - self.max_size

        if overflow <= 0:
            return

        if self.prune_from == PruneFrom.FORWARD:
            victims = children[-overflow:]
            survivors = children[:-overflow]
        else:
            victims = children[:overflow]
            survivors = children[overflow:]

        if self.prune_type == PruneType.DISCARD:
            self.retained.extend(victims)

        container.metadata["children"] = survivors

        self._notify(victims)

    def _notify(self, victims: List[KObject]):
        if self.notify == NotifyMode.RAISE:
            raise ValueError(
                f"Retention policy: removed {len(victims)} objects"
            )
        elif self.notify == NotifyMode.CALL and self.callback:
            self.callback(victims)

class KObjectFactory(Protocol):
    def create(self, data: Any, **metadata) -> KObject: ...


class KVectorizer(Protocol):
    def vectorize(self, obj: KObject) -> List[float]: ...

class KMatcher(Protocol):
    def match(self, query: KObject, candidates: List[KObject], top_k=10) -> List[KObject]: ...



class KVectorStore(Protocol):
    def add(self, obj_id: str, vector: list[float]): ...
    def get(self, obj_id: str) -> list[float] | None: ...
    def remove(self, obj_id: str): ...

class KVectorIndex(Protocol):
    def build(self, store: KVectorStore): ...
    def query(self, vector, top_k=10) -> list[str]: ...
