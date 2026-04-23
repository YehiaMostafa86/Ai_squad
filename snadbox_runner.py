import subprocess
import time
import os

def evaluate_code(cpp_code, test_input, expected_output, time_limit=2.0):
    """
    Saves the AI's C++ code, compiles it, runs it against a test case, 
    and measures execution time.
    """
    file_name = "temp_solution.cpp"
    executable = "temp_solution.out" # Note: If you are on Windows, you might need to change this to "temp_solution.exe"

    # 1. Save the AI's raw code to a physical C++ file
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(cpp_code)

    # 2. Compile the code using g++
    # We use -O2 to optimize the code, exactly like real Codeforces servers do
    compile_process = subprocess.run(
        ["g++", "-O2", file_name, "-o", executable],
        capture_output=True, text=True
    )

    # If g++ throws an error, we catch it here
    if compile_process.returncode != 0:
        print(f"the wrong answer: {cpp_code}")
        return "Compile Error (CE)", 0.0

    # 3. Run the compiled program and start the stopwatch
    start_time = time.time()
    
    try:
        # We run the executable and feed it the 'test_input' exactly as if a human typed it
        run_process = subprocess.run(
            [f"./{executable}"], # Windows users: change to [f"{executable}"]
            input=test_input,        
            capture_output=True,
            text=True,
            timeout=time_limit       # The strict time limit cutoff
        )
        
        execution_time = time.time() - start_time
        actual_output = run_process.stdout.strip()
        print(f"Ai output{actual_output}")

        # 4. Grade the output against the answer key
        if actual_output == expected_output.strip():
            result = "Accepted"
        else:
            result = "Wrong Answer (WA)"
            
        return result, round(execution_time, 4)

    # Catch the timeout if the AI wrote an infinite loop or slow algorithm
    except subprocess.TimeoutExpired:
        return "Time Limit Exceeded (TLE)", time_limit
        
    finally:
        # 5. Clean up the workspace so we don't leave trash files everywhere
        if os.path.exists(file_name): os.remove(file_name)
        if os.path.exists(executable): os.remove(executable)


# --- Local Test to prove the Sandbox works ---
if __name__ == "__main__":
    
    print("Initializing C++ Sandbox Test...\n")
    
    # Let's pretend Llama 3 wrote this code
    perfect_code = """
    #include <iostream>
    using namespace std;
    int main() {
        int a, b;
        cin >> a >> b;
        cout << a + b << endl;
        return 0;
    }
    """
    
    # We feed it 5 and 7, we expect 12.
    test_case_in = "5 7\n"
    test_case_out = "12"
    
    print("Running Perfect Code:")
    grade, time_taken = evaluate_code(perfect_code, test_case_in, test_case_out)
    print(f"Result: {grade} | Time: {time_taken}s\n")
    
    # Let's pretend the AI wrote a bad program that prints the wrong math
    bad_code = """
    #include <iostream>
    using namespace std;
    int main() {
        int a, b;
        cin >> a >> b;
        cout << a * b << endl; // AI made a mistake and multiplied instead of added
        return 0;
    }
    """
    
    print("Running Bad Code:")
    grade_bad, time_taken_bad = evaluate_code(bad_code, test_case_in, test_case_out)
    print(f"Result: {grade_bad} | Time: {time_taken_bad}s\n")