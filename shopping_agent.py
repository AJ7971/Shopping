"""smolagents tools and agent configuration for the Stage 2 recommender."""

from __future__ import annotations

import json
from typing import Any

try:
    from smolagents import ToolCallingAgent, tool
    SMOLAGENTS_AVAILABLE = True
except ImportError:  # Keep the offline wrapper tests usable before requirements are installed.
    ToolCallingAgent = None  # type: ignore[assignment,misc]
    SMOLAGENTS_AVAILABLE = False

    def tool(function):  # type: ignore[no-redef]
        """Allow direct offline invocation; requirements.txt provides the real decorator."""
        return function

import app


def _decode_products(products_json: str) -> list[dict[str, Any]]:
    """Decode the product list passed between tools, rejecting malformed input."""
    try:
        products = json.loads(products_json)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("products_json must be a JSON-encoded product list") from exc
    if not isinstance(products, list) or any(not isinstance(item, dict) for item in products):
        raise ValueError("products_json must contain a list of product objects")
    return products


@tool
def search_products(keyword: str) -> str:
    """Find sample products whose titles match a shopping keyword.

    Args:
        keyword: Non-empty word or phrase to find in product titles.
    """
    products = app.fetch_products()
    matches = app.search_products(products, keyword)
    return json.dumps(matches, ensure_ascii=False)


@tool
def filter_products(
    products_json: str,
    keyword: str,
    max_price: float = -1.0,
    brand: str = "Any",
    category: str = "Any",
    min_rating: float = 0.0,
) -> str:
    """Apply Stage 2 hard constraints to products returned by search_products.

    Args:
        products_json: JSON array returned by search_products.
        keyword: Original non-empty search phrase, reapplied with constraints.
        max_price: Maximum allowed price; use -1 for no budget limit.
        brand: Required brand, or "Any" when no brand is required.
        category: Required category, or "Any" when no category is required.
        min_rating: Minimum inclusive rating from 0 through 5.
    """
    products = _decode_products(products_json)
    eligible = app.search_products(
        products,
        keyword,
        max_price=max_price if max_price >= 0 else None,
        brand=brand,
        category=category,
        min_rating=min_rating,
    )
    return json.dumps(eligible, ensure_ascii=False)


@tool
def rank_products(
    products_json: str,
    price_weight: float = 0.5,
    limit: int = app.MAX_RESULTS,
) -> str:
    """Rank eligible products with the Stage 2 normalized weighted score.

    Args:
        products_json: JSON array returned by filter_products.
        price_weight: Price importance from 0 to 1; rating gets the remaining weight.
        limit: Maximum number of highest-scoring products to return.
    """
    products = _decode_products(products_json)
    ranked = app.rank_products(
        products, price_weight=price_weight, rating_weight=1 - price_weight, limit=limit
    )
    return json.dumps(ranked, ensure_ascii=False)


SHOPPING_TOOLS = [search_products, filter_products, rank_products]


def create_shopping_agent(model: Any) -> ToolCallingAgent:
    """Create a shopping agent using the supplied smolagents model.

    Args:
        model: Configured smolagents model. No model or API call is created here.
    """
    if ToolCallingAgent is None:
        raise RuntimeError("Install requirements.txt to configure the smolagents shopping agent.")
    return ToolCallingAgent(
        tools=SHOPPING_TOOLS,
        model=model,
        instructions=(
            "For shopping requests, search product titles first, then apply every requested "
            "hard constraint, then rank eligible records. Use only observed product fields. "
            "Recommend only returned records and explain using their price and rating. "
            "These records are sample dataset content, not live offers."
        ),
    )
