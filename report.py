import json
from tabulate import tabulate


def generate_report(results_path: str = "eval_results.json") -> None:
    with open(results_path, "r") as f:
        results = json.load(f)
    
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    pass_rate = (passed / total) * 100
    
    avg_groundedness = sum(r["scores"]["groundedness"] for r in results) / total
    avg_relevance = sum(r["scores"]["relevance"] for r in results) / total
    avg_correctness = sum(r["scores"]["correctness"] for r in results) / total
    avg_overall = sum(r["scores"]["overall"] for r in results) / total
    
    print("\n" + "=" * 70)
    print("  FINSIGHT EVALS — RESULTS REPORT")
    print("=" * 70)
    
    print(f"\nOverall Pass Rate:  {pass_rate:.1f}%  ({passed}/{total} questions passed)")
    print(f"Average Scores:")
    print(f"  Groundedness:  {avg_groundedness:.2f}")
    print(f"  Relevance:     {avg_relevance:.2f}")
    print(f"  Correctness:   {avg_correctness:.2f}")
    print(f"  Overall:       {avg_overall:.2f}")
    
    print("\n" + "-" * 70)
    print("QUESTION BREAKDOWN")
    print("-" * 70)
    
    table_data = []
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        table_data.append([
            r["id"],
            r["question"][:40] + "...",
            r["category"],
            r["difficulty"],
            f"{r['scores']['groundedness']:.2f}",
            f"{r['scores']['relevance']:.2f}",
            f"{r['scores']['correctness']:.2f}",
            f"{r['scores']['overall']:.2f}",
            status
        ])
    
    headers = ["ID", "Question", "Category", "Difficulty", 
               "Ground.", "Relev.", "Correct.", "Overall", "Result"]
    
    print(tabulate(table_data, headers=headers, tablefmt="simple"))
    
    print("\n" + "-" * 70)
    print("FAILED QUESTIONS")
    print("-" * 70)
    
    failed_results = [r for r in results if not r["passed"]]
    
    if not failed_results:
        print("All questions passed.")
    else:
        for r in failed_results:
            print(f"\n{r['id']}: {r['question']}")
            print(f"Expected: {r['expected']}")
            print(f"Actual:   {r['actual'][:200]}...")
            print(f"Reasoning: {r['scores']['reasoning']}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    generate_report()