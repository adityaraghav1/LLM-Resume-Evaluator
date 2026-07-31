import time
from pathlib import Path

from parser import read_resume
from llm import (
    parse_resume,
    final_score
)


def evaluate_all_resumes(job, resume_folder):
    """
    Evaluate every resume inside a folder and
    return candidates sorted by score.
    """

    resume_folder = Path(resume_folder)

    if not resume_folder.exists():
        raise FileNotFoundError(
            f"{resume_folder} does not exist."
        )

    results = []

    for file_path in resume_folder.iterdir():

        if file_path.suffix.lower() not in [".pdf", ".docx"]:
            continue

        print(f"\nProcessing: {file_path.name}")

        try:

            resume_text = read_resume(file_path)

            parsed_resume = parse_resume(
                resume_text
            )

            time.sleep(1)

            match = final_score(
                job,
                parsed_resume
            )

            results.append({

                "name": parsed_resume.name,

                "score": match.score,

                "details": match.details

            })

            print(
                f"✓ {parsed_resume.name} : {match.score}%"
            )

        except Exception as e:

            print(
                f"❌ Failed to process {file_path.name}"
            )

            print(e)

    results.sort(

        key=lambda candidate: candidate["score"],

        reverse=True

    )

    return results
