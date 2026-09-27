# FinSight Evals: LLM Evaluation Framework

Module 3 of FinSight AI, a personal financial intelligence platform I built to support my own investment research.

This tool measures the quality of answers produced by the FinSight RAG system against a golden dataset of questions with known correct answers. It scores each answer on three dimensions (groundedness, relevance, and correctness) using Claude as a judge, and produces a detailed pass/fail report.

## Why this exists

Building an AI system that produces answers is one thing. Knowing whether those answers are accurate and trustworthy is another. For a financial research tool where bad information could lead to real investment decisions, measuring answer quality is not optional.

This eval framework lets you quantify system quality, track improvements across code changes, and identify specific failure modes such as retrieval gaps, hallucinations, or chunking problems before they affect real users.

## What it measures

Three dimensions, each scored 0.0 to 1.0:

**Groundedness:** Is the answer based on real document content or did the system fabricate information? A hallucinated revenue figure is more dangerous than admitting the information was not found.

**Relevance:** Does the answer actually address what was asked? A system can be perfectly grounded but still answer the wrong question.

**Correctness:** Does the answer match the known expected answer? Catches cases where the answer is real and on-topic but factually wrong.

A question passes if its overall score (average of the three dimensions) is at or above 0.7.

## Architecture

```
dataset.json contains golden questions with expected answers
    |
    v
evals.py loads each question and runs it through finsight-rag
    |
    v
get_rag_answer() queries ChromaDB directly for relevant chunks
then sends chunks + question to Claude for an answer
    |
    v
judge_answer() sends the question, expected answer, and actual answer
to Claude with a scoring rubric (LLM-as-a-judge pattern)
    |
    v
Claude returns groundedness, relevance, and correctness scores as JSON
    |
    v
Results saved to eval_results.json
    |
    v
report.py reads eval_results.json and prints a formatted summary
```

### Key design decisions

**LLM-as-a-judge:** Rather than rule-based string matching, Claude evaluates each answer against the expected answer using a structured rubric. Two answers that say the same thing differently both score well, while a subtly wrong number scores poorly. This is the same pattern used in production eval systems at major AI labs.

**Direct ChromaDB access:** The eval framework calls the RAG retrieval logic directly in Python rather than going through the Streamlit UI. This enables automated batch evaluation of all questions without manual interaction.

**Separation from application code:** The eval framework is a standalone module. It imports retrieval logic from finsight-rag but does not depend on the Streamlit app being running. This means evals can run in CI/CD pipelines or on a schedule without a running server.

**Structured JSON output from judge:** The judge prompt explicitly requests JSON-only output with defined keys. This makes scores machine-readable and easy to aggregate across many questions, which matters when scaling the dataset beyond 10 questions.

## Current results

Evaluated against Apple Inc 10-K 2025 (10 questions):

```
Overall Pass Rate:  70.0%  (7/10 passed)
Average Groundedness:  0.91
Average Relevance:     0.88
Average Correctness:   0.72
Average Overall:       0.84
```

Failure analysis identified two categories of issues: retrieval gaps where relevant content exists in the document but was not surfaced by the top-8 chunk search, and one case of overly simplified expected answers that did not match the document's actual level of detail.

## Tech stack

| Layer | Technology |
|---|---|
| LLM judge | Anthropic Claude (claude-sonnet-5) |
| RAG system under test | finsight-rag (ChromaDB + Claude) |
| Report formatting | tabulate |
| Language | Python 3.12 |

## Setup

**Requirements:** Python 3.12, an Anthropic API key, and finsight-rag cloned and set up at `../finsight-rag/` with at least one document ingested.

```bash
# Clone the repo
git clone https://github.com/PPatel98/finsight-evals.git
cd finsight-evals

# Create and activate a virtual environment
python3.12 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"   # Mac/Linux
setx ANTHROPIC_API_KEY "your-key-here"     # Windows

# Run the evaluation suite
python evals.py

# Generate the report
python report.py
```

## Project structure

```
finsight-evals/
    dataset.json        Golden test questions with expected answers
    evals.py            Runs each question through the RAG system and judges results
    judge.py            LLM-as-a-judge scoring function
    report.py           Generates formatted pass/fail summary from eval_results.json
    eval_results.json   Raw results from the most recent eval run
    requirements.txt
    README.md
```

## Extending the dataset

Add new questions to `dataset.json` following the existing format. Each question needs an `id`, `question`, `expected_answer`, `category`, and `difficulty`. The eval runner picks up new questions automatically on the next run.

Good questions for financial evals are specific (have a clear verifiable answer), varied across document sections, and realistic (things an investor would actually ask).

## Part of FinSight AI

This is Module 3 of a larger platform I am building for personal investment research.

| Module | Repo | Description | Status |
|---|---|---|---|
| 1 - Document Intelligence | [finsight-rag](https://github.com/PPatel98/finsight-rag) | Ask questions about any financial PDF | Complete |
| 2 - Research Agent | [finsight-agent](https://github.com/PPatel98/finsight-agent) | Autonomous multi-source company research | Complete |
| 3 - Eval Framework | [finsight-evals](https://github.com/PPatel98/finsight-evals) | Measure and validate AI answer quality | Complete |

## Author

Parth Patel, Software Engineer

- LinkedIn: [linkedin.com/in/parth-p75](https://linkedin.com/in/parth-p75)
- GitHub: [github.com/PPatel98](https://github.com/PPatel98)