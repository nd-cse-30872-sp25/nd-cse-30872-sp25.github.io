import os
import json

# Configuration
RESULTS_DIR = "static/grading/results"
LEADERBOARD_FILE = "static/json/leaderboard.json"
BONUS_POOL = 100
GUARANTEED_POINTS = 1

def aggregate_results():
    """
    Aggregate results from all students and distribute bonus points.
    """
    raw_scores = {}
    for file_name in os.listdir(RESULTS_DIR):
        if file_name.endswith(".json"):
            with open(os.path.join(RESULTS_DIR, file_name), "r") as f:
                data = json.load(f)
                raw_scores[data["student"]] = data["raw_score"]

    # Distribute bonus points
    total_raw_scores = sum(raw_scores.values())
    remaining_pool = BONUS_POOL - (len(raw_scores) * GUARANTEED_POINTS)

    leaderboard = []
    for student, raw_score in raw_scores.items():
        normalized_score = raw_score / total_raw_scores if total_raw_scores > 0 else 0
        bonus_points = GUARANTEED_POINTS + (normalized_score * remaining_pool)

        leaderboard.append({
            "student": student,
            "raw_score": raw_score,
            "bonus_points": round(bonus_points, 2),
        })

    return leaderboard


def save_leaderboard(leaderboard):
    """
    Save the leaderboard as a JSON file.
    """
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=4)


if __name__ == "__main__":
    # Aggregate scores and calculate bonus points
    leaderboard = aggregate_results()

    # Save the updated leaderboard
    save_leaderboard(leaderboard)

    print(f"Leaderboard updated and saved to {LEADERBOARD_FILE}")