# RESEARCH_NOTES.md

## Initial market note
The biggest recurring pain in code-agent workflows is not just model quality but weak observability, poor trust, and difficulty understanding what the agent actually did.

## Project thesis
A useful observability layer for code agents should make it easier to inspect:
- tool usage
- command execution
- file edits
- test outcomes
- failures and retries
- overall run summaries

## Questions to investigate
- which adjacent agent tools expose the best execution visibility?
- what trace schema is most useful for debugging?
- what output format helps users most: JSON, Markdown, HTML, or all three?

## Practical schema lesson
A useful first schema should answer debugging questions directly:
- what happened first
- where the first actionable failure appeared
- what changed in the repo
- whether tests passed after the change
- which artifact to inspect next

This suggests starting with ordered events plus compact summaries instead of a more abstract tracing model.
