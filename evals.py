import json
import os
import chromadb
import anthropic
from chromadb.utils import embedding_functions
from judge import judge_answer

# Configuration
CHROMA_PATH = "../finsight-rag/chroma_db"
DATASET_PATH = "dataset.json"
PASS_THRESHOLD = 0.7

def load_dataset(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def get_rag_answer(question: str, collection_id: str) -> str:
    embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    try:
        collection = chroma_client.get_collection(
            name=collection_id,
            embedding_function=embedding_fn
        )
        
        results = collection.query(
            query_texts=[question],
            n_results=8
        )
        
        chunks = results["documents"][0]
        context = "\n\n---\n\n".join(chunks)
        
        client = anthropic.Anthropic()
        
        prompt = f"""You are a financial analyst assistant. Use ONLY the document excerpts below to answer the question. If the answer is not in the excerpts, say so clearly.

DOCUMENT EXCERPTS:
{context}

QUESTION:
{question}

ANSWER:"""
        
        message = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    except Exception as e:
        return f"Error retrieving answer: {str(e)}"

def run_evals() -> list:
    print("Loading dataset...")
    dataset = load_dataset(DATASET_PATH)
    
    collection_id = dataset["collection_id"]
    questions = dataset["questions"]
    
    print(f"Running {len(questions)} questions against collection: {collection_id}")
    print("-" * 60)
    
    results = []
    
    for i, item in enumerate(questions):
        question_id = item["id"]
        question = item["question"]
        expected = item["expected_answer"]
        category = item["category"]
        difficulty = item["difficulty"]
        
        print(f"[{i+1}/{len(questions)}] {question_id}: {question[:50]}...")
        
        # Step 1 — get actual answer from RAG system
        actual = get_rag_answer(question, collection_id)
        # Step 2 — judge the answer
        scores = judge_answer(question, expected, actual)
        
        # Step 3 — determine pass/fail
        passed = scores["overall"] >= PASS_THRESHOLD
        
        result = {
            "id": question_id,
            "question": question,
            "expected": expected,
            "actual": actual,
            "category": category,
            "difficulty": difficulty,
            "scores": scores,
            "passed": passed
        }
        
        results.append(result)
        
        status = "PASS" if passed else "FAIL"
        print(f"   Overall: {scores['overall']:.2f} | {status}")
        print(f"   Groundedness: {scores['groundedness']:.2f} | Relevance: {scores['relevance']:.2f} | Correctness: {scores['correctness']:.2f}")
        print()
    
    return results


if __name__ == "__main__":
    results = run_evals()
    
    # Save results to file
    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=4)
    
    print("Results saved to eval_results.json")
    print("Run report.py to see the full summary")    