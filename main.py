# main.py

import time
from llm_client import ask_ai_to_code
from snadbox_runner import evaluate_code
from database_loader import fetch_real_problems

# --- 1. The Mock Dataset ---
# Later, Role 1 will replace this with thousands of problems from Hugging Face.
# For now, we just use these two to prove the loop works.
PROBLEMS = fetch_real_problems(30)


# --- 2. The Competitors ---
# Which AIs are we testing today?
MODELS_TO_TEST = ["llama-3.3-70b-versatile"] ## llama-3.3-70b-versatile groq/compound-mini  openai/gpt-oss-120b

def run_testbed():
    print("===========================================")
    print(" STARTING ALGORITHMIC AI JUDGE TESTBED ")
    print("===========================================\n")
    
    # This dictionary will keep track of everyone's score
    leaderboard = {model: {"Accepted": 0, "WA": 0, "CE": 0, "TLE": 0} for model in MODELS_TO_TEST}

    # --- 3. The Main Loop ---
    for problem in PROBLEMS:
        print(f"--- Problem {problem['id']}: {problem['title']} ---")
        
        for ai_model in MODELS_TO_TEST:
            print(f"[{ai_model}] is writing code...")
            
            # Step A: Get the code from Groq
            cpp_code = ask_ai_to_code(ai_model, problem['description'])
            print(f"---------------------cpp_code:----------------------- {cpp_code}")
            
            # Step B: Pass it to the C++ Sandbox
            grade, time_taken = evaluate_code(cpp_code, problem['test_input'], problem['expected_output'])
            
            print(f"Result: {grade} ({time_taken}s)\n")
            
            # Step C: Update the Leaderboard Scorecard
            if grade == "Accepted":
                leaderboard[ai_model]["Accepted"] += 1
           
            elif grade == "Wrong Answer (WA)":
                leaderboard[ai_model]["WA"] += 1
            elif grade == "Compile Error (CE)":
                leaderboard[ai_model]["CE"] += 1
            elif grade == "Time Limit Exceeded (TLE)":
                leaderboard[ai_model]["TLE"] += 1
            print("Cooling down API for 10 seconds before next problem...")
            time.sleep(10)
                
        time.sleep(1) # Small pause so we don't spam the API too fast

    # --- 4. Print the Final Results ---
    print("===========================================")
    print(" FINAL LEADERBOARD RESULTS ")
    print("===========================================")
    for ai_model, scores in leaderboard.items():
        print(f"{ai_model}:")
        print(f"   Accepted: {scores['Accepted']}")
        print(f"   Wrong Answer: {scores['WA']}")
        print(f"   Compile Errors: {scores['CE']}")
        print(f"   TLE: {scores['TLE']}\n")

if __name__ == "__main__":
    run_testbed()