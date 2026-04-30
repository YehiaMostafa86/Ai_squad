# main.py

import time
from llm_client import ask_ai_to_code
from snadbox_runner import evaluate_code
from database_loader import fetch_real_problems


PROBLEMS = fetch_real_problems(30)
N = len(PROBLEMS)
MAX_SCORE = ((0.1 *3 * N) **-1) 


# --- 2. The Competitors ---
# Which AIs are we testing today?
MODELS_TO_TEST = ["llama-3.3-70b-versatile" , "groq/compound-mini" ,"openai/gpt-oss-120b" ] ## llama-3.3-70b-versatile groq/compound-mini  openai/gpt-oss-120b

def run_testbed():
    print("===========================================")
    print(" STARTING ALGORITHMIC AI JUDGE TESTBED ")
    print("===========================================\n")
    
    # This dictionary will keep track of everyone's score
    leaderboard = {model: {"Accepted": 0, "WA": 0, "CE": 0,"sum_weighted_time": 0.0, "final_score": 0.0} for model in MODELS_TO_TEST}

    # --- 3. The Main Loop ---
    for problem in PROBLEMS:
        print(f"--- Problem {problem['id']}: {problem['title']} (Difficulty: {problem['difficulty']}x) ---")
        
        for ai_model in MODELS_TO_TEST:
            
            print(f"[{ai_model}] is writing code...")
            
            # Step A: Get the code from Groq
 
            cpp_code = ask_ai_to_code(ai_model, problem['description'])
                
            
            # Step B: Pass it to the C++ Sandbox
            grade, time_taken = evaluate_code(cpp_code, problem['test_input'], problem['expected_output'])
            
            print(f"Result: {grade} ({time_taken}s)\n")
            
            # Step C: Update the Leaderboard Scorecard
            if grade == "Accepted":
                leaderboard[ai_model]["Accepted"] += 1
                actual_time = time_taken
           
            elif grade == "Wrong Answer (WA)":
                leaderboard[ai_model]["WA"] += 1
                actual_time = 2.0
            elif grade == "Compile Error (CE)":
                leaderboard[ai_model]["CE"] += 1
                actual_time = 2.0

            # Add (Time * Difficulty) to their total sum
            leaderboard[ai_model]["sum_weighted_time"] += (actual_time * problem['difficulty'])
            
            print("Cooling down API for 10 seconds before next problem...")
            time.sleep(10)
                
        time.sleep(1) # Small pause so we don't spam the API too fast
    for model_name, stats in leaderboard.items():
    # 1. Average the weighted time over all questions (N)
        avg_weighted_time = stats["sum_weighted_time"] 
        
        # Failsafe: Prevent division by zero if execution time was somehow perfectly 0.0
        if avg_weighted_time == 0:
            avg_weighted_time = 0.001
            
        # 2. Power of -1 to reward lower times
        raw_score = avg_weighted_time ** -1
        
        # 3. Divide by MAX_RAW_SCORE and multiply by 100 for the percentage
        final_percentage = (raw_score / MAX_SCORE ) * 100
        
        # Save it to the dictionary
        stats["final_score"] = final_percentage
        
        
    # --- 4. Print the Final Results ---
    print("===========================================")
    print(" FINAL LEADERBOARD RESULTS ")
    print("===========================================")
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1]['final_score'], reverse=True)
    for ai_model, scores in sorted_leaderboard.items():
        print(f"{ai_model}:")
        print(f"   Performance Score: {stats['final_score']:.2f}%   ")
        print(f"   Accepted: {stats['AC']} | WA: {stats['WA']} | CE: {stats['CE']}   ")
        print("-------------------------------------------")

if __name__ == "__main__":
    run_testbed()