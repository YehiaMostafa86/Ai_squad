import json
import urllib.request
import random

def fetch_real_problems(num_problems=5):
    """
    Fetches real problems, but FILTERS OUT hard/open-ended questions.
    Only returns easy problems with strict, single-line answers.
    """
    print(f" Fetching {num_problems} easy exact-match problems via REST API...")
    
    # We pull a larger batch (30) so we have enough to filter through
    url = f"https://datasets-server.huggingface.co/rows?dataset=codeparrot/apps&config=introductory&split=test&offset=0&length={num_problems}"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return []

    formatted_problems = []
    problem_count = 0

    for entry in data.get("rows", []):
        row = entry["row"]
        try:
            test_cases = json.loads(row["input_output"])
            
            if not test_cases.get("inputs") or not test_cases.get("outputs"):
                continue
                
            hidden_input = test_cases["inputs"][0]
            expected_output = test_cases["outputs"][0]
            
            # --- THE EASY PROBLEM FILTER ---
            # 1. Skip problems with multiple lines of output
            if "\n" in expected_output.strip():
                continue
            
            # 2. Skip problems with long outputs (we want single numbers or YES/NO)
            if len(expected_output.strip()) > 10:
                continue
                
            # 3. Skip problems where the text says "several answers" are allowed
            question_text = row["question"].lower()
            if "several answers" in question_text or "print any" in question_text:
                continue
            # -------------------------------
            mock_diff = round(random.uniform(1.0,3.0),1)
            
            formatted_problems.append({
                "id": problem_count + 1,
                "title": f"APPS Challenge #{row['problem_id']} (Filtered)",
                "description": row["question"],
                "test_input": hidden_input,
                "expected_output": expected_output,
                "difficulty": mock_diff
            })
            
            problem_count += 1
            
            # Stop once we find the exact number of easy problems you asked for
            if problem_count >= num_problems:
                break
                
        except (json.JSONDecodeError, KeyError, IndexError):
            continue

    print(" Filtered Dataset loaded successfully!\n")
    return formatted_problems

# --- Quick Test ---
if __name__ == "__main__":
    problems = fetch_real_problems(3)
    for p in problems:
        print(f"Problem: {p['title']}")
        print(f"Input: {repr(p['test_input'])}")
        print(f"Expected Output: {repr(p['expected_output'])}\n")