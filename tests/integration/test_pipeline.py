"""Integration: event stream -> compiled graph -> agent run -> metrics."""
import pytest


@pytest.mark.skip(reason="wire up once API + worker are running in CI")
def test_record_compile_run_evaluate():
    # POST a batch of events -> assert graph compiles -> start a random run ->
    # assert evaluation_metrics has a divergence_step.
    ...
