#!/usr/bin/env python3
"""Rewrite modern homm3data syntax for the Python 3.4/3.8 legacy builds."""

import argparse
import ast
from pathlib import Path


class LegacyTransformer(ast.NodeTransformer):
    """Lower the syntax used by homm3data 0.1.13 to Python 3.4 syntax."""

    def __init__(self):
        self.match_number = 0

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.returns = None
        for argument in list(node.args.args) + list(node.args.kwonlyargs):
            argument.annotation = None
        if node.args.vararg:
            node.args.vararg.annotation = None
        if node.args.kwarg:
            node.args.kwarg.annotation = None
        return node

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_AnnAssign(self, node):
        value = self.visit(node.value) if node.value is not None else ast.Constant(None)
        return ast.copy_location(ast.Assign(targets=[node.target], value=value), node)

    def visit_JoinedStr(self, node):
        parts = []
        arguments = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value).replace("{", "{{").replace("}", "}}"))
            elif isinstance(value, ast.FormattedValue):
                if value.conversion != -1 or value.format_spec is not None:
                    raise ValueError("formatted f-string conversions are not supported")
                parts.append("{{{}}}".format(len(arguments)))
                arguments.append(self.visit(value.value))
            else:
                raise ValueError("unknown f-string component")
        return ast.copy_location(
            ast.Call(
                func=ast.Attribute(value=ast.Constant("".join(parts)), attr="format", ctx=ast.Load()),
                args=arguments,
                keywords=[],
            ),
            node,
        )

    def _pattern_test(self, subject, pattern):
        if isinstance(pattern, ast.MatchValue):
            return ast.Compare(left=subject, ops=[ast.Eq()], comparators=[self.visit(pattern.value)])
        if isinstance(pattern, ast.MatchSingleton):
            return ast.Compare(left=subject, ops=[ast.Is()], comparators=[ast.Constant(pattern.value)])
        if isinstance(pattern, ast.MatchOr):
            return ast.BoolOp(
                op=ast.Or(),
                values=[self._pattern_test(subject, item) for item in pattern.patterns],
            )
        if isinstance(pattern, ast.MatchAs) and pattern.pattern is None and pattern.name is None:
            return None
        raise ValueError("unsupported match pattern: {}".format(type(pattern).__name__))

    def visit_Match(self, node):
        self.match_number += 1
        variable = "__homm3data_match_{}".format(self.match_number)
        store = ast.copy_location(
            ast.Assign(
                targets=[ast.Name(id=variable, ctx=ast.Store())],
                value=self.visit(node.subject),
            ),
            node,
        )
        first_if = None
        previous_if = None
        default_body = []
        for case in node.cases:
            test = self._pattern_test(ast.Name(id=variable, ctx=ast.Load()), case.pattern)
            body = [self.visit(statement) for statement in case.body]
            if test is None:
                default_body = body
                continue
            if case.guard is not None:
                test = ast.BoolOp(op=ast.And(), values=[test, self.visit(case.guard)])
            current = ast.If(test=test, body=body, orelse=[])
            if first_if is None:
                first_if = current
            else:
                previous_if.orelse = [current]
            previous_if = current
        if previous_if is not None:
            previous_if.orelse = default_body
        return [store, first_if] if first_if is not None else [store] + default_body


def backport_file(path):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    transformed = LegacyTransformer().visit(tree)
    ast.fix_missing_locations(transformed)
    output = ast.unparse(transformed) + "\n"
    ast.parse(output, filename=str(path), feature_version=(3, 4))
    path.write_text(output, encoding="utf-8")
    return output != source


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("site_packages", type=Path)
    args = parser.parse_args()
    package = args.site_packages / "homm3data"
    files = list(package.rglob("*.py"))
    if not files:
        parser.error("homm3data package not found below {}".format(args.site_packages))
    changed = [path for path in files if backport_file(path)]
    print("Backported {} homm3data file(s) for legacy Python".format(len(changed)))


if __name__ == "__main__":
    main()
