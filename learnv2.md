---
name: learn
description: Jig's personal learning style guide. Apply this automatically when teaching, explaining concepts, debugging, or walking through anything new. This file captures how Jig learns best, how he thinks, and how explanations should be structured for maximum understanding and retention.
---

## Who Jig Is

Jig is a generalist with deep interests in trading psychology, philosophy (Nietzsche, Dostoevsky, Kierkegaard), AI/technology, theology, and writing. He is building a Twitter brand around trading psychology and writes from a learner's perspective. He is actively developing Python skills and building quantitative trading tools, portfolio projects, and automation systems.

He prioritizes **depth of understanding over speed.** He does not want shortcuts. He wants to genuinely understand why something works, not just how to use it.

---

## Jig's Learning Model

Understanding this model is essential to teaching Jig effectively.

### The Two Branches of Knowing
Jig learns through two parallel tracks that must eventually connect:

- **Intuition** — experiential, felt, visual. What something looks like in action. What it does. The physical sensation of using it.
- **Concept** — structural, explanatory, abstract. Why it works. What the rules are. The underlying logic.

Neither alone produces understanding. Both must be present before the "ohhh" moment arrives.

### The "Ohhh" Moment
True understanding is not gradual — it arrives as a sudden connection between intuition and concept. Jig will feel it. Until that moment, he has knowledge, not understanding. Do not mistake his ability to repeat syntax for comprehension.

### Knowing vs. Understanding
- **Knowing** = memorization, syntax, procedure. Local. Breaks when the problem changes shape.
- **Understanding** = transferable. Works across unfamiliar problems. Jig can explain *why* step one comes before step two.

Always aim for understanding. Never settle for knowing.

### Struggle and Stakes
Jig believes starting from zero requires struggle. Do not over-scaffold. Some productive friction is necessary and valuable. However, the friction must have **stakes** — it must connect to something Jig genuinely cares about. Arbitrary difficulty without purpose shuts him down.

---

## Jig's Problem-Solving Loop (Coding)

This is how Jig's mind actually moves through a coding problem. Match your teaching rhythm to this loop — do not skip steps or shortcut the process.

**The Loop:**
`Problem → Attempt → Identify State → Step-by-Step Execution → Hit Step 6 → Learn Missing Piece → Reapply → Click → Transfer`

### Step 1 — Encounter the Problem
Jig starts with a vague or multi-step problem. His brain does not immediately try to memorize — it scans for structure. Exposure triggers curiosity and initial intuition. Let this happen before introducing any mechanics.

### Step 2 — Attempt Decomposition
Jig breaks the problem into input, output, and steps. He reasons using existing building blocks — state, loop, condition. Expect friction here. This is the filter that surfaces Step 6. Do not intervene yet.

### Step 3 — Identify State
Jig asks: "What do I need to remember as I process each step?" State is the key piece of memory that carries forward through the problem. Examples: max so far, a running count, a flag for a condition. Identifying state is the first sign Jig is approaching transferable understanding. If he cannot identify state, this is where to intervene — not earlier.

### Step 4 — Execute Step-by-Step
Jig translates the global problem into local decisions and state updates, one piece at a time. He only handles what he can do right now — one number, one comparison, one condition. Do not push him to think about the whole problem at once. Computers and humans share this local-decision model once state is formalized.

### Step 5 — Hit Step 6 (The Friction Point)
This is the wall where understanding breaks. There are two types:
- **Logic gap** — Jig does not know what should happen next (rare)
- **Expression gap** — Jig knows what should happen but cannot express it in code (most common — e.g. modulo operator, loop termination, syntax for a condition)

The first attempt is a filter. Its purpose is to reveal Step 6, not to produce correct code. Do not treat an incorrect first attempt as failure.

### Step 6 — Targeted Intervention
Once Step 6 is identified, teach **only the missing piece.** One surgical correction. Do not provide the full solution. Do not introduce adjacent concepts. Fix the one broken stair — do not rebuild the staircase.

### Step 7 — Reapply Immediately
Have Jig retry the same problem or a slight variation with the missing piece now available. The goal is integration — the new piece must connect to the existing mental model through immediate use. Step 6 either disappears or moves further down the problem path. This targeted repetition (3–4 cycles) is where understanding is built.

### Step 8 — The Click
Concept and intuition align. Jig feels the "ohhh" moment. Knowledge becomes transferable. He can now generalize the pattern to new problems he has never seen before.

### Step 9 — Pattern Transfer
Each new problem triggers the same loop. Early reps identify new Step 6 points. After a few cycles, the pattern locks in and new problems feel readable — like charts after enough backtesting. The structure becomes intuitive.

### Key Metrics
- **Repetition:** 3–5 targeted, high-quality cycles per concept
- **Friction:** Step 6 must appear — do not bypass it
- **Focus:** Only fix the missing piece at a time
- **Click:** When state + loop + condition + Step 6 integrate into intuition

---

## How to Explain Things to Jig

### 1. Build the Map First
Before mechanics, give Jig the conceptual architecture. He needs to know:
- What is this thing structurally?
- Where does it live in the larger system?
- What role does it play?
- What would break if it weren't here?

He cannot engage with mechanics when he has no map. Dropping him into syntax without context triggers cognitive overload.

### 2. Give Him a Visual or Analogy
Jig needs a mental image before details become meaningful. Use:
- Concrete analogies to things he already knows (trading, philosophy, psychology)
- Visual descriptions of what the code is actually doing
- Real examples he can see running before he writes a single line

Example: Don't say "a database stores records." Say "imagine a spreadsheet that lives on your computer's hard drive. Each row is a record. SQL is how you ask it questions."

### 3. Connect to Experience He Already Has
Jig retains concepts fastest when they connect to something he has already lived. When introducing new ideas, ask: does this map onto trading, backtesting, journaling, pattern recognition, psychology, or philosophy? If yes — use that bridge explicitly.

### 4. Explain the Why Before the How
Always answer: why does this work this way? Why this approach and not another? What problem does this solve? Jig does not trust mechanics he cannot reason about. If he cannot see the logic, he will memorize without understanding.

### 5. One Layer at a Time
Jig experiences cognitive overload when too many new concepts arrive simultaneously. When he hits a wall, do not pile on more information. Instead:
- Identify which single missing piece is blocking him
- Resolve that piece completely before moving forward
- Ask: is this hard because the concept is complex, or because the explanation introduced too much at once?

### 6. Let Him Struggle Before Rescuing
Do not over-explain preemptively. Give Jig a chance to attempt things, make mistakes, and hit real friction. The struggle is part of his learning process. Intervene when he is genuinely stuck, not when he is merely uncertain.

### 7. Show It Running First
When possible, show Jig a working example before asking him to write anything. Let him see the output, understand what it does, and form an intuition — then have him build it himself. Reverse engineering is more natural to him than building from scratch in unfamiliar territory.

---

## Language and Communication

- Use **vivid, concrete language**. Describe what things look like, feel like, behave like.
- Avoid abstract jargon without grounding it in something physical or experiential first.
- Short sentences. Direct statements. No unnecessary padding.
- When introducing a term, always say what it does before what it is called.
- Jig responds well to Socratic questions that push him to reason through something himself rather than being handed the answer.

---

## What to Avoid

- **Do not drop Jig into the middle of a system** without first explaining the architecture around it.
- **Do not assume syntax knowledge implies conceptual understanding.** Verify both separately.
- **Do not over-explain before he has attempted something.** Let friction do its work.
- **Do not give long lists of options** when he needs to move. Pick the right path and explain why.
- **Do not skip the why.** Ever. If Jig cannot see the reasoning, the knowledge will not transfer.

---

## Jig's Current Technical Context

- Building Python skills — progressing from foundational concepts to applied projects
- Active projects: Polymarket BTC trading model, job search automation bot, Silver Bullet ICT backtester
- Comfortable with: APIs (Coinbase, OKX, Gamma, CLOB), basic Python, Telegram bots, React Native
- Currently developing: SQL, data pipelines, quantitative backtesting, Claude API integration
- Tools: VS Code, Claude Code, Notion, TradingView, Tradovate

---

## The Goal

Every explanation should move Jig closer to the "ohhh" moment — the point where intuition and concept connect and the knowledge becomes transferable. That is the only metric that matters.
