# WEEK 5 - Token Economics
## Cost and Rate-Limit Budgeting Before Building an LLM Feature

This project follows the uploaded **WEEK5_Token_Economics_Cost_and_Rate_Limit_Budgeting.docx** practical lab.

It creates a reusable Python planner that estimates:
- Input, output and total tokens per day
- Daily and 30-day estimated hosted API cost
- Peak requests per minute (RPM) with a safety margin
- Peak total tokens per minute (TPM) with a safety margin
- Daily and monthly budget checks
- A planning recommendation: within limits or revise before build

**Important:** This Week 5 practical is a pre-build budget planner. It does not need to call Ollama or another LLM. The configured prices and limits are illustrative placeholders and must be replaced with the current rate card and quota for the exact provider, model and service tier.

## Folder structure

```text
Week5_Token_Economics/
├── .env
├── budget.py
├── test_budget.py
├── requirements.txt
└── README.md
```

## 1. Open in VS Code

Extract the ZIP and open the `Week5_Token_Economics` folder in VS Code.

Open **Terminal > New Terminal**.

## 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the environment's Python directly in the install/run commands below.

## 3. Install the dependency

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you did not activate the environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. Review .env assumptions

The supplied `.env` contains the lab's illustrative example:
- Requests/day: 2,000
- Average input tokens/request: 1,200
- Average output tokens/request: 300
- Peak requests/minute: 30
- Input price per million tokens: $0.30
- Output price per million tokens: $1.20
- RPM limit: 60
- TPM limit: 100,000
- Monthly budget: $50
- Daily budget: $2
- Safety margin: 20%

These are sample planning values, not a live provider quote or verified quota.

## 5. Run the budget planner

```powershell
python budget.py
```

Expected sample figures (approximately):
- Input tokens/day: 2,400,000
- Output tokens/day: 600,000
- Total tokens/day: 3,000,000
- Daily estimated cost: $1.44
- 30-day estimated cost: $43.20
- Peak RPM with 20% margin: 36
- Peak total TPM with 20% margin: 54,000

With the handout's exact $50 monthly budget and a 20% safety margin, the monthly budget check correctly reports REVIEW: $43.20 × 1.20 = $51.84, which is above $50. The other three checks pass. This exposes a small inconsistency in the handout: its sample interpretation says the monthly budget passes, but its supplied formula applies the 20% margin to monthly cost. To make all four checks pass without changing the cost assumptions, raise `MONTHLY_BUDGET_USD` in `.env` to at least `51.84` (for example, `55`).

## 6. Run automated tests

```powershell
python -m unittest -v
```

The tests check cost calculations, token totals, RPM/TPM capacity, budget failures and negative input validation. They do not call an LLM API.

## 7. Formulas used

Let:
- R = expected requests per day
- I = average input tokens per request
- O = average output tokens per request
- Pi = input price per million tokens
- Po = output price per million tokens

```text
Input tokens/day  = R * I
Output tokens/day = R * O
Total tokens/day  = R * (I + O)

Daily cost = ((R * I * Pi) + (R * O * Po)) / 1,000,000
Monthly cost (30-day estimate) = Daily cost * 30

Peak RPM with margin = Peak RPM * (1 + margin/100)
Peak total TPM with margin = Peak RPM * (I + O) * (1 + margin/100)
```

This lab uses total TPM as a simplified planning check. Providers may enforce separate input/output limits, shared limits, or other quota dimensions; verify the selected provider's definition. Account for retries because retries may consume additional tokens and cost.

## 8. What-if analysis

Edit one value at a time in `.env`, save it, and run `python budget.py` again:
1. Double requests/day and compare daily/monthly cost.
2. Increase peak requests/minute until RPM or TPM needs review.
3. Increase input tokens/request to model longer context.
4. Reduce output tokens/request and observe the cost impact.
5. Increase model token prices and compare budget status.

## Security

The `.env` file contains planning assumptions, not API credentials. If you later add provider keys, keep them in `.env`, exclude `.env` from version control, and never publish secrets.

## Week 5 deliverable

A working, reusable token economics planner with cost estimates, rate-limit checks, safety margin, budget checks, automated tests and a go/no-go planning recommendation.
