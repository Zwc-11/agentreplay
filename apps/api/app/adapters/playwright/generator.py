"""Compile a workflow graph into a runnable Playwright test."""
from __future__ import annotations

from app.core.graph.model import Command, Graph


def _locator(c: Command) -> str:
    name = c.name or c.text
    if c.role and name:
        return f'page.getByRole("{c.role}", {{ name: "{name}" }})'
    if c.text:
        return f'page.getByText("{c.text}")'
    return f'page.locator("{c.selector}")'


def command_to_line(c: Command) -> str:
    if c.kind == "goto":
        return f'  await page.goto("{c.url}");'
    if c.kind == "fill":
        return f'  await {_locator(c)}.fill("{c.value}");'
    if c.kind == "click":
        return f'  await {_locator(c)}.click();'
    if c.kind == "assertVisible":
        return f'  await expect({_locator(c)}).toBeVisible();'
    return f"  // unsupported: {c.kind}"


def generate_test(graph: Graph, test_name: str = "recorded workflow") -> str:
    lines = [command_to_line(c) for c in graph.human_commands()]
    body = "\n".join(lines) if lines else "  // no actions recorded"
    return (
        'import { test, expect } from "@playwright/test";\n\n'
        f'test("{test_name}", async ({{ page }}) => {{\n'
        f"{body}\n"
        "});\n"
    )
