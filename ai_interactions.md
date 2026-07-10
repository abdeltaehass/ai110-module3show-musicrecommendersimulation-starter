# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Two multi-step extension tasks in one session: (1) add five new attributes (popularity, release decade, duration, vocalness, detailed mood tags) to all 20 songs in `data/songs.csv` and wire them into the scoring logic; (2) implement a diversity penalty so the top-5 list stops stacking songs from the same artist or genre. A hard constraint I set up front: the five existing test profiles had to produce byte-identical scores afterward, because my model card documents their exact outputs as evidence.

**Prompts used:**

- "Add these 5 columns to every row of songs.csv: popularity (0–100), release_decade, duration_sec, vocalness (0–1), and mood_tags (pipe-separated so commas don't break the CSV). Keep values internally consistent with each song's existing genre/energy — a metal track shouldn't be 95% acoustic."
- "Extend score_song to use the new attributes, but every new term must be gated behind a new user preference key accessed with .get(), so profiles that don't set those keys score exactly as before. Verify the math stays valid and the old tests still pass."
- "Add a diversity rule to recommend_songs: when building the top-k list, penalize a candidate's score by 0.5 for each already-picked song by the same artist and 0.3 for each with the same genre. The penalty must appear in the printed reasons so the re-ranking is explainable."

**What did the agent generate or change?**

- `data/songs.csv`: 5 new columns across all 20 rows.
- `src/recommender.py`: new gated scoring terms (popularity scaling, decade match, instrumental bonus, mood-tag partial credit), an `apply_diversity_penalty` function using greedy re-ranking, new fields on the `Song` dataclass with defaults so old constructor calls still work, and updated `load_songs` type conversions.
- `src/main.py`: a sixth profile ("Cozy Evening") that exercises every new attribute, plus a before/after diversity demo.

**What did you verify or fix manually?**

- Re-ran `python -m src.main` and compared the five original profiles' scores line-by-line against the model card — all unchanged (e.g. Library Rain still exactly 5.00), confirming the gating worked.
- Hand-traced Coffee Shop Stories under the new profile: 2.0 + 0.5 + 1.47 + 0.5 + 0.26 + 0.5 = 5.23, matching the printed score.
- Checked the diversity math: Focus Flow's −1.10 penalty = one repeat artist (−0.5) + two repeat genres (−0.3 × 2). Verified Spacewalk Thoughts correctly jumped it in the ranking.
- Ran `pytest` to confirm the starter tests (which build `Song` objects without the new fields) still pass thanks to the dataclass defaults.
- One design choice I had to make myself: the agent initially had a mood-tag match *stack* with a primary mood match, double-counting mood. I had it changed to an either/or (full credit for primary match, partial credit via tags only when the primary misses).

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

The **Strategy pattern** (in a lightweight, Pythonic form) for the multiple scoring modes: balanced, genre-first, mood-first, and energy-focused.

**How did AI help you brainstorm or implement it?**

I asked how to support multiple ranking strategies without duplicating the scoring function or littering it with if/elif mode checks. The discussion surfaced three options: (a) subclasses of a `ScoringStrategy` base class, (b) passing scoring functions as first-class values, and (c) a dictionary of named weight tables passed into one shared scoring function. We chose (c): since all four modes share the same *formula* and differ only in *coefficients*, the "strategy" that varies is just data. Full strategy classes would have been ceremony without benefit at this scale — a point the AI made and I agreed with after sketching what the class version would look like.

**How does the pattern appear in your final code?**

`SCORING_MODES` at the top of `src/recommender.py` maps each mode name to an interchangeable weight table. `score_song(user_prefs, song, weights)` is the single shared algorithm; `recommend_songs(..., mode="balanced")` and `Recommender.recommend(..., mode=...)` select the strategy at call time. Adding a fifth mode is one dictionary entry — no scoring code changes. The mode-comparison demo in `src/main.py` shows the payoff: the same conflicted user gets three different #1 songs depending on which strategy is active.
