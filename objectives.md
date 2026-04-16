# Learning Objectives

## North Star Goal
Build a production-grade multi-agent Bitcoin research system that 
demonstrates genuine AI architecture skills — not just prompt usage.

## Core Principle
Favor deterministic structural solutions over probabilistic prompt-based 
ones. If code can handle it, code handles it.

## What I Am Learning To Do

### Agentic Architecture (Priority 1)
- Design hub-and-spoke multi-agent systems from scratch
- Decompose complex tasks into specialized independent subagents
- Execute subagents in parallel and aggregate results
- Build escalation logic using deterministic threshold conditions
- Propagate errors structurally across agents — never silently
- Isolate context per subagent so each gets only what it needs
- Design coordinator-subagent communication patterns cleanly

### Structured Output & Prompt Engineering (Priority 2)
- Use tool_use with JSON schemas instead of asking Claude to "return JSON"
- Write JSON schemas that enforce field types, required properties, 
  and valid value ranges
- Build validation retry loops that pass specific error feedback 
  back to the model
- Distinguish between structural errors (schema) and semantic errors 
  (business logic) and handle each appropriately
- Use few-shot examples to show Claude exactly what correct output 
  looks like

### Tool & API Design (Priority 3)
- Write tool descriptions precisely enough that Claude routes correctly 
  without ambiguity
- Design clean tool boundaries — one tool, one responsibility
- Handle tool failures gracefully with structured error responses
- Connect real external APIs as tools — CoinGecko, CryptoPanic, Binance

### Context Management (Priority 4)
- Prevent context bloat by summarizing before passing between agents
- Track information provenance through the pipeline
- Design clean handoff patterns between subagents and coordinator
- Understand when to fork context vs share it

### Python (Ongoing)
- Learn by building — not by studying in isolation
- Understand every line of code I write or Claude generates
- Be able to explain any function, variable, or API call if asked
- Build comfort with APIs, data structures, functions, and error handling

## What Good Looks Like
At the end of this project I should be able to:
- Explain every architectural decision and why it was made
- Defend the choice of tool_use over prompt-based JSON
- Walk through the coordinator-subagent flow without referencing notes
- Identify anti-patterns in someone else's agent architecture
- Build a second multi-agent system in a different domain from scratch

## Anti-Patterns To Avoid
- Accepting Claude's output without understanding it
- Using prompts to enforce what code should handle
- Building without knowing why — cargo-culting architecture
- Moving to the next component before the current one is understood
- Treating this as a certification study project rather than a 
  real build

## Progress Markers
[ ] Can explain hub-and-spoke architecture without notes
[ ] Built one working subagent with validated JSON output
[ ] Built a retry loop that handles validation failure
[ ] Wired two subagents to a coordinator
[ ] Implemented escalation logic with deterministic threshold
[ ] All four subagents working independently
[ ] Full pipeline running end to end
[ ] Can identify at least 5 architectural anti-patterns by name
[ ] Could rebuild this in a different domain from scratch