from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated, NoReturn, Optional

import typer

CTX_PASSTHROUGH_COMMANDS: tuple[str, ...] = (
    "add", "retrieve", "expand", "compact", "forget", "delete",
    "overview", "tools", "metrics", "dream", "feedback",
    "upstream", "evidence-chain", "chain-confidence",
    "skill-tools", "skill-context", "skill-import", "items",
)

_PASSTHROUGH = {
    "allow_extra_args": True,
    "ignore_unknown_options": True,
    "help_option_names": [],
}

app = typer.Typer(
    name="ctx",
    help="SeekContext — semantic context layer: write, retrieve, evolve, and serve.",
    add_completion=False,
    no_args_is_help=True,
)


# ---------------------------------------------------------------------------
# Passthrough layer (18 commands)
# ---------------------------------------------------------------------------

def _run_contextseek(argv: Sequence[str]) -> None:
    """Delegate to contextseek.cli.run_cli(); raise typer.Exit with its exit code."""
    try:
        from contextseek.cli.main import run_cli
    except ModuleNotFoundError:
        _raise_missing()

    from agentseek_contextseek.config import apply_contextseek_env_aliases
    apply_contextseek_env_aliases()

    exit_code = run_cli(list(argv))
    raise typer.Exit(exit_code)


def _passthrough(command_name: str):
    def _cmd(ctx: typer.Context) -> None:
        _run_contextseek([command_name, *ctx.args])
    _cmd.__name__ = f"ctx_{command_name.replace('-', '_')}"
    _cmd.__doc__ = f"[contextseek] {command_name} — run `agentseek ctx {command_name} --help` for options."
    return _cmd


for _name in CTX_PASSTHROUGH_COMMANDS:
    app.command(_name, context_settings=_PASSTHROUGH)(_passthrough(_name))


# ---------------------------------------------------------------------------
# New commands (3)
# ---------------------------------------------------------------------------

@app.command("init")
def cmd_init(
    backend: Annotated[str, typer.Option(help="Storage backend: memory | file | oceanbase")] = "memory",
    path: Annotated[str, typer.Option(help="Root path for file/oceanbase backend")] = ".contextseek/store",
    force: Annotated[bool, typer.Option(help="Overwrite existing config")] = False,
) -> None:
    """Initialize contextseek config and directories in the current project."""
    _setup()
    from agentseek_contextseek._init import run_init
    run_init(backend=backend, path=path, force=force)


@app.command("serve")
def cmd_serve(
    host: Annotated[str, typer.Option(help="Bind host")] = "127.0.0.1",
    port: Annotated[int, typer.Option(help="HTTP port")] = 8001,
    mcp: Annotated[bool, typer.Option(help="Also start MCP SSE server")] = False,
    reload: Annotated[bool, typer.Option(help="Dev mode with auto-reload")] = False,
) -> None:
    """Start the contextseek HTTP API server (and optionally the MCP SSE server)."""
    _setup()
    from agentseek_contextseek._serve import run_serve
    run_serve(host=host, port=port, with_mcp=mcp, reload=reload)


@app.command("sync")
def cmd_sync(
    scope: Annotated[str, typer.Option(help="Target scope (tenant/project/agent)")],
    source: Annotated[Optional[list[str]], typer.Option(help="Source type: rag | powermem | trace | skills")] = None,
    config: Annotated[str, typer.Option(help="DataPlug config file path")] = ".contextseek/sync.yaml",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Print import count without writing")] = False,
) -> None:
    """Import context from external sources into a scope via DataPlugs."""
    _setup()
    from agentseek_contextseek._sync import run_sync
    run_sync(scope=scope, sources=source or [], config_path=config, dry_run=dry_run)


# ---------------------------------------------------------------------------
# Registration and helpers
# ---------------------------------------------------------------------------

def register_ctx_commands(target: typer.Typer) -> None:
    """Attach the `ctx` command group onto a root Typer app."""
    if any(g.name == app.info.name for g in target.registered_groups):
        return
    target.add_typer(app, name="ctx")


def _setup() -> None:
    """Check contextseek is installed and apply env aliases — call once per command."""
    _require_contextseek()
    from agentseek_contextseek.config import apply_contextseek_env_aliases
    apply_contextseek_env_aliases()


def _require_contextseek() -> None:
    try:
        import contextseek  # noqa: F401
    except ModuleNotFoundError:
        _raise_missing()


def _raise_missing() -> NoReturn:
    typer.echo(
        "The `agentseek ctx` commands require `contextseek` in the current environment.\n"
        "Install it with:  uv pip install contextseek\n"
        "Or via extra:     uv pip install 'agentseek[context]'",
        err=True,
    )
    raise typer.Exit(1)


__all__ = ["CTX_PASSTHROUGH_COMMANDS", "app", "register_ctx_commands"]
