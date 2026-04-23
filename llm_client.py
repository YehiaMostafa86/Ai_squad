import os
import re
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

# --- EXPLANATION 1: The Connection ---
# This line creates the "bridge" between your laptop and Groq's LPU servers.
# For right now, you can paste your actual API key directly inside the quotes. 
# (Note: Before you upload this to GitHub later, we will hide this key so it doesn't get stolen!)
client = Groq(api_key=os.getenv("groq_api")) # add your api from https://console.groq.com/keys

def sanitize_code(raw_text):
    """Strips markdown code blocks from the AI's output."""
    text = raw_text.strip()
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    # If the AI started with ```cpp or ```c++
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] # Remove that first line entirely
        
    # If the AI ended with ```
    if text.endswith("```"):
        text = text[:-3] # Remove the last 3 characters
        
    return text.strip()

def ask_ai_to_code(model_name, problem_description):
    """
    Takes a coding problem, sends it to the AI, and returns only the C++ code.
    """
    
    # --- EXPLANATION 2: The System Prompt ---
    # AI models are naturally chatty. They want to say "Here is your code!"
    # In a testbed, chatty text will cause a Compile Error (CE) when we pass it to g++.
    # This system prompt acts as a strict rule forcing the AI to act like a machine, not a chatbot.
    system_prompt = (
        
        "You are an expert competitive programmer. "
        "Solve the following problem using C++. "
        "Output ONLY the raw, compilable C++ code. "
        "Do not include any explanations, markdown formatting (like ```cpp), or comments."
        "Don't write anything excpet the answer"
        "answer with a c++ code only if you could not write [N/A]"
        "don't include emojis"
        
    )

    print(f"Connecting to {model_name}...")

    # --- EXPLANATION 3: The API Call ---
    # This is where the actual request happens. We send a package to Groq containing
    # the rules (system) and the actual problem (user).
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": problem_description}
        ],
        # Temperature controls creativity. 
        # 1.0 = highly creative (good for writing poems). 
        # 0.0 = completely deterministic and strict (mandatory for writing C++ logic).
        temperature=0.0, 
    )
    
    # --- EXPLANATION 4: The Return ---
    # The API sends back a massive JSON object with tons of data (token count, time taken, etc.).
    # We navigate through that JSON to extract strictly the text message the AI wrote.
    
    raw_data = response.choices[0].message.content
    
    return sanitize_code(raw_data)


# --- EXPLANATION 5: The Local Test ---
# This block only runs if you run this specific file directly. 
# It is a great way to test the function without running the whole project.
if __name__ == "__main__":
    
    # A classic, simple competitive programming problem
    test_problem = "Read two integers from standard input and print their sum to standard output."
    
    # We are calling our function using Llama 3.1 (8 Billion parameters)
    print("Testing API Connection...")
    ai_code = ask_ai_to_code("qwen/qwen3-32b", test_problem)
    
    print("\n--- The AI Wrote: ---")
    print(ai_code)