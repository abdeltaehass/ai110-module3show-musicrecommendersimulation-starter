"""
Command line runner for the Music Recommender Simulation.

Run from the project root with:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    }
    print(
        f"User profile: genre={user_prefs['favorite_genre']}, "
        f"mood={user_prefs['favorite_mood']}, "
        f"energy={user_prefs['target_energy']}, "
        f"acoustic={user_prefs['likes_acoustic']}"
    )

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} — {song['artist']}  [score: {score:.2f}]")
        print(f"   because: {explanation}\n")


if __name__ == "__main__":
    main()
