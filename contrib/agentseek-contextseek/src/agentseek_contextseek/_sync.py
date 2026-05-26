from __future__ import annotations

import importlib
from pathlib import Path

import typer

_PLUG_MAP: dict[str, str] = {
    "rag": "contextseek.dataplug.rag:RagPlug",
    "powermem": "contextseek.dataplug.powermem:PowerMemPlug",
    "trace": "contextseek.dataplug.trace:TracePlug",
    "skills": "contextseek.dataplug.skills:SkillsPlug",
}


def run_sync(scope: str, sources: list[str], config_path: str, dry_run: bool) -> None:
    try:
        cs_mod = importlib.import_module("contextseek.client.contextseek")
    except ModuleNotFoundError as exc:
        msg = "contextseek is required. Install with: uv pip install contextseek"
        raise SystemExit(msg) from exc

    ctx = cs_mod.ContextSeek.from_settings()

    config_file = Path(config_path)
    plug_config: dict = {}
    if config_file.exists():
        import yaml  # type: ignore[import-untyped]
        plug_config = yaml.safe_load(config_file.read_text()) or {}

    if not sources:
        typer.echo("No --source specified. Nothing to sync.", err=True)
        raise typer.Exit(1)

    total = 0
    for source in sources:
        cls_path = _PLUG_MAP.get(source)
        if cls_path is None:
            typer.echo(f"Unknown source '{source}'. Valid options: {', '.join(_PLUG_MAP)}", err=True)
            raise typer.Exit(1)

        module_path, cls_name = cls_path.rsplit(":", 1)
        try:
            mod = importlib.import_module(module_path)
            plug_cls = getattr(mod, cls_name)
        except (ModuleNotFoundError, AttributeError) as exc:
            typer.echo(f"Could not load plug for '{source}': {exc}", err=True)
            raise typer.Exit(1) from exc

        plug = plug_cls(**plug_config.get(source, {}))

        if dry_run:
            count = plug.count(scope=scope)
            typer.echo(f"[dry-run] {source}: {count} items would be imported into {scope}")
            total += count
        else:
            imported = ctx.plug(plug, scope=scope)
            typer.echo(f"{source}: imported {imported} items into {scope}")
            total += imported

    if dry_run:
        typer.echo(f"[dry-run] total: {total} items")
    else:
        typer.echo(f"sync complete: {total} items imported into {scope}")
