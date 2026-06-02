"""
main.py – The core orchestrator for the pipeline
"""
import json
from database import init_db, save_investigation
from agents import investigate_transaction, evaluate_investigation
from config import DATA_PATH

def run_pipeline():
    init_db()

    try:
        with open(DATA_PATH, 'r') as f:
            transactions = json.load(f)
    except FileNotFoundError:
        print("❌ Data file not found. Please run 'python data_generator.py' first.")
        return

    print(f"🚀 Starting EDD Pipeline for {len(transactions)} transactions...")
    print(f"   Rate limit: 28 requests/min  |  2 calls/transaction  |  ~{len(transactions)*2} total calls\n")

    for txn in transactions:
        print(f"Processing {txn['transaction_id']}...")

        # Step 1: Frontline Agent  (call 1 of 2)
        investigation = investigate_transaction(txn)
        decision  = investigation.get('decision',  'Escalate')
        reasoning = investigation.get('reasoning', 'No reasoning provided.')

        # Step 2: EDD Auditor  (call 2 of 2)
        # No manual sleep needed — the rate limiter in agents.py handles pacing
        evaluation = evaluate_investigation(txn, decision, reasoning)

        # Step 3: Persist
        save_investigation({
            'transaction_id':    txn['transaction_id'],
            'ground_truth_label': txn['ground_truth_label'],
            'agent_decision':    decision,
            'agent_reasoning':   reasoning,
            **evaluation,
        })

        print(f"  ✅ Agent: {decision} | EDD Score: {evaluation['final_edd_score']}/100")

    print("\n🎉 Pipeline complete! Run:  streamlit run dashboard.py")

if __name__ == "__main__":
    run_pipeline()