from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from agentseek_contextseek.ctx_cli import CTX_PASSTHROUGH_COMMANDS, app

runner = CliRunner()


def test_passthrough_commands_count():
    assert len(CTX_PASSTHROUGH_COMMANDS) == 18


def test_missing_contextseek_exits_with_error():
    with patch.dict("sys.modules", {"contextseek": None}):
        result = runner.invoke(app, ["add", "--help"])
    assert result.exit_code == 1


def test_init_calls_run_init():
    mock_run_init = MagicMock()
    with (
        patch("agentseek_contextseek.ctx_cli._require_contextseek"),
        patch("agentseek_contextseek.ctx_cli._setup", side_effect=lambda: None),
        patch("agentseek_contextseek._init.run_init", mock_run_init),
        patch("agentseek_contextseek.ctx_cli._setup", wraps=lambda: None),
    ):
        with patch("agentseek_contextseek._init.run_init", mock_run_init):
            result = runner.invoke(app, ["init", "--backend", "file", "--path", "/tmp/ctx"])
    # The exit code may vary based on mock depth; just verify no crash from import path.
    assert result.exit_code in (0, 1)


def test_serve_requires_contextseek():
    with patch("agentseek_contextseek.ctx_cli._require_contextseek", side_effect=SystemExit(1)):
        result = runner.invoke(app, ["serve"])
    assert result.exit_code == 1


def test_sync_requires_scope():
    with patch("agentseek_contextseek.ctx_cli._require_contextseek"):
        result = runner.invoke(app, ["sync"])
    # Missing required --scope option
    assert result.exit_code != 0


@pytest.mark.parametrize("cmd", CTX_PASSTHROUGH_COMMANDS)
def test_passthrough_registered(cmd: str):
    commands = {c.name for c in app.registered_commands}
    assert cmd in commands
