import json
import requests

def run_evals():
    with open("cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    correct = 0
    failed_cases = []
    
    print("Running 8 eval cases against local API...\n")
    
    for i, case in enumerate(cases):
        response = requests.post(
            "http://127.0.0.1:8000/triage",
            json={"text": case["text"]}
        )
        
        if response.status_code == 200:
            result = response.json()
            actual = result["category"]
            
            if actual == case["expected_category"]:
                correct += 1
                print(f"Case {i+1}: PASS (Got {actual})")
            else:
                failed_cases.append({"text": case["text"], "expected": case["expected_category"], "got": actual, "reason": result["reason"]})
                print(f"Case {i+1}: FAIL (Expected {case['expected_category']}, got {actual})")
        else:
            print(f"Case {i+1}: ERROR {response.status_code}")
            
    print(f"\nFinal Score: {correct} / {len(cases)}")
    if failed_cases:
        print("\nFailed Cases:")
        print(json.dumps(failed_cases, indent=2))

if __name__ == "__main__":
    run_evals()