from __future__ import annotations


def run_serve(host: str, port: int, with_mcp: bool, reload: bool) -> None:
    try:
        import uvicorn
    except ModuleNotFoundError as exc:
        msg = "uvicorn is required for `agentseek ctx serve`. Install it with: uv pip install uvicorn"
        raise SystemExit(msg) from exc

    try:
        from contextseek.http.server import create_app  # noqa: F401
    except ModuleNotFoundError as exc:
        msg = "contextseek HTTP server not available. Make sure contextseek[http] is installed."
        raise SystemExit(msg) from exc

    if with_mcp:
        import threading

        try:
            from contextseek.mcp.server import create_sse_app
        except ModuleNotFoundError as exc:
            msg = "contextseek MCP server not available. Make sure contextseek[mcp] is installed."
            raise SystemExit(msg) from exc

        mcp_port = port + 1
        mcp_app = create_sse_app()

        def _run_mcp() -> None:
            uvicorn.run(mcp_app, host=host, port=mcp_port, log_level="info")

        thread = threading.Thread(target=_run_mcp, daemon=True)
        thread.start()
        print(f"MCP SSE server started at http://{host}:{mcp_port}")

    uvicorn.run(
        "contextseek.http.server:create_app",
        factory=True,
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )
