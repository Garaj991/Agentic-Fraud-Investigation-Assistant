Agentic Fraud Investigation & Automated EDD Pipeline

An AI-driven pipeline designed to evaluate financial transactions using an automated Enhanced Due Diligence (EDD) system with strict rate-limiting controls.

Setup Instructions

Clone the repository

Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt


Configure your Environment Variables:
Create a .env file in the root directory:

GROQ_API_KEY=your_groq_api_key_here
FRAUD_AGENT_MODEL=llama-3.3-70b-versatile
EDD_EVALUATOR_MODEL=llama-3.3-70b-versatile


Generate data and run pipeline:

python data_generator.py
python main.py
