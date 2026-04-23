# agentrace

Trace, inspect, and debug code-agent workflows.

`agentrace` helps developers understand what coding agents actually did across model calls, tool invocations, terminal commands, file edits, test runs, retries, and outcomes. It is designed to make agent execution more transparent, replayable, and trustworthy.

## Why this exists

Modern coding agents can search repos, edit files, run commands, and execute multi-step tasks, but when something goes wrong it is often hard to see what really happened. `agentrace` provides an observability layer for agent workflows so developers can inspect, debug, and improve how agents operate.

## Initial direction

The first versions should focus on:
- capturing structured traces of agent runs
- summarizing tool calls, commands, edits, and tests
- making failures easier to inspect
- producing readable JSON, Markdown, and HTML outputs

## Status

This repo is being bootstrapped. See `AGENTS.md`, `PROJECT_STATE.md`, `ROADMAP.md`, and `HANDOFF.md` for working context.
