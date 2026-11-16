---
name: product-ranking
description: Implement and verify deterministic hard-constraint filtering and weighted recommendations for the DummyJSON Streamlit shopping app.
---

# Product ranking workflow

1. Inspect `AGENTS.md` and current code before editing. Keep DummyJSON records as sample data and do not fabricate attributes.
2. Fetch with a finite timeout, check HTTP status, decode JSON, and validate the `products` list. Translate failures into concise interface messages.
3. Normalize only supported numeric values. Apply keyword, maximum price, brand, category, and minimum rating as hard eligibility conditions before ranking. Unknown values fail a selected required condition. Do not infer size/dimensions unless the dataset provides a real usable field.
4. Preserve Stage 1's five lowest-price search mode. For recommendations, normalize price and rating among all eligible products, apply configurable nonnegative weights summing to one, and sort deterministically by score then documented tie-breakers.
5. Show product title, price, brand, rating, available image, score and a short explanation. Explain no-match outcomes and offer constraint changes without relaxing any condition.
6. Add pytest cases using mocked API responses for combined filters, inclusive boundaries, missing/invalid values, normalized scores, ties, no matches, API errors, and Stage 1 regression.
7. Run pytest and make a focused Streamlit check with real API data when available. Record unavailable checks rather than claiming they passed.

## Verification notes

Price is normalized so lower prices score higher; rating is normalized so higher ratings score higher. When a dimension has equal values, all candidates receive 1.0 on that dimension. Ties are resolved by lower numeric price, title, then product id.
