from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path

import typer


def run_init(backend: str, path: str, force: bool) -> None:
    cwd = Path.cwd()
    ctx_dir = cwd / ".contextseek"
    store_dir = cwd / path

    if ctx_dir.exists() and not force:
        typer.echo(
            f".contextseek/ already exists. Use --force to overwrite.",
            err=True,
        )
        raise typer.Exit(1)

    ctx_dir.mkdir(parents=True, exist_ok=True)
    store_dir.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Created {ctx_dir}")

    _write_env_template(cwd / ".env", backend, path, force)
    _register_mcp(cwd / ".agentseek" / "mcp.json", force)

    typer.echo("contextseek initialized.")


def _write_env_template(env_path: Path, backend: str, path: str, force: bool) -> None:
    base_block = textwrap.dedent(f"""\
        # ---------------------------------------------------------------------------
        # ContextSeek (agentseek[context])
        # ---------------------------------------------------------------------------
        # AGENTSEEK_CTX_STORAGE_BACKEND={backend}
        # AGENTSEEK_CTX_STORAGE_PATH={path}
        # AGENTSEEK_CTX_EMBEDDING_PROVIDER=openai
        # AGENTSEEK_CTX_EMBEDDING_MODEL=text-embedding-3-small
        # AGENTSEEK_CTX_EMBEDDING_DIMS=1536
        # AGENTSEEK_CTX_LLM_PROVIDER=openai
        # AGENTSEEK_CTX_LLM_MODEL=gpt-4o-mini
        # AGENTSEEK_CTX_EVOLUTION_ENABLED=true
        # AGENTSEEK_CTX_RETRIEVAL_DEFAULT_K=5
    """)

    ob_block = textwrap.dedent("""\
        # AGENTSEEK_CTX_OB_HOST=127.0.0.1
        # AGENTSEEK_CTX_OB_PORT=2881
        # AGENTSEEK_CTX_OB_USER=root@test
        # AGENTSEEK_CTX_OB_PASSWORD=
        # AGENTSEEK_CTX_OB_DB_NAME=contextseek
    """)

    block = base_block + (ob_block if backend == "oceanbase" else "")

    if env_path.exists():
        existing = env_path.read_text()
        if "AGENTSEEK_CTX_" in existing and not force:
            typer.echo(f"{env_path} already contains AGENTSEEK_CTX_* entries, skipping.")
            return
        env_path.write_text(existing.rstrip() + "\n\n" + block)
    else:
        env_path.write_text(block)

    typer.echo(f"Updated {env_path}")


def _register_mcp(mcp_path: Path, force: bool) -> None:
    entry = {
        "command": "contextseek-mcp-stdio",
        "env": {
            "STORAGE_BACKEND": os.environ.get("AGENTSEEK_CTX_STORAGE_BACKEND", "memory"),
            "OB_HOST": os.environ.get("AGENTSEEK_CTX_OB_HOST", "127.0.0.1"),
        },
    }

    mcp_path.parent.mkdir(parents=True, exist_ok=True)

    if mcp_path.exists():
        try:
            config = json.loads(mcp_path.read_text())
        except json.JSONDecodeError:
            config = {}
        servers = config.setdefault("mcpServers", {})
        if "contextseek" in servers and not force:
            typer.echo(f"{mcp_path} already has 'contextseek' entry, skipping.")
            return
        servers["contextseek"] = entry
    else:
        config = {"mcpServers": {"contextseek": entry}}

    mcp_path.write_text(json.dumps(config, indent=2) + "\n")
    typer.echo(f"Registered contextseek in {mcp_path}")
