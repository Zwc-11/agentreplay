import sys

from app.scripts import demo


def test_demo_script_runs_calendar_workflow(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["demo", "calendar-demo"])

    demo.main()

    out = capsys.readouterr().out
    assert "Workflow: calendar-demo" in out
    assert "create a calendar event" in out
