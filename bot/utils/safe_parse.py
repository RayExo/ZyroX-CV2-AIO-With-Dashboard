# ╔══════════════════════════════════════════════════════════════════╗
# ║  Safe parsing helpers — no eval() on untrusted data              ║
# ╚══════════════════════════════════════════════════════════════════╝

from __future__ import annotations

import ast
import json
import operator
import re
from typing import Any


def parse_role_id_list(raw: str | None) -> list[int]:
    """Parse a stored role-ID list (JSON or legacy Python repr)."""
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(raw)
        except (ValueError, SyntaxError):
            return []
    if not isinstance(parsed, list):
        return []
    return [int(x) for x in parsed if str(x).isdigit()]


def dump_role_id_list(ids: list[int]) -> str:
    return json.dumps(ids)


_MATH_ALLOWED = re.compile(r"^[\d+\-*/().\s]+$")


def _eval_math_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_math_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _eval_math_node(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        left = _eval_math_node(node.left)
        right = _eval_math_node(node.right)
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError("division by zero")
        return ops[type(node.op)](left, right)
    raise ValueError("unsupported expression")


def safe_math_eval(expression: str) -> str:
    """Evaluate basic arithmetic safely (digits, +, -, *, /, parentheses)."""
    expr = expression.strip()
    if not expr or not _MATH_ALLOWED.match(expr):
        raise ValueError("invalid characters in expression")
    tree = ast.parse(expr, mode="eval")
    return str(_eval_math_node(tree))
