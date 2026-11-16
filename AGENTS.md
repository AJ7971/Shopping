# Project instructions

## Stage 2 shopping recommender

1. Use Python 3 and Streamlit for the web application.
2. Retrieve product records from the DummyJSON products API (`https://dummyjson.com/products`). Treat the API response as sample dataset content, not live retailer inventory or offers.
3. Apply the keyword, budget, brand, category, and minimum rating as hard constraints before ranking. Unknown values fail a selected attribute constraint; never invent specifications.
4. Preserve Stage 1's lowest-price mode (five cheapest). Weighted mode scores every eligible product using normalized price and rating, with nonnegative weights summing to 1, and returns up to five highest scores. Use deterministic tie-breaking.
5. Keep API access, filtering, and ranking in small, readable Python functions; keep Streamlit layout and rendering in `app.py`.
6. Handle empty queries, no matches, timeouts, HTTP errors, invalid JSON, and unexpected response shapes with useful messages. Do not expose stack traces.
7. Show title, price, brand, rating, image when available, and weighted score/explanation in ranked mode. Clearly label data as sample dataset content, not live offers.
8. Keep dependencies in `requirements.txt`. Run pytest for constraint boundaries, missing data, ranking, ties, no matches, API errors, and Stage 1 regression behavior.
