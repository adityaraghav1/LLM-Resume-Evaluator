from parser import read_resume
from llm import parse_resume


resume_path = "resumes/resume1.pdf"


text = read_resume(resume_path)

print("\n--- Resume Text ---")
print(text[:500])


resume = parse_resume(text)


print("\n--- Parsed Resume ---")
print(resume.model_dump_json(indent=2))
