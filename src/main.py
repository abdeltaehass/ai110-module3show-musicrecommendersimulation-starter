"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs

# Test profiles: three distinct listener types plus two adversarial/edge cases.
PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.9,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "likes_acoustic": False,
    },
    # Adversarial: conflicting preferences — sad mood but near-max energy.
    "Conflicted (sad + high energy)": {
        "favorite_genre": "edm",
        "favorite_mood": "sad",
        "target_energy": 0.9,
        "likes_acoustic": True,
    },
    # Edge case: a genre that does not exist anywhere in the catalog.
    "Unknown Genre (k-pop)": {
        "favorite_genre": "k-pop",
        "favorite_mood": "focused",
        "target_energy": 0.5,
        "likes_acoustic": False,
    },
}


def run_profile(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Prints the top k recommendations for one named user profile."""
    print("=" * 70)
    print(f"Profile: {name}")
    print(
        f"  genre={user_prefs['favorite_genre']}, "
        f"mood={user_prefs['favorite_mood']}, "
        f"energy={user_prefs['target_energy']}, "
        f"acoustic={user_prefs['likes_acoustic']}"
    )
    print()
    for rank, (song, score, explanation) in enumerate(
        recommend_songs(user_prefs, songs, k), start=1
    ):
        print(f"{rank}. {song['title']} — {song['artist']}  [score: {score:.2f}]")
        print(f"   because: {explanation}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs)


if __name__ == "__main__":
    main()
