"""
data_generator.py – Programmatic generation of skewed synthetic transactions
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from config import DATA_PATH

def generate_transactions(num_total=100):
    transactions = []
    
    # Enforce strict distribution
    num_legit = int(num_total * 0.80)
    num_fraud = int(num_total * 0.10)
    num_escalate = num_total - num_legit - num_fraud
    
    start_time = datetime.now() - timedelta(days=30)
    
    merchants_legit = ["Starbucks", "Amazon", "Uber", "Target", "Whole Foods", "Netflix", "Local Grocery", "Shell Gas"]
    merchants_fraud = ["Crypto.com", "Unknown Electronics", "Luxury Watches Inc.", "Wire Transfer Intl", "GiftCards.com"]
    merchants_escalate = ["Best Buy", "Apple Store", "Delta Airlines", "Hotel Booking", "High-End Boutique"]
    
    # 1. Generate 80% Legitimate Data
    for _ in range(num_legit):
        amount = round(random.uniform(5, 150), 2)
        transactions.append({
            "transaction_id": f"TXN-LGT-{str(uuid.uuid4())[:6]}",
            "timestamp": (start_time + timedelta(minutes=random.randint(1, 40000))).isoformat() + "Z",
            "user_id": f"USER-{random.randint(1000, 9999)}",
            "amount": amount,
            "merchant": random.choice(merchants_legit),
            "merchant_category": "Everyday",
            "location": "New York, NY",
            "ip_address": f"192.168.1.{random.randint(1, 255)}",
            "device_id": f"DEV-{random.randint(100, 999)}",
            "is_cnp": random.choice([True, False]),
            "velocity_1h": random.randint(0, 1),
            "historical_avg_amount": round(amount * random.uniform(0.8, 1.2), 2),
            "ground_truth_label": "Legitimate",
            "ground_truth_risk_score": random.randint(1, 3),
            "notes": "Standard everyday spending patterns."
        })
        
    # 2. Generate 10% Fraud Data
    for _ in range(num_fraud):
        amount = round(random.uniform(800, 5000), 2)
        transactions.append({
            "transaction_id": f"TXN-FRD-{str(uuid.uuid4())[:6]}",
            "timestamp": (start_time + timedelta(minutes=random.randint(1, 40000))).isoformat() + "Z",
            "user_id": f"USER-{random.randint(1000, 9999)}",
            "amount": amount,
            "merchant": random.choice(merchants_fraud),
            "merchant_category": "High Risk",
            "location": "Lagos, Nigeria",
            "ip_address": f"41.190.2.{random.randint(1, 255)}",
            "device_id": "UNKNOWN_DEVICE",
            "is_cnp": True,
            "velocity_1h": random.randint(5, 15),
            "historical_avg_amount": round(random.uniform(20, 50), 2),
            "ground_truth_label": "Fraud",
            "ground_truth_risk_score": random.randint(9, 10),
            "notes": "Clear impossible travel, massive velocity spike, and unknown device."
        })
        
    # 3. Generate 10% Escalate Data (Ambiguous / Conflicting signals)
    for _ in range(num_escalate):
        amount = round(random.uniform(300, 1500), 2)
        transactions.append({
            "transaction_id": f"TXN-ESC-{str(uuid.uuid4())[:6]}",
            "timestamp": (start_time + timedelta(minutes=random.randint(1, 40000))).isoformat() + "Z",
            "user_id": f"USER-{random.randint(1000, 9999)}",
            "amount": amount,
            "merchant": random.choice(merchants_escalate),
            "merchant_category": "Electronics/Travel",
            "location": "New York, NY", 
            "ip_address": f"104.28.1.{random.randint(1, 255)}", # Anomalous IP (e.g. VPN)
            "device_id": f"DEV-{random.randint(100, 999)}", # BUT a recognized device
            "is_cnp": True,
            "velocity_1h": random.randint(2, 4),
            "historical_avg_amount": round(amount * random.uniform(0.1, 0.3), 2), 
            "ground_truth_label": "Escalate",
            "ground_truth_risk_score": random.randint(6, 8),
            "notes": "Ambiguous. Unusually high amount and anomalous IP, but originating from a trusted device."
        })
        
    # Shuffle the dataset so processing is mixed
    random.shuffle(transactions)
    
    with open(DATA_PATH, 'w') as f:
        json.dump(transactions, f, indent=4)
        
    print(f"✅ Generated {len(transactions)} transactions to {DATA_PATH}")
    print(f"   Distribution: {num_legit} Legitimate, {num_fraud} Fraud, {num_escalate} Escalate")

if __name__ == "__main__":
    generate_transactions()