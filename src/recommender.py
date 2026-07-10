import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# Scoring modes (Strategy pattern): each mode is an interchangeable weight
# table, so the ranking behavior can be swapped without touching the scoring
# code. "balanced" is the Algorithm Recipe documented in the README.
SCORING_MODES: Dict[str, Dict[str, float]] = {
    "balanced": {
        "genre": 2.0, "mood": 1.0, "mood_tag": 0.5, "energy": 1.5,
        "acoustic": 0.5, "popularity": 0.5, "decade": 0.5, "instrumental": 0.5,
    },
    "genre-first": {
        "genre": 4.0, "mood": 0.5, "mood_tag": 0.25, "energy": 0.75,
        "acoustic": 0.5, "popularity": 0.5, "decade": 0.5, "instrumental": 0.5,
    },
    "mood-first": {
        "genre": 0.75, "mood": 3.0, "mood_tag": 1.5, "energy": 1.0,
        "acoustic": 0.5, "popularity": 0.5, "decade": 0.5, "instrumental": 0.5,
    },
    "energy-focused": {
        "genre": 0.5, "mood": 0.5, "mood_tag": 0.25, "energy": 4.0,
        "acoustic": 0.25, "popularity": 0.25, "decade": 0.25, "instrumental": 0.25,
    },
}

ACOUSTIC_THRESHOLD = 0.6
INSTRUMENTAL_THRESHOLD = 0.2

# Diversity penalties: subtracted per repeat of the same artist/genre already
# in the recommendation list being built.
ARTIST_REPEAT_PENALTY = 0.5
GENRE_REPEAT_PENALTY = 0.3

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2010
    duration_sec: int = 200
    vocalness: float = 0.5
    mood_tags: str = ""

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

    def to_prefs(self) -> Dict:
        """Converts the profile into the plain dict format used by score_song."""
        return asdict(self)

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5, mode: str = "balanced") -> List[Song]:
        """Returns the top k songs ranked by how well they match the user's taste."""
        prefs = user.to_prefs()
        weights = SCORING_MODES[mode]
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(prefs, asdict(song), weights)[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song, mode: str = "balanced") -> str:
        """Returns a human-readable explanation of why a song scored what it did."""
        score, reasons = score_song(user.to_prefs(), asdict(song), SCORING_MODES[mode])
        return f"{song.title} scored {score:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Reads the song catalog CSV into a list of dicts, converting numeric fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in ("id", "tempo_bpm", "popularity", "release_decade", "duration_sec"):
                row[field] = int(row[field])
            for field in ("energy", "valence", "danceability", "acousticness", "vocalness"):
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict, weights: Optional[Dict[str, float]] = None) -> Tuple[float, List[str]]:
    """Scores one song against the user's preferences, returning (score, reasons)."""
    w = weights or SCORING_MODES["balanced"]
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs["favorite_genre"]:
        score += w["genre"]
        reasons.append(f"genre match: {song['genre']} (+{w['genre']:.1f})")

    # Detailed mood tags give partial credit when the primary mood misses,
    # e.g. a "cozy" listener still connects with a song tagged cozy|warm.
    mood_tags = [tag for tag in str(song.get("mood_tags", "")).split("|") if tag]
    if song["mood"] == user_prefs["favorite_mood"]:
        score += w["mood"]
        reasons.append(f"mood match: {song['mood']} (+{w['mood']:.1f})")
    elif user_prefs["favorite_mood"] in mood_tags:
        score += w["mood_tag"]
        reasons.append(f"mood tag match: {user_prefs['favorite_mood']} (+{w['mood_tag']:.1f})")

    # Closeness rewards songs near the target energy, not just high or low ones.
    closeness = 1.0 - abs(user_prefs["target_energy"] - song["energy"])
    energy_points = w["energy"] * closeness
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} "
        f"(+{energy_points:.2f})"
    )

    if user_prefs.get("likes_acoustic") and song["acousticness"] >= ACOUSTIC_THRESHOLD:
        score += w["acoustic"]
        reasons.append(f"acoustic feel (+{w['acoustic']:.1f})")

    if user_prefs.get("prefers_popular") and "popularity" in song:
        pop_points = w["popularity"] * song["popularity"] / 100
        score += pop_points
        reasons.append(f"popularity {song['popularity']}/100 (+{pop_points:.2f})")

    if user_prefs.get("favorite_decade") and song.get("release_decade") == user_prefs["favorite_decade"]:
        score += w["decade"]
        reasons.append(f"{song['release_decade']}s release (+{w['decade']:.1f})")

    if user_prefs.get("prefers_instrumental") and song.get("vocalness", 1.0) <= INSTRUMENTAL_THRESHOLD:
        score += w["instrumental"]
        reasons.append(f"instrumental (+{w['instrumental']:.1f})")

    return score, reasons

def apply_diversity_penalty(scored: List[Tuple[Dict, float, str]], k: int) -> List[Tuple[Dict, float, str]]:
    """Greedily picks k songs, penalizing repeats of an artist or genre already picked."""
    remaining = list(scored)
    picked: List[Tuple[Dict, float, str]] = []

    def adjusted_score(item: Tuple[Dict, float, str]) -> float:
        song = item[0]
        penalty = ARTIST_REPEAT_PENALTY * sum(1 for p, _, _ in picked if p["artist"] == song["artist"])
        penalty += GENRE_REPEAT_PENALTY * sum(1 for p, _, _ in picked if p["genre"] == song["genre"])
        return item[1] - penalty

    while remaining and len(picked) < k:
        best = max(remaining, key=adjusted_score)
        remaining.remove(best)
        song, raw_score, explanation = best
        adjusted = adjusted_score(best)
        if adjusted < raw_score:
            explanation += f"; diversity penalty (-{raw_score - adjusted:.2f}: artist/genre already listed)"
        picked.append((song, adjusted, explanation))
    return picked

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    diversify: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Scores every song with the chosen mode's weights and returns the top k as (song, score, explanation)."""
    weights = SCORING_MODES[mode]
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, weights)
        scored.append((song, score, "; ".join(reasons)))
    scored.sort(key=lambda item: item[1], reverse=True)
    if diversify:
        return apply_diversity_penalty(scored, k)
    return scored[:k]
