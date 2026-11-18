# Stage 3 — Agentic Shopping Recommender

## Implementation

`shopping_agent.py` exposes three `smolagents` tools: `search_products`, `filter_products`, and `rank_products`. They reuse Stage 2’s `app.fetch_products`, `app.search_products`, and `app.rank_products` functions. Product records are passed between tool calls as JSON. `create_shopping_agent(model)` configures a `ToolCallingAgent` with all three tools and instructions to apply hard constraints before ranking and ground recommendations in returned product data.

## Function and agent tool explanation (128 words)

A Stage 2 function performs a defined operation when ordinary Python code calls it with arguments. An agent tool exposes that operation through a name, typed inputs, and a description that an LLM can read. The shopping agent can then choose a tool based on the request, inspect its returned product records, and call another tool with those observations. Here it searches titles, applies requested budget, brand, category, and rating constraints, then ranks the eligible records. The tools reuse `app.fetch_products`, `app.search_products`, and `app.rank_products`; they do not reimplement filtering or scoring. Product records move between tools as JSON so each tool call is self-contained. The agent is configured with all three tools, but this submission makes no paid model call. Offline tests invoke the tools directly and verify registration.

## Offline verification

- `python3 -m pytest -q` — 13 passed, 1 skipped. Wrapper tests exercised search, filtering, ranking, and malformed input.
- The agent-registration check was skipped because `smolagents` is absent from the environment. Installing it failed because the package index could not be reached. Install `requirements.txt` to run the registration test against the real library.
- Live agent execution was not run; the assignment makes it optional.
