# Stage 1 — Product Search

## Scope

Stage 1 provides keyword search over products from the DummyJSON products API. Results are sample dataset content, not live retailer inventory or offers. The lowest-price mode returns up to five matching products, ordered by ascending price with title as a deterministic tie-breaker.

## Current implementation

The Stage 1 behavior remains available in the Streamlit app as **Lowest price (Stage 1)**. It uses the shared product fetch and search functions, then sorts eligible matches by price and title before limiting the list to five.

## Verification

The Stage 1 regression test in `tests/test_app.py` checks price ordering and the five-result limit. It passes as part of the complete test suite. The current app also displays title, price, brand, rating, and an image when available.

This report summarizes the Stage 1 behavior preserved by the current project; a separate historical Stage 1 development log was not available in the project files.
