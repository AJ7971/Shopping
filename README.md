# Shopping Recommender — Stage 2

The Streamlit app uses the DummyJSON products endpoint as sample dataset content. It supports keyword, budget, brand, category, and minimum rating constraints. Choose **Lowest price (Stage 1)** to see up to five cheapest eligible records, or **Weighted recommendations** to score every eligible record on normalized price and rating. The weight slider controls price importance; rating receives the remaining weight. Brand/category/rating constraints exclude records with missing required attributes.

## Run

```bash
python3 -m pip install -r requirements.txt
streamlit run app.py
```

## Verify

```bash
python3 -m pytest -q
```

Tests mock the service and cover combined constraints and inclusive boundaries, missing attributes, invalid prices, both ranking behavior and Stage 1 ordering/limit, ties, no matches, weight validation, response shape, and HTTP failures. For a live UI check, run the app and submit a multi-condition query such as keyword `phone`, a budget, and a rating threshold. Confirm the app can rank a product outside the five cheapest eligible records.

## Submission items

- Agent rules: `AGENTS.md`
- Ranking skill: `.agents/skills/product-ranking/SKILL.md` (the original product-search skill remains in `.agents/skills/product-search/`)
- Source and mocked tests: `app.py`, `tests/`
- Development notes and reflection: `SUBMISSION_REPORT.md`

Before submitting, capture a screenshot from the running app with several selected conditions and actual result cards. The controlled comparison of Codex with and without explicit skill invocation also remains to be completed; see `SUBMISSION_REPORT.md`.
