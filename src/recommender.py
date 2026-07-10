import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

# Scoring weights from the Algorithm Recipe (see README: How The System Works)
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_BONUS = 0.5
ACOUSTIC_THRESHOLD = 0.6

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

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs ranked by how well they match the user's taste."""
        prefs = user.to_prefs()
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(prefs, asdict(song))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of why a song scored what it did."""
        score, reasons = score_song(user.to_prefs(), asdict(song))
        return f"{song.title} scored {score:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Reads the song catalog CSV into a list of dicts, converting numeric fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            row["tempo_bpm"] = int(row["tempo_bpm"])
            for field in ("energy", "valence", "danceability", "acousticness"):
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores one song against the user's preferences, returning (score, reasons)."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs["favorite_genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {song['genre']} (+{GENRE_WEIGHT:.1f})")

    if song["mood"] == user_prefs["favorite_mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {song['mood']} (+{MOOD_WEIGHT:.1f})")

    # Closeness rewards songs near the target energy, not just high or low ones.
    closeness = 1.0 - abs(user_prefs["target_energy"] - song["energy"])
    energy_points = ENERGY_WEIGHT * closeness
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} "
        f"(+{energy_points:.2f})"
    )

    if user_prefs.get("likes_acoustic") and song["acousticness"] >= ACOUSTIC_THRESHOLD:
        score += ACOUSTIC_BONUS
        reasons.append(f"acoustic feel (+{ACOUSTIC_BONUS:.1f})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song in the catalog and returns the top k as (song, score, explanation)."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
