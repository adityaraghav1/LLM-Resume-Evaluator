from typing import List, Optional, Union
from pydantic import BaseModel, field_validator


def _stringify(value) -> str:
    """
    Turn a dict or list coming back from the LLM into a readable string,
    since smaller/faster models don't always follow the schema exactly.
    """

    if isinstance(value, dict):
        parts = [
            f"{key}: {val}"
            for key, val in value.items()
            if val not in (None, "", [])
        ]
        return ", ".join(parts)

    if isinstance(value, list):
        return " ".join(_stringify(item) for item in value if item)

    return str(value)


class Experience(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None

    @field_validator("description", mode="before")
    @classmethod
    def coerce_description(cls, v):
        if v is None or isinstance(v, str):
            return v
        return _stringify(v)


class Resume(BaseModel):

    name: Optional[str] = None

    email: Optional[str] = None

    phone: Optional[str] = None

    education: List[str] = []

    skills: List[str] = []

    experience: List[Experience] = []

    @field_validator("education", mode="before")
    @classmethod
    def coerce_education(cls, v):
        if not isinstance(v, list):
            return v
        return [item if isinstance(item, str) else _stringify(item) for item in v]

    @field_validator("skills", mode="before")
    @classmethod
    def coerce_skills(cls, v):
        if not isinstance(v, list):
            return v
        return [item if isinstance(item, str) else _stringify(item) for item in v]



class JobDescription(BaseModel):

    title: Optional[str] = None

    required_skills: List[str] = []

    experience_required: Optional[str] = None

    education_required: Optional[str] = None

    description: Optional[str] = None



class MatchResult(BaseModel):

    score: int

    details: dict
