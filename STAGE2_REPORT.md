# Stage 2 — Shopping Recommender

## Codex development log

This report records work from the current coding session; it is not a record of separate historical Codex runs.

1. **Constraints and attributes:** Extended the app with keyword, maximum price, brand, category, and rating conditions. Kept only attributes present in DummyJSON records; size/dimensions were not added because the dataset does not expose a consistent supported field. Missing values fail an active brand/category/rating requirement. Added tests for combined conditions, inclusive limits, missing fields, and invalid prices.
2. **Weighted ranking (`$product-ranking` workflow):** Added normalized price and rating scores, a price-weight slider with rating as the complementary weight, deterministic tie-breaking, score explanations, and ranking across all eligible records. Added tests for score calculation, ties, weight validation, and finding a high-rated item beyond a cheapest-first shortlist.
3. **Interface and integration:** Added selectors, recommendation mode, result metadata, no-match guidance, API shape/HTTP tests, and Stage 1 cheapest mode. UI behavior is now behind `main()` so tests can import pure functions without starting a network request.

## Skill comparison evidence

The assignment asks for two implementations of the same narrow task from the same starting state, with and without explicit skill invocation. That controlled comparison was not performed in this session, so there are no truthful comparative test results or observable differences to report. To complete this activity, repeat a narrowly scoped ranking task twice from the same commit/worktree snapshot, record each exact prompt and whether `$product-ranking` was invoked, then run the same focused pytest cases and compare results and code changes.

## Edge case and correction

The first test run caught an empty-keyword edge case: the filtering helper treated a blank keyword as matching every title. I changed it to return no results, consistent with the form asking users for a keyword, and the empty-query regression test now passes. The initial test expectations also clarified the tie rule: a cheap low-rated item can tie a high-priced high-rated item with equal weights, in which case lower price wins. The original Stage 1 module also executed its Streamlit page and fetched the API at import time; the page now runs only under `if __name__ == "__main__"`, allowing tests to import pure functions without network access.

## Reflection (190 words)

`AGENTS.md` gives Codex the project-wide contract: the source of product data, which filters are mandatory, what ranking means, and how failures should appear. The `product-ranking` skill turns that contract into a sequence of implementation and verification steps, including how to handle missing attributes and how to break score ties. These files improve consistency, but they do not establish that the implementation is correct. Human supervision remains necessary: I reviewed the dataset’s available fields and left dimensions out rather than inventing support, and I kept Stage 1’s cheapest-results behavior as a separate mode. The initial pytest run caught a blank-keyword bug in the filtering helper and exposed an incorrect assumption in a tie-order assertion; both were corrected, then the full suite passed. Moving page execution under `main()` also made the logic testable without a live service. The tests cover boundaries, missing values, ranking, ties, API failures, and Stage 1 behavior. I did not perform the requested same-state comparison of Codex with and without explicit skill invocation, so that remains an evidence gap. One limitation is that normalized scores depend on the current eligible result set: the same product can receive a different score when search conditions change. A production recommender might instead use stable business-defined score ranges or richer user preferences.

## Verification status

- Automated: `python3 -m pytest -q` — 9 passed at the time of the Stage 2 report. One environment warning reports that urllib3 is using LibreSSL rather than OpenSSL; it does not affect the mocked tests.
- Live Streamlit multi-condition check and screenshot: not captured in that Stage 2 session.
- Controlled skill comparison: not performed; see above.
