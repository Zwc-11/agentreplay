import json
import os

from app.core.workflow.compiler import compile_graph

HERE = os.path.dirname(__file__)
SEED = os.path.abspath(os.path.join(HERE, "..", "..", "..", "examples", "demo-shop", "recordings", "checkout.json"))


def _events():
    with open(SEED) as f:
        return json.load(f)["events"]


def test_compiles_seed_into_states_and_actions():
    g = compile_graph(_events(), "checkout-demo", graph_id="g")
    # 17 state/assertion nodes + 4 network nodes
    assert len(g.nodes) == 21
    assert len(g.human_commands()) == 16


def test_first_state_is_login_and_last_is_assertion():
    g = compile_graph(_events(), "checkout-demo")
    states = g.state_nodes()
    assert states[0].label == "Login"
    assert states[-1].kind == "assertion"


def test_input_bursts_coalesced_and_value_captured():
    g = compile_graph(_events(), "checkout-demo")
    fills = [c for c in g.human_commands() if c.kind == "fill"]
    assert any(c.value == "demo@shop.test" for c in fills)


def test_network_events_become_dependency_edges():
    g = compile_graph(_events(), "checkout-demo")
    assert any(e.kind == "network-dependency" for e in g.edges)
    assert any(n.kind == "network" for n in g.nodes)
