from dataclasses import dataclass
from typing import Optional


class Node:
    pass


@dataclass
class Program(Node):
    statements: list


@dataclass
class Require(Node):
    module: str


@dataclass
class Function(Node):
    return_type: str
    name: str
    parameters: list
    body: list


@dataclass
class Parameter(Node):
    type: str
    name: str


@dataclass
class VariableDeclaration(Node):
    type: Optional[str]
    name: str
    value: Node


@dataclass
class Assignment(Node):
    name: str
    value: Node


@dataclass
class Return(Node):
    value: Optional[Node]


@dataclass
class While(Node):
    condition: Node
    body: list


@dataclass
class If(Node):
    condition: Node
    body: list
    elif_blocks: list
    else_body: Optional[list]


@dataclass
class Elif(Node):
    condition: Node
    body: list


@dataclass
class Call:
    function: object
    arguments: list

@dataclass
class Identifier(Node):
    name: str


@dataclass
class Literal(Node):
    value: object
    type: str

@dataclass
class ArrayLiteral(Node):
    elements: list

@dataclass
class IndexExpression(Node):
    array: Node
    index: Node

@dataclass
class CppBlock(Node):
    code: str

@dataclass
class QualifiedName(Node):
    parts: list[str]

@dataclass
class BinaryExpression(Node):
    left: Node
    operator: str
    right: Node
