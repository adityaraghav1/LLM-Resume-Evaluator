# AI Resume Evaluator

LLM-powered resume screening and candidate ranking. Upload resumes (PDF/DOCX)
and a job description, and get each candidate scored, matched against
required skills, and given an AI-written verdict — all in a Streamlit UI.

## How it works

1. `parser.py` extracts raw text from uploaded PDF/DOCX resumes.
2. `llm.py` calls Groq (`llama-3.3-70b-versatile`) to:
   - parse the job description into structured fields
   - parse each resume into structured fields
   - score each resume against the job description
3. `resume_parser.py` runs this pipeline across every resume in a folder
   and returns candidates sorted by score.
4. `app.py` is the Streamlit front end that ties it all together.

## Setup

**Requirements:** Python 3.11+, a free [Groq API key](https://console.groq.com/keys)

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your key:

```bash
cp .env.example .env
```

```
GROQ_API_KEY=your_groq_api_key_here
```

## Run locally

```bash
streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## Testing the pipeline directly

Drop a sample resume at `resumes/resume1.pdf`, then:

```bash
python test_pipeline.py
```

## Project structure

```
.
├── app.py              
├── llm.py               
├── models.py             
├── parser.py             
├── resume_parser.py        
├── test_pipeline.py         
├── resumes/                
├── requirements.txt
├── pyproject.toml
└── .env.example
```
