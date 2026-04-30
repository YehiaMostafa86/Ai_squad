import streamlit as st
import time
import pandas as pd

# Import your existing backend functions!
from database_loader import fetch_real_problems
from llm_client import ask_ai_to_code
from snadbox_runner import evaluate_code

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Algorithmic Judge", page_icon="⚖️", layout="wide")
MODELS_TO_TEST = ["llama-3.3-70b-versatile", "groq/compound-mini", "openai/gpt-oss-120b"]

# --- UI HEADER ---
st.title("🏆 Kisméretű modellek tesztpaddja")
st.subheader("Testbed for Small AI Models")
st.markdown("---")

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    num_problems = st.slider("Number of problems to fetch:", 1, 30, 3)
    start_button = st.button("🚀 Run AI Benchmark", use_container_width=True)

# --- MAIN EXECUTION LOGIC ---
if start_button:
    # 1. Fetch Data
    with st.spinner("Fetching live algorithmic problems..."):
        PROBLEMS = fetch_real_problems(num_problems)
    st.success(f"Successfully loaded {len(PROBLEMS)} problems!")

    # 2. Setup Leaderboard
    MAX_RAW_SCORE = (0.1 * 20) ** -1
    leaderboard = {model: {"AC": 0, "WA": 0, "CE": 0, "sum_weighted_time": 0.0} for model in MODELS_TO_TEST}

    # 3. Create UI Containers for live updates
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 4. The Main Loop
    for i, problem in enumerate(PROBLEMS):
        st.markdown(f"### 📝 Problem {problem['id']}: {problem['title']} (Diff: {problem['difficulty']})")
        
        # Create an expander so users can read the problem description!
        with st.expander("View Problem Description"):
            st.write(problem['description'])
            st.code(f"Input: {problem['test_input']}\nExpected: {problem['expected_output']}", language="text")

        # Create columns so AI results sit side-by-side
        cols = st.columns(len(MODELS_TO_TEST))

        for j, ai_model in enumerate(MODELS_TO_TEST):
            with cols[j]:
                st.markdown(f"**🤖 {ai_model}**")
                status_text.text(f"Running {ai_model} on Problem {problem['id']}...")
                
                # Fetch Code
                ai_code = ask_ai_to_code(ai_model, problem['description'])
                
                # Show the code the AI wrote inside a collapsible box!
                with st.expander("Show C++ Code"):
                    st.code(ai_code, language="cpp")

                # Evaluate Code
                result, execution_time = evaluate_code(ai_code, problem['test_input'], problem['expected_output'])
                
                # Color code the results
                if result == "Accepted":
                    st.success(f"✅ {result} ({execution_time}s)")
                    leaderboard[ai_model]["AC"] += 1
                    actual_time = execution_time
                elif result == "Wrong Answer":
                    st.error(f"❌ {result}")
                    leaderboard[ai_model]["WA"] += 1
                    actual_time = 2.0
                else:
                    st.warning(f"⚠️ {result}")
                    leaderboard[ai_model]["CE"] += 1
                    actual_time = 2.0
                
                leaderboard[ai_model]["sum_weighted_time"] += (actual_time * problem['difficulty'])

        # Update progress bar
        progress_bar.progress((i + 1) / len(PROBLEMS))
        time.sleep(2) # Small cooldown between questions

    status_text.text("Benchmark Complete!")
    st.balloons() # Fun animation for finishing!

    # --- FINAL LEADERBOARD CALCULATION ---
    st.markdown("---")
    st.header("🏅 Final Leaderboard")
    
    leaderboard_data = []
    for model_name, stats in leaderboard.items():
        avg_weighted_time = stats["sum_weighted_time"] / len(PROBLEMS) if stats["sum_weighted_time"] > 0 else 0.001
        final_score = ((avg_weighted_time ** -1) / MAX_RAW_SCORE) * 100
        
        leaderboard_data.append({
            "AI Model": model_name,
            "Final Score (%)": round(final_score, 2),
            "Accepted ✅": stats["AC"],
            "Wrong Answer ❌": stats["WA"],
            "Compile Error ⚠️": stats["CE"]
        })

    # Convert to Pandas DataFrame to make it a beautiful table
    df = pd.DataFrame(leaderboard_data).sort_values(by="Final Score (%)", ascending=False)
    
    # Display the table beautifully
    st.dataframe(df, use_container_width=True)