# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

The clearest weakness I found during testing is that **the energy term acts as a universal score floor that drowns out weak taste signals**. Every song earns energy-closeness points no matter how badly it mismatches the user, so a song with zero genre, mood, or acoustic connection can still ride into the top 5 purely by having a similar energy level — that's how *Cumbia Sunrise* (latin) reached the top 5 for both the pop lover and the rock lover. This hurts users whose taste is defined by identity rather than intensity: the "sad + high energy" user got four high-energy songs and almost nothing sad, because one mood point can't compete with ~1.5 energy points that every energetic song collects automatically. The system also fails silently for users outside the catalog's vocabulary — a k-pop fan gets confident-looking recommendations built on nothing but tempo math, with no warning that their actual taste was ignored. Finally, catalog imbalance compounds this: lofi has three songs while metal, reggae, and latin have one each, so some "favorite genres" simply have more chances to fill a top-5 list than others.

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
