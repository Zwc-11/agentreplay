from app.adapters.playwright.generator import generate_test
from app.core.graph.model import Command, Edge, Graph, Node


def _graph():
    g = Graph("g", "s")
    g.nodes = [Node("s0", "page-state", "Login", 0), Node("s1", "page-state", "Dash", 1)]
    g.edges = [
        Edge("e0", "s0", "s1", "human-path", command=Command("goto", url="https://x.local")),
        Edge("e1", "s0", "s1", "human-path", command=Command("fill", role="textbox", name="Email", value="a@b.c")),
        Edge("e2", "s0", "s1", "human-path", command=Command("click", role="button", text="Sign in")),
        Edge("e3", "s0", "s1", "human-path", command=Command("assertVisible", text="Dashboard")),
    ]
    return g


def test_generated_test_is_runnable_playwright():
    out = generate_test(_graph(), "login")
    assert 'import { test, expect } from "@playwright/test";' in out
    assert 'await page.goto("https://x.local");' in out
    assert 'getByRole("textbox", { name: "Email" }).fill("a@b.c")' in out
    assert 'getByRole("button", { name: "Sign in" }).click()' in out
    assert 'await expect(page.getByText("Dashboard")).toBeVisible();' in out
