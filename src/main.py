"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:
    python -m src.main
"""

import textwrap

from src.recommender import SCORING_MODES, load_songs, recommend_songs

# Test profiles: three distinct listener types, two adversarial/edge cases,
# and one profile that exercises the extended attributes (decade, popularity,
# instrumental preference, detailed mood tags).
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
    # Extended attributes: mood tag ("cozy" is a tag, never a primary mood),
    # release decade, popularity, and instrumental preference all in play.
    "Cozy Evening (extended)": {
        "favorite_genre": "jazz",
        "favorite_mood": "cozy",
        "target_energy": 0.35,
        "likes_acoustic": True,
        "favorite_decade": 2000,
        "prefers_popular": True,
        "prefers_instrumental": True,
    },
}

TITLE_W, ARTIST_W, REASON_W = 20, 18, 46


def print_table(recommendations: list) -> None:
    """Prints recommendations as an ASCII table with wrapped reason columns."""
    divider = f"+----+{'-' * (TITLE_W + 2)}+{'-' * (ARTIST_W + 2)}+-------+{'-' * (REASON_W + 2)}+"
    print(divider)
    print(f"| #  | {'Title':<{TITLE_W}} | {'Artist':<{ARTIST_W}} | Score | {'Reasons':<{REASON_W}} |")
    print(divider)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reason_lines = textwrap.wrap(explanation, REASON_W) or [""]
        print(
            f"| {rank:<2} | {song['title'][:TITLE_W]:<{TITLE_W}} "
            f"| {song['artist'][:ARTIST_W]:<{ARTIST_W}} | {score:>5.2f} "
            f"| {reason_lines[0]:<{REASON_W}} |"
        )
        for line in reason_lines[1:]:
            print(f"|    | {'':<{TITLE_W}} | {'':<{ARTIST_W}} |       | {line:<{REASON_W}} |")
    print(divider)


def describe(user_prefs: dict) -> str:
    """Formats a profile's preferences as a one-line summary."""
    return ", ".join(f"{key}={value}" for key, value in user_prefs.items())


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    print("#" * 70)
    print("# Top 5 per profile (balanced mode)")
    print("#" * 70)
    for name, prefs in PROFILES.items():
        print(f"\nProfile: {name}")
        print(f"  {describe(prefs)}\n")
        print_table(recommend_songs(prefs, songs, k=5))

    print()
    print("#" * 70)
    print("# Scoring modes compared — Conflicted profile (sad + high energy)")
    print("#" * 70)
    conflicted = PROFILES["Conflicted (sad + high energy)"]
    for mode in SCORING_MODES:
        top3 = recommend_songs(conflicted, songs, k=3, mode=mode)
        picks = ", ".join(f"{song['title']} ({score:.2f})" for song, score, _ in top3)
        print(f"{mode:>15}: {picks}")

    print()
    print("#" * 70)
    print("# Diversity penalty — Chill Lofi profile")
    print("#" * 70)
    chill = PROFILES["Chill Lofi"]
    print("\nWithout diversity penalty:\n")
    print_table(recommend_songs(chill, songs, k=5))
    print("\nWith diversity penalty (repeat artist -0.5, repeat genre -0.3):\n")
    print_table(recommend_songs(chill, songs, k=5, diversify=True))


if __name__ == "__main__":
    main()
