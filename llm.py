import os
import json
import re
import time

from dotenv import load_dotenv
from groq import Groq

from models import (
    Resume,
    JobDescription,
    MatchResult
)

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "llama-3.1-8b-instant"

def call_groq_with_retry(max_retries: int = 5, **kwargs):
    """
    Wrap client.chat.completions.create with retry + backoff for 429s.
    Groq's error message includes the exact wait time (e.g. "try again
    in 2.31s"), so we parse that out instead of guessing.
    """
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**kwargs)

        except Exception as e:

            message = str(e)

            is_rate_limit = (
                "rate_limit_exceeded" in message
                or "429" in message
            )

            if not is_rate_limit or attempt == max_retries - 1:
                raise

            wait_match = re.search(r"try again in ([\d.]+)s", message)

            wait_time = float(wait_match.group(1)) + 1 if wait_match else (2 ** attempt)

            print(
                f"⏳ Rate limited, waiting {wait_time:.1f}s "
                f"(attempt {attempt + 1}/{max_retries})..."
            )

            time.sleep(wait_time)

    raise RuntimeError("Exceeded max retries due to rate limiting.")


JOB_SCHEMA = JobDescription.model_json_schema()


JOB_SYSTEM_PROMPT = f"""
You are an expert technical recruiter.

Extract the job description information.

Return ONLY valid JSON matching this schema:

{JOB_SCHEMA}

Rules:
- Do not invent information.
- Missing fields should be null.
- Missing lists should be [].
"""



def parse_job_description(job_text: str) -> JobDescription:


    response = call_groq_with_retry(

        model=MODEL,

        messages=[

            {
                "role": "system",
                "content": JOB_SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": job_text
            }

        ],

        response_format={
            "type": "json_object"
        }

    )


    data = json.loads(
        response.choices[0].message.content
    )


    return JobDescription(**data)


RESUME_SCHEMA = Resume.model_json_schema()


RESUME_SYSTEM_PROMPT = f"""
You are an expert resume parser.

Extract candidate information from the resume.

Return ONLY JSON matching this schema:

{RESUME_SCHEMA}

Rules:

- Do not invent information.
- Missing values should be null.
- Missing lists should be [].
- Extract skills from entire resume.
- Include internships as experience.
"""



def parse_resume(resume_text: str) -> Resume:


    response = call_groq_with_retry(

        model=MODEL,

        messages=[

            {
                "role": "system",
                "content": RESUME_SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": resume_text
            }

        ],

        response_format={
            "type": "json_object"
        }

    )


    data = json.loads(
        response.choices[0].message.content
    )


    return Resume(**data)



MATCH_SCHEMA = MatchResult.model_json_schema()



MATCH_SYSTEM_PROMPT = f"""

You are an expert technical recruiter.

Compare resume with job description.

Return ONLY JSON.

Follow this schema:

{MATCH_SCHEMA}


Rules:

- Score between 0 and 100.
- Never give 100 unless almost every requirement matches.
- Give realistic scores.
- Extract matching skills.
- Extract missing important skills.
- Check experience requirement.
- Check education requirement.
- Write a short professional verdict.


Return only JSON.

The details dictionary must contain:

- candidate_name
- matching_skills
- missing_important_skills
- experience_requirement_met
- education_requirement_met
- final_verdict


Rules:

- Score must be between 0 and 100.
- Do not invent skills.
- Keep verdict concise.
"""



def final_score(
    job: JobDescription,
    resume: Resume
) -> MatchResult:


    response = call_groq_with_retry(

        model=MODEL,

        messages=[

            {
                "role": "system",
                "content": MATCH_SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": f"""
Job Description:

{job.model_dump_json(indent=2)}


Resume:

{resume.model_dump_json(indent=2)}
"""
            }

        ],

        response_format={
            "type": "json_object"
        }

    )


    data = json.loads(
        response.choices[0].message.content
    )


    return MatchResult(**data)
