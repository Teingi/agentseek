# AgentSeek v0.0.1

We are proud to publish the first public release of **AgentSeek**.

Version `0.0.1` establishes the initial stable baseline for the AgentSeek distribution: a database-native harness with opinionated defaults, documentation, and a repeatable release pipeline for ongoing iteration.

## Release Scope

This release focuses on shipping the core foundation rather than a broad feature surface.

- First public package release of `agentseek` on PyPI
- Initial documentation set for installation, configuration, and extension points
- Stable baseline for local workspace state and project-level customization
- CI-driven release flow for reproducible package publishing and docs deployment

## What AgentSeek Provides In v0.0.1

At this stage, AgentSeek is positioned as a practical distribution layer for running Bub-compatible agent workflows with AgentSeek defaults.

- A branded `agentseek` CLI entry point with project-oriented defaults
- Environment-variable aliases in the `AGENTSEEK_*` namespace
- Local runtime state under `.agentseek` by default for easier workspace portability
- Support for project-local skills under `.agents/skills`
- MCP configuration via `.agentseek/mcp.json` (or a custom config path)

## Installation

Install from PyPI:

```bash
pip install agentseek==0.0.1
```

## Quick Verification

After installation, run the following command to verify your environment:

```bash
agentseek --help
```

If you need model responses, configure your provider credentials first (for example via `.env` or `AGENTSEEK_*` variables).

## Compatibility Notes

- Python `3.12+` is required for the documented setup path
- This `agentseek` release line is separate from the `agentseek-cli` contrib package release line
- `agentseek-cli` uses independent tags and release automation

## Documentation

To get started and go deeper:

- Getting Started (installation, local state, MCP setup)
- Configuration (environment aliases and runtime paths)
- Extensions (skills, plugins, and project customization)
- Introducing AgentSeek (background and product positioning)

## Why v0.0.1 Matters

This release marks the transition from exploratory work to a formal public baseline.  
The goal is to make runtime behavior, context handling, and extension wiring easy to adopt in real projects while keeping the kernel and distribution boundary clear.

## Known Boundaries For This Release

- The priority is stability of the base harness and distribution defaults
- Broader ecosystem integrations and deeper contrib capabilities will continue to evolve after this baseline
- Users should expect incremental improvements across docs, packaging ergonomics, and extension workflows in upcoming releases

## Feedback

If you encounter issues or have suggestions, please open an issue in the repository.  
Early feedback is especially valuable at this stage and directly informs roadmap priorities after `0.0.1`.
