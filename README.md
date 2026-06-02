```
# Agentic Fraud Investigation & Automated EDD Pipeline

An AI-driven transaction monitoring pipeline engineered to evaluate financial risks using an automated, multi-agent Enhanced Due Diligence (EDD) framework. The system operates under strict sliding-window rate-limiting constraints to align with free-tier API parameters while ensuring production-grade error handling and persistent logging.

## Core Features

* Multi-Agent Workflow: Utilizes a frontline Fraud Investigator agent to classify incoming transaction hazards and an independent EDD Compliance Auditor agent to score reasoning validity.
* Sliding-Window Rate Limiter: Features a precise, custom-built collections.deque mechanism capping calls strictly at 28 requests per minute (RPM) with sub-second safety margins.
* Deterministic Persistence: Commits structural execution histories, pipeline classifications, evaluation scores, and audit justifications to an ACID-compliant local SQLite database.
* Dynamic Data Simulation: Bundles a customizable generation pipeline pre-configured with 50 unique historical test cases covering structural risk paradigms (e.g., impossible travel, account takeovers, velocity spikes, and card testing).

---

## Technical Architecture & File Structures

* config.py: Acts as the central configuration engine. Manages file system paths, loads credentials from runtime environments, configures weighted validation metrics, and defines operational rate limits.
* database.py: Orchestrates database initializations, schema provisioning, and atomic record upserts to protect pipeline histories.
* agents.py: Contains the multi-agent LLM logic, sliding-window pacing throttles, and structured JSON parsing layers.
* data_generator.py: Provisions the local database with deterministic fraud evaluation data across 10 independent distribution channels.
* main.py: Drives execution flow by loading data payloads, querying internal agent engines sequentially, and pushing audited summaries down to persistent states.

---

## Local Setup & Installation

### 1. Provision Local Workspace
Clone this repository to your local runtime environment and navigate to the project root directory:

    cd ~/fraud_ai_edd

### 2. Configure Virtual Environment & Dependencies
Initialize an isolated virtual workspace and install all explicit library dependencies:

    # Initialize workspace environment
    python -m venv venv

    # Activate environment (Linux/macOS)
    source venv/bin/activate

    # Alternative activation (Windows Command Prompt)
    # venv\Scripts\activate

    # Install critical pipeline requirements
    pip install groq python-dotenv

### 3. Establish Runtime Environment Variables
Construct a custom .env file within your root repository path to expose secure variables to the application layer:

    GROQ_API_KEY=your_actual_groq_api_key_here
    FRAUD_AGENT_MODEL=llama-3.3-70b-versatile
    EDD_EVALUATOR_MODEL=llama-3.3-70b-versatile
    DB_PATH=fraud_investigation.db
    DATA_PATH=synthetic_transactions.json

---

## Execution Instructions

### Step 1: Synthesize High-Fidelity Datasets
Before running your pipeline, trigger the target generation script to compile your baseline evaluation matrix:

    python data_generator.py

### Step 2: Initialize Core Pipeline Processes
Launch the automated orchestration layer to run transaction investigations and audit evaluations concurrently:

    python main.py

---

## Production Safeguards & Compliance Data Protection

To avoid accidental exposure of structural environment configurations and security definitions, this workspace implements an explicit .gitignore deployment layout.

The following assets are strictly bounded from upstream Git commits:
* Local configuration environments (.env)
* Local application database files (*.db)
* Intermediate runtime payloads (synthetic_transactions.json)
* Python execution caching nodes (__pycache__/, *.pyc)

```
