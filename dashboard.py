"""
dashboard.py – Streamlit UI to visualize investigations
"""
import streamlit as st
import sqlite3
import pandas as pd
from config import DB_PATH

st.set_page_config(page_title="EDD Fraud Dashboard", layout="wide")
st.title("🛡️ Agentic Fraud Investigation & EDD Dashboard")

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM investigations", conn)
    conn.close()
    return df

df = load_data()

if not df.empty:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Investigations Processed", len(df))
    col2.metric("Average EDD Score", f"{round(df['final_edd_score'].mean(), 1)} / 100")
    
    # Calculate accuracy against ground truth
    matches = len(df[df['agent_decision'] == df['ground_truth_label']])
    accuracy = (matches / len(df)) * 100
    col3.metric("Agent Accuracy vs Ground Truth", f"{round(accuracy, 1)}%")

    st.subheader("Transaction Log")
    
    # Styling to highlight failed verdicts
    def highlight_discrepancies(row):
        if row['agent_decision'] != row['ground_truth_label']:
            return ['background-color: #ffcccc'] * len(row)
        return [''] * len(row)

    st.dataframe(df.style.apply(highlight_discrepancies, axis=1), use_container_width=True)
else:
    st.info("No investigations found. Please run `python main.py` to process transactions.")