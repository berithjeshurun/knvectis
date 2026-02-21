# knvectis/_objects.py
from ._base import KObject, KRetentionPolicy
from ._states import TraversalMode, RelationshipType, MatchLevel
from dataclasses import dataclass, field
from typing import Any, Optional, List, Generator, Callable, Dict, Set, Union, Literal
from enum import Enum, auto, Flag
import uuid, secrets, hashlib, threading
from copy import copy

sha1 = lambda x : hashlib.sha1(str(x).encode()).hexdigest()
VAR_GEN_ID : Literal['secrets', 'uuid'] = "secrets"


__all__ = [
    "sha1",
    "VAR_GEN_ID",
    "_GEN_IDS",
    "gen_id",
    "Entity",
    "Leaf",
    "Branch",
    "Tree",
    "Node",
    "Net",
    "Layer",
    "Matrix"
]


_GEN_IDS = set()
_GEN_IDS_LOCK = threading.Lock()

def gen_id() -> str:
    if VAR_GEN_ID == 'secrets':
        generated = secrets.token_urlsafe(8)
    else:
        generated = str(uuid.uuid4())[:8]

    with _GEN_IDS_LOCK:
        if generated in _GEN_IDS:
            return gen_id()
        else:
            _GEN_IDS.add(generated)
            return generated

@dataclass
class Entity:
    id: str
    key: str
    label: str
    type: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Leaf(KObject):
    id: str = field(default_factory=gen_id)
    data: Any = None
    parent: Optional[KObject] = field(default=None, repr=False)

    def __repr__(self):
        return f"Leaf(id={self.id[:6]}, data={self.data!r})"

    @property
    def hash(self) -> str:
        # Structural hash: content + position in hierarchy
        return sha1(f"{self.data}|{self.parent.id if self.parent else None}")

    @property
    def shash(self) -> str:
        # Semantic hash: stable meaning of this leaf
        return sha1(f"{self.data}")
    

    @property
    def allowed_children(self):
        return (Leaf,)


@dataclass
class Branch(KObject):
    id: str = field(default_factory=gen_id)
    data: Optional[Any] = None
    parent: Optional["KObject"] = field(default=None, repr=False)
    retention: Optional[KRetentionPolicy] = None

    def add_leaf(self, leaf_data: Any, **meta) -> Leaf:
        leaf = Leaf(data=leaf_data, metadata=meta)
        self + leaf
        return leaf

    def walk_leaves(self) -> Generator["Leaf", None, None]:
        for child in self:
            if isinstance(child, Leaf):
                yield child

    def __repr__(self):
        return f"Branch(id={self.id[:6]}, data={self.data!r})"
    
    def __add__(self, other: KObject):
        result = super().__add__(other)

        if self.retention:
            self.retention.apply(self)

        return result
    

    @property
    def hash(self) -> str:
        children_ids = [c.id for c in self]
        parent_id = self.parent.id if self.parent else None
        return sha1(f"{self.data}|{children_ids}|{parent_id}")

    @property
    def shash(self) -> str:
        return sha1(f"{self.data}|{self.id}")
    
    @property
    def leaves(self):
        return [c for c in self if isinstance(c, Leaf)]
    
    @property
    def allowed_children(self):
        return (Leaf,)
    
@dataclass
class Tree(KObject):
    id: str = field(default_factory=gen_id)
    data: Optional[Any] = None
    parent: Optional[KObject] = field(default=None, repr=False)
    retention: Optional[KRetentionPolicy] = None

    def walk_branches(self) -> Generator[Branch, None, None]:
        for child in self:
            if isinstance(child, Branch):
                yield child

    def walk_leaves(self) -> Generator[Leaf, None, None]:
        for branch in self.walk_branches():
            yield from branch.walk_leaves()

    def walk(self) -> Generator[KObject, None, None]:
        for child in self:
            yield child
            if isinstance(child, Branch):
                yield from child.walk_leaves()
    
    def add_branch(
        self,
        branch_data: Any = None,
        retention: KRetentionPolicy | Literal["inherit"] | None = None
    ) -> Branch:
        if retention == "inherit" and self.retention:
            policy = copy(self.retention)
        elif isinstance(retention, KRetentionPolicy):
            policy = retention
        else:
            policy = None

        branch = Branch(data=branch_data, retention=policy)
        self + branch
        return branch
    
    @property
    def branches(self) -> List[Branch]:
        return [c for c in self if isinstance(c, Branch)]

    def __repr__(self):
        return f"Tree(id={self.id[:6]}, data={self.data!r})"
    
    def __add__(self, other: KObject):
        result = super().__add__(other)
        if self.retention:
            self.retention.apply(self)
        return result


    @property
    def hash(self) -> str:
        children_ids = [c.id for c in self]
        parent_id = self.parent.id if self.parent else None
        return sha1(f"{self.data}|{children_ids}|{parent_id}")

    @property
    def shash(self) -> str:
        return sha1(f"{self.data}")
    
    @property
    def allowed_children(self):
        return (Branch,)


@dataclass
class Node(KObject):
    id: str = field(default_factory=gen_id)
    data: Optional[Any] = None
    parent: Optional[KObject] = field(default=None, repr=False)
    retention: Optional[KRetentionPolicy] = None

    def add_tree(
        self,
        tree_data: Any = None,
        retention: KRetentionPolicy | Literal["inherit"] | None = None
    ) -> Tree:
        if retention == "inherit" and self.retention:
            policy = copy(self.retention)
        elif isinstance(retention, KRetentionPolicy):
            policy = retention
        else:
            policy = None

        tree = Tree(data=tree_data, retention=policy)
        self + tree
        return tree

    def walk_trees(self) -> Generator[Tree, None, None]:
        for child in self:
            if isinstance(child, Tree):
                yield child

    def walk_branches(self) -> Generator[Branch, None, None]:
        for tree in self.walk_trees():
            yield from tree.walk_branches()

    def __add__(self, other: KObject):
        result = super().__add__(other)
        if self.retention:
            self.retention.apply(self)
        return result


    @property
    def trees(self) -> List[Tree]:
        return [c for c in self if isinstance(c, Tree)]

    def __repr__(self):
        return f"Node(id={self.id[:6]}, data={self.data!r})"

    @property
    def hash(self) -> str:
        children_ids = [c.id for c in self]
        parent_id = self.parent.id if self.parent else None
        return sha1(f"{self.data}|{children_ids}|{parent_id}")

    @property
    def shash(self) -> str:
        return sha1(f"{self.data}")
    
    @property
    def allowed_children(self):
        return (Tree,)

Element = Union[Node, Tree, Branch, Leaf]

@dataclass
class Net(KObject):
    id: str = field(default_factory=gen_id)
    parent: Optional[KObject] = field(default=None, repr=False)
    index: Dict[str, KObject] = field(default_factory=dict, repr=False)
    retention: Optional[KRetentionPolicy] = None

    # ---- Registration ----
    def register(self, obj: KObject):
        self.index[obj.id] = obj

    def unregister(self, obj: KObject):
        self.index.pop(obj.id, None)

    def get(self, obj_id: str) -> Optional[KObject]:
        return self.index.get(obj_id)

    def add_node(self, node_data: Any = None) -> Node:
        node = Node(data=node_data)
        self + node 
        self.register(node)
        if self.retention:
            children = self.metadata.get("children", [])
            self.retention.apply(children)
        return node

    def walk_nodes(self) -> Generator[Node, None, None]:
        for child in self:
            if isinstance(child, Node):
                yield child
                yield from child.walk_trees()

    def walk_all(self) -> Generator[KObject, None, None]:
        stack = list(self)
        while stack:
            obj = stack.pop(0)
            yield obj
            stack.extend(list(obj))

    # ---- Search ----
    def find(self, predicate: Callable[[KObject], bool]) -> Optional[KObject]:
        for obj in self.walk_all():
            if predicate(obj):
                return obj
        return None

    def __repr__(self):
        return f"Net(id={self.id[:6]}, nodes={len(self.children)})"

    @property
    def children(self):
        return self.metadata.get("children", [])

    # ---- Hashing ----
    @property
    def hash(self) -> str:
        ids = [c.id for c in self.children]
        return sha1(f"{ids}")

    @property
    def shash(self) -> str:
        return self.hash
    
    @property
    def allowed_children(self):
        return (Node,)


@dataclass
class Layer(KObject):
    name: str = ""
    id: str = field(default_factory=gen_id)
    parent: Optional[KObject] = field(default=None, repr=False)

    storage: Optional[Any] = field(default=None, repr=False)
    retention: Optional[KRetentionPolicy] = None

    def __add__(self, other: KObject):
        result = super().__add__(other)
        if self.retention:
            self.retention.apply(self)
        return result

    def add_net(self, net: Net) -> Net:
        self + net
        return net

    def create_net(self) -> Net:
        net = Net()
        self + net
        return net

    def walk_nets(self) -> Generator[Net, None, None]:
        for child in self:
            if isinstance(child, Net):
                yield child

    def on_load(self):
        if self.storage:
            self.storage.load_layer(self)

    def on_unload(self):
        if self.storage:
            self.storage.unload_layer(self)

    def __repr__(self):
        return f"Layer(name={self.name!r}, nets={len(self.children)})"

    @property
    def children(self):
        return self.metadata.get("children", [])

    @property
    def hash(self) -> str:
        net_ids = [n.id for n in self.children]
        return sha1(f"{self.name}|{net_ids}")

    @property
    def shash(self) -> str:
        return sha1(self.name)
    
    @property
    def allowed_children(self):
        return (Net,)

@dataclass
class Matrix(KObject):
    id: str = field(default_factory=gen_id)
    name: str = "Matrix"
    parent: Optional[KObject] = field(default=None, repr=False)

    retention: Optional[KRetentionPolicy] = None
    storage: Optional[Any] = None
    active: bool = field(default=False, repr=False)

    def __add__(self, other: KObject):
        result = super().__add__(other)
        if self.retention:
            self.retention.apply(self.children)
        return result

    # Add an existing layer
    def add_layer(self, layer: Layer) -> Layer:
        self + layer
        if self.active:
            layer.on_load()
        return layer

    # Create a new layer inside the matrix
    def create_layer(self, name: str = "", **kwargs) -> Layer:
        layer = Layer(name=name, **kwargs)
        self.add_layer(layer)
        return layer

    # Iterate over all layers
    def walk_layers(self) -> Generator[Layer, None, None]:
        for child in self:
            if isinstance(child, Layer):
                yield child

    @property
    def layers(self) -> list[Layer]:
        return list(self.walk_layers())

    # Lifecycle control
    def start(self):
        if self.active:
            return
        self.active = True
        for layer in self.layers:
            layer.on_load()

    def stop(self):
        if not self.active:
            return
        for layer in self.layers:
            layer.on_unload()
        self.active = False

    @property
    def children(self):
        return self.metadata.get("children", [])

    # Identity
    @property
    def hash(self) -> str:
        layer_ids = [l.id for l in self.layers]
        return sha1(f"{self.name}|{layer_ids}")

    @property
    def shash(self) -> str:
        return sha1(self.name)

    def __repr__(self):
        return f"Matrix(name={self.name!r}, layers={len(self.layers)}, active={self.active})"

    @property
    def allowed_children(self):
        return (Layer,)