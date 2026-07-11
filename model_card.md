# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

---

## 2. Intended Use  

VibeMatch is a classroom simulation of a content-based music recommender. Given one user's stated taste — a favorite genre, a favorite mood, an ideal energy level, and whether they like acoustic sounds — it ranks a small song catalog and returns the top five matches, each with a plain-language reason.

It assumes the user can describe their own taste up front, that their taste fits the catalog's vocabulary (a "k-pop" fan is out of luck), and that taste doesn't change between requests.

**Intended for:** learning how recommendation scoring works, experimenting with weights, and discussing algorithmic bias.

**Not intended for:** real users or production use. It should not be used to make claims about real listening behavior, to discover genuinely new music (it recommends more of what you already said you like), or for anyone whose taste vocabulary isn't represented in the catalog — it will fail silently and still look confident.

---

## 3. How the Model Works  

Think of the system as a judge with a scorecard. For every song in the catalog, it asks four questions:

1. **Is this the user's favorite genre?** If yes, the song earns 2 points — the biggest prize, because genre is the strongest signal of taste.
2. **Is this the mood they asked for?** If yes, 1 point.
3. **How close is the song's energy to what they want?** This isn't a yes/no question — a song at exactly the right intensity earns 1.5 points, and the points shrink the further away it is. Someone who wants calm music shouldn't be handed the loudest track, and someone who wants a workout shouldn't get a lullaby.
4. **If the user likes acoustic sounds, does this song deliver them?** A small half-point bonus.

Add the points up and you get the song's score. Do that for all 20 songs, sort from highest to lowest, and the top five become the recommendations. Alongside each score, the system keeps the list of reasons it awarded points, so every recommendation can explain itself.

The starter project came with empty function shells; I implemented all of the loading, scoring, and ranking logic, chose the weights, added the acoustic bonus, and made the two code paths (the function-based one and the class-based one) share a single scoring brain so they can never disagree.

---

## 4. Data  

The catalog is `data/songs.csv`: **20 fictional songs** described by genre, mood, energy, tempo, valence (musical positivity), danceability, and acousticness. The starter file had 10 songs across 7 genres; I doubled it, adding 9 genres (hip hop, country, classical, edm, folk, metal, r&b, reggae, latin) and 7 moods (confident, nostalgic, melancholy, energetic, romantic, angry, sad) so the recommender would have real variety to choose from.

What the data can't see: lyrics, language, artist popularity, era or decade, vocals vs. instrumental, cultural context, and anything about *why* a person loves a song (memories, friends, trends). The catalog is also imbalanced — lofi has 3 tracks while metal, reggae, and latin have 1 each — which quietly gives some genres more chances to be recommended.

---

## 5. Strengths  

- **Coherent listeners get accurate lists.** The Chill Lofi profile's top three were the catalog's three lofi tracks, in energy-closeness order, with the two runner-ups being chill-adjacent outsiders (ambient, jazz). That matches exactly what a human would pick.
- **Every recommendation explains itself.** The reasons list ("genre match (+2.0); energy 0.35 vs target 0.35 (+1.50)") makes the system auditable — when a result looks odd, you can see precisely why it happened.
- **The energy-closeness idea works.** Rewarding *proximity* instead of *magnitude* let songs like *Coffee Shop Stories* (jazz, but quiet and acoustic) surface for the lofi listener — a vibe match across genre lines, which is the behavior real content-based systems aim for.
- **Profiles separate cleanly.** The pop and lofi test profiles shared zero songs in their top fives; pop and rock swapped their #1 picks exactly as intuition predicts.

---

## 6. Limitations and Bias 

The clearest weakness I found during testing is that **the energy term acts as a universal score floor that drowns out weak taste signals**. Every song earns energy-closeness points no matter how badly it mismatches the user, so a song with zero genre, mood, or acoustic connection can still ride into the top 5 purely by having a similar energy level — that's how *Cumbia Sunrise* (latin) reached the top 5 for both the pop lover and the rock lover. This hurts users whose taste is defined by identity rather than intensity: the "sad + high energy" user got four high-energy songs and almost nothing sad, because one mood point can't compete with ~1.5 energy points that every energetic song collects automatically. The system also fails silently for users outside the catalog's vocabulary — a k-pop fan gets confident-looking recommendations built on nothing but tempo math, with no warning that their actual taste was ignored. Finally, catalog imbalance compounds this: lofi has three songs while metal, reggae, and latin have one each, so some "favorite genres" simply have more chances to fill a top-5 list than others.

**Fairness update — diversity penalty (implemented).** After documenting these biases, I added an optional diversity rule to the ranking: when building the top-5 list, a candidate song loses 0.5 points for each already-selected song by the same artist and 0.3 points for each with the same genre, and the deduction is printed in the song's reasons so the re-ranking stays transparent. This directly attacks two of the problems above. It breaks the filter bubble's grip on the list: for the Chill Lofi user, the penalty stopped one artist (LoRoom) from taking two of the top three slots and promoted an ambient track with the right vibe instead, so the user sees more of the catalog without losing relevance. It also softens the catalog-imbalance advantage, because a genre with many entries can no longer flood the results just by showing up more often. The penalty is deliberately a re-ranking step rather than a scoring change — every song's underlying merit score is untouched, and fairness is applied only when composing the final list.

---

## 7. Evaluation  

I tested five profiles: three realistic listener types (**High-Energy Pop**, **Chill Lofi**, **Deep Intense Rock**) and two adversarial cases (**Conflicted** — sad mood but 0.9 energy, and **Unknown Genre** — a k-pop fan whose genre appears nowhere in the catalog). For each I checked whether the top 5 matched what a human DJ would pick, and whether the reasons printed by the system actually justified the ranking.

### Results (weights: genre 2.0, mood 1.0, energy 1.5, acoustic 0.5)

```
Profile: High-Energy Pop (genre=pop, mood=happy, energy=0.9)
1. Sunrise City — Neon Echo        [4.38]  genre + mood + energy 0.82
2. Gym Hero — Max Pulse            [3.46]  genre + energy 0.93
3. Rooftop Lights — Indigo Parade  [2.29]  mood + energy 0.76
4. Storm Runner — Voltline         [1.48]  energy 0.91 only
5. Cumbia Sunrise — Rio Bloom      [1.44]  energy 0.86 only
```

```
Profile: Chill Lofi (genre=lofi, mood=chill, energy=0.35, acoustic=True)
1. Library Rain — Paper Lanterns   [5.00]  genre + mood + perfect energy + acoustic
2. Midnight Coding — LoRoom        [4.89]  genre + mood + energy 0.42 + acoustic
3. Focus Flow — LoRoom             [3.92]  genre + energy 0.40 + acoustic
4. Spacewalk Thoughts — Orbit Bloom [2.90] mood + energy 0.28 + acoustic
5. Coffee Shop Stories — Slow Stereo [1.97] energy 0.37 + acoustic only
```

```
Profile: Deep Intense Rock (genre=rock, mood=intense, energy=0.95)
1. Storm Runner — Voltline         [4.44]  genre + mood + energy 0.91
2. Gym Hero — Max Pulse            [2.47]  mood + energy 0.93
3. Bassline Horizon — Klub Vector  [1.50]  perfect energy match only
4. Iron Choir — Gravemarch         [1.47]  energy 0.97 only
5. Cumbia Sunrise — Rio Bloom      [1.36]  energy 0.86 only
```

```
Profile: Conflicted (genre=edm, mood=sad, energy=0.9, acoustic=True)
1. Bassline Horizon — Klub Vector  [3.42]  genre + energy 0.95
2. Rainy Platform — Neon Echo      [1.81]  mood match, but energy 0.44 far off
3. Storm Runner — Voltline         [1.48]  energy only
4. Dust Road Home — Willow Creek   [1.48]  energy + acoustic
5. Gym Hero — Max Pulse            [1.46]  energy only
```

```
Profile: Unknown Genre (genre=k-pop, mood=focused, energy=0.5)
1. Focus Flow — LoRoom             [2.35]  mood + energy 0.40
2. Velvet Hour — Sable Rose        [1.47]  energy only
3. Island Clockwork — Palm Circuit [1.47]  energy only
4. Dust Road Home — Willow Creek   [1.42]  energy only
5. Rainy Platform — Neon Echo      [1.41]  energy only
```

### Comparing the profiles

- **Pop vs. Rock:** the top of each list swaps exactly as it should (*Sunrise City* ↔ *Storm Runner*), but the *bottoms* of the lists converge — both end with *Cumbia Sunrise*, because once genre and mood run out of matching songs, the energy term takes over and both profiles want roughly the same intensity.
- **Pop vs. Lofi:** these two share zero songs in their top 5, the cleanest separation in the test. The lofi profile's acoustic preference pulls in *Coffee Shop Stories* (jazz) and *Spacewalk Thoughts* (ambient) — genre outsiders that match the *vibe* — which is exactly the behavior the energy-closeness design was meant to produce.
- **Rock vs. Conflicted:** both are high-energy profiles, and 3 of 5 songs overlap (*Bassline Horizon*, *Storm Runner*, *Gym Hero*). The conflicted user's "sad" preference barely registers — one mood point can't outbid the energy floor — so the system quietly resolves the contradiction in favor of energy.
- **Conflicted vs. Unknown Genre:** the conflicted user at least gets their genre served (#1 is edm). The k-pop user gets nothing of theirs: every recommendation is scored on energy and mood alone, yet the output looks just as confident. Only the score magnitudes (max 2.35 vs. 5.00 for lofi) hint that the system is guessing.
- **Lofi vs. Unknown Genre:** highest-confidence vs. lowest-confidence lists. *Library Rain*'s perfect 5.00 comes from every term firing at once; *Velvet Hour*'s 1.47 comes from energy alone. The scores are honest about this — but only if you know to read them.

### What surprised me

**Gym Hero shows up for everyone.** It appears in three of five lists — for the pop fan, the rock fan, and the conflicted user. In plain language: *Gym Hero* is a pop song with near-maximum energy, and since most of my test users wanted high energy, it always collects the big energy points, then rides a genre or mood match the rest of the way. It's the catalog's "crowd-pleaser" — not because it's anyone's favorite, but because it's nobody's mismatch. Real platforms have the same phenomenon: broadly inoffensive tracks accumulate recommendations everywhere.

**The weight-shift experiment changed less than expected — until it didn't.** Doubling energy (1.5→3.0) and halving genre (2.0→1.0) left the top-5 *order identical* for all three realistic profiles; only the gaps compressed. But for the conflicted user, the change was dramatic: *Rainy Platform* — the only sad song, their only mood match — fell out of the top 5 entirely, replaced by more high-energy songs. The lesson: weights don't matter much when a user's preferences all point the same direction, but they decide *everything* when preferences conflict. The change made recommendations different, not better.

---

## 8. Future Work  

1. **Genre and mood similarity instead of exact matching.** Right now "indie pop" earns zero genre points from a pop fan and "relaxed" earns zero mood points from a chill fan, even though humans treat them as neighbors. A small similarity table (indie pop ≈ pop: 0.8) would award partial credit and fix the vocabulary brittleness — including giving the k-pop fan a reasonable pop-based list instead of silent failure.
2. **A confidence signal.** Scores should be normalized so users (or the UI) can tell a strong 5.0 match from a weak 1.5 guess. *(The diversity rule originally planned alongside this has since been implemented — see the fairness update in section 6 — but confidence signaling remains open.)*
3. **Learning from feedback.** Let likes and skips nudge the profile's weights over time instead of trusting a one-time questionnaire. That's the first step from pure content-based filtering toward the collaborative behavior real platforms use.

---

## 9. Personal Reflection  

My biggest learning moment was the weight-shift experiment. I expected that doubling the energy weight and halving genre would shuffle every list — instead, the three realistic profiles didn't change *at all*, and only the contradictory "sad but high energy" user was affected, losing their single sad song from the top five. That taught me something general: **weights don't matter when a user's preferences agree with each other; they decide everything when preferences conflict.** Tuning a recommender is really about deciding who wins the edge cases.

AI tools accelerated almost every phase — drafting the expanded catalog, sketching the scoring math, and generating the adversarial test profiles I probably wouldn't have thought of alone. But I learned to double-check everything against actual runs: the most valuable habit was tracing one song's score by hand (*Sunrise City*: 2.0 + 1.0 + 1.5 × (1 − 0.02) = 4.47) to confirm the code did what the recipe claimed, and reading the printed "reasons" to catch logic that looked right but scored wrong.

What surprised me most is how little machinery it takes for output to *feel* like a real recommendation. Twenty songs, four if-statements, and a sort — yet "Library Rain, because: genre match, mood match, perfect energy, acoustic feel" reads like Spotify talking to you. The explanation is doing as much psychological work as the math. It changed how I look at real apps: when a recommendation feels uncannily personal, it may just be a weighted sum with good reasons attached — and the same simplicity means the biases I found here (filter bubbles, catalog imbalance, silent failure for unusual tastes) are plausibly hiding inside systems used by billions of people.

If I extended this, I'd start with the similarity matrix from Future Work — exact string matching was the single biggest source of unfair results in my tests.
