import os
import json
import subprocess
import time
import sys

# Configuration
GRADING_DIR = "static/grading"
RESULTS_DIR = os.path.join(GRADING_DIR, "results")
CODE_DIR = os.path.join(GRADING_DIR, "code")
DEFAULT_LANGUAGE = "python"  # Default language (can be dynamically determined)
LANG_EXTENSIONS = {
    "python": "py",
    "java": "java",
    "c++": "cpp",
    "c": "c",
    "javascript": "js",
}

def find_submission_file(language):
    """
    Locate the student's submission file based on the language extension.
    """
    ext = LANG_EXTENSIONS.get(language, None)
    if not ext:
        raise ValueError(f"Unsupported language: {language}")

    for file in os.listdir("."):
        if file.endswith(f".{ext}"):
            return file

    raise FileNotFoundError(f"No submission file found for language: {language}")


def calculate_correctness(input_path, output_path, student_file):
    """
    Compare the student's output to the expected output for correctness.
    """
    with open(input_path, "r") as f_in, open(output_path, "r") as f_out:
        expected_output = f_out.read().strip()
        try:
            result = subprocess.run(
                ["python3", student_file],
                input=f_in.read(),
                text=True,
                capture_output=True,
                timeout=5,  # Prevent infinite loops
            )
            student_output = result.stdout.strip()
            return 1.0 if student_output == expected_output else 0.0
        except subprocess.TimeoutExpired:
            return 0.0


def calculate_speed(input_path, student_file):
    """
    Measure execution speed for the student's program.
    """
    with open(input_path, "r") as f_in:
        try:
            start_time = time.time()
            subprocess.run(
                ["python3", student_file],
                input=f_in.read(),
                text=True,
                capture_output=True,
                timeout=5,
            )
            elapsed_time = time.time() - start_time
            threshold = 2  # Threshold in seconds for a max score
            return max(0, min(1, threshold / elapsed_time))
        except subprocess.TimeoutExpired:
            return 0.0


def calculate_linting(student_file):
    """
    Calculate the linting score based on PEP8 compliance using flake8.
    """
    try:
        result = subprocess.run(["flake8", student_file], capture_output=True, text=True)
        linting_errors = len(result.stdout.splitlines())
        max_errors = 10  # Maximum tolerable errors for a score of 0
        return max(0, 1 - (linting_errors / max_errors))
    except FileNotFoundError:
        print("flake8 is not installed. Skipping linting.")
        return 0


if __name__ == "__main__":
    # Extract branch name (challenge name) from environment variables
    github_ref = os.getenv("GITHUB_REF", "")
    challenge = github_ref.split("/")[-1]  # Extract branch name (e.g., refs/heads/challenge00)
    if not challenge.startswith("challenge"):
        raise ValueError("Branch name must start with 'challenge' (e.g., challenge00)")

    # Locate input/output files for the challenge
    input_path = os.path.join(CODE_DIR, challenge, "input.txt")
    output_path = os.path.join(CODE_DIR, challenge, "output.txt")
    if not os.path.exists(input_path) or not os.path.exists(output_path):
        raise FileNotFoundError(f"Input/output files not found for challenge: {challenge}")

    # Determine the submission language and locate the file
    language = DEFAULT_LANGUAGE  # Modify if you want to determine dynamically
    student_file = find_submission_file(language)

    # Calculate scores
    correctness = calculate_correctness(input_path, output_path, student_file)
    speed = calculate_speed(input_path, student_file)
    linting = calculate_linting(student_file)
    raw_score = round(0.7 * correctness + 0.2 * speed + 0.1 * linting, 2)

    # Generate results
    results = {
        "student": os.getenv("GITHUB_ACTOR", "unknown_student"),
        "challenge": challenge,
        "correctness": correctness,
        "speed": speed,
        "linting": linting,
        "raw_score": raw_score,
    }

    # Save results to JSON
    os.makedirs(RESULTS_DIR, exist_ok=True)
    results_path = os.path.join(RESULTS_DIR, f"{results['student']}.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=4)

    print("Grading complete. Results saved to:", results_path)