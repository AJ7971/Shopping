"""Streamlit search and recommendation app for DummyJSON sample products."""

from __future__ import annotations

from typing import Any, Optional

import requests
import streamlit as st

PRODUCTS_URL = "https://dummyjson.com/products?limit=0"
MAX_RESULTS = 5


def fetch_products() -> list[dict[str, Any]]:
    """Fetch and validate the product collection from DummyJSON."""
    response = requests.get(PRODUCTS_URL, timeout=10)
    response.raise_for_status()
    payload = response.json()
    products = payload.get("products") if isinstance(payload, dict) else None
    if not isinstance(products, list) or any(not isinstance(p, dict) for p in products):
        raise ValueError("The product service returned an unexpected response.")
    return products


def _number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if number == number and abs(number) != float("inf") else None


def search_products(
    products: list[dict[str, Any]], keyword: str = "", *, max_price: Optional[float] = None,
    brand: str = "Any", category: str = "Any", min_rating: float = 0,
) -> list[dict[str, Any]]:
    """Apply mandatory conditions. Unknown values fail selected brand/category/rating constraints."""
    query = keyword.strip().casefold()
    if not query:
        return []
    result = []
    for product in products:
        title = product.get("title")
        price = _number(product.get("price"))
        if not isinstance(title, str) or query not in title.casefold() or price is None or price < 0:
            continue
        if max_price is not None and price > max_price:
            continue
        if brand != "Any" and product.get("brand") != brand:
            continue
        if category != "Any" and product.get("category") != category:
            continue
        rating = _number(product.get("rating"))
        if min_rating > 0 and (rating is None or rating < min_rating):
            continue
        result.append(product)
    return result


def rank_products(
    products: list[dict[str, Any]], *, price_weight: float = 0.5, rating_weight: float = 0.5,
    limit: int = MAX_RESULTS,
) -> list[dict[str, Any]]:
    """Score all eligible records using normalized price/rating; return top results with explanations."""
    if price_weight < 0 or rating_weight < 0 or abs(price_weight + rating_weight - 1) > 1e-9:
        raise ValueError("Ranking weights must be nonnegative and sum to 1.")
    candidates = []
    for p in products:
        price, rating = _number(p.get("price")), _number(p.get("rating"))
        if price is not None and price >= 0 and rating is not None:
            candidates.append((p, price, rating))
    if not candidates:
        return []
    prices = [item[1] for item in candidates]
    ratings = [item[2] for item in candidates]
    pmin, pmax, rmin, rmax = min(prices), max(prices), min(ratings), max(ratings)
    ranked = []
    for product, price, rating in candidates:
        price_score = 1.0 if pmax == pmin else 1 - (price - pmin) / (pmax - pmin)
        rating_score = 1.0 if rmax == rmin else (rating - rmin) / (rmax - rmin)
        score = price_weight * price_score + rating_weight * rating_score
        item = dict(product)
        item["recommendation_score"] = score
        item["recommendation_explanation"] = f"Balances price ({price_score:.2f}) and rating ({rating_score:.2f})."
        ranked.append(item)
    ranked.sort(key=lambda p: (-p["recommendation_score"], _number(p.get("price")), str(p.get("title", "")).casefold(), str(p.get("id", ""))))
    return ranked[:max(0, limit)]


def show_product(product: dict[str, Any], ranked: bool) -> None:
    image_url = product.get("thumbnail")
    title = product.get("title") or "Untitled product"
    price = float(product["price"])
    with st.container(border=True):
        columns = st.columns([1, 3]) if isinstance(image_url, str) and image_url.startswith(("https://", "http://")) else [st.container()]
        with columns[-1]:
            st.subheader(title)
            st.write(f"**Price:** ${price:,.2f}  ·  **Brand:** {product.get('brand') or 'Unknown'}  ·  **Rating:** {product.get('rating', 'Unknown')}")
            if ranked:
                st.write(f"**Recommendation score:** {product['recommendation_score']:.3f} — {product['recommendation_explanation']}")
        if len(columns) == 2:
            with columns[0]:
                st.image(image_url, width="stretch")


def main() -> None:
    st.set_page_config(page_title="Shopping Recommender", page_icon="🛍️")
    st.title("Shopping Recommender")
    st.caption("Sample product information from a dataset; these are not live retailer offers.")

    try:
        products = fetch_products()
    except requests.exceptions.JSONDecodeError:
        products = []
        st.error("The product service returned data that couldn't be read. Please try again.")
    except (requests.RequestException, ValueError):
        products = []
        st.error("Couldn't load product data. Please try again.")

    if products:
        brands = sorted({p["brand"] for p in products if isinstance(p.get("brand"), str) and p["brand"]})
        categories = sorted({p["category"] for p in products if isinstance(p.get("category"), str) and p["category"]})
    else:
        brands, categories = [], []

    with st.form("product-search"):
        keyword = st.text_input("Product keyword", placeholder="Try laptop, phone, or watch")
        c1, c2, c3 = st.columns(3)
        with c1:
            max_price = st.number_input("Maximum budget ($, 0 = no limit)", min_value=0.0, value=0.0, step=10.0)
            selected_brand = st.selectbox("Brand", ["Any", *brands])
        with c2:
            selected_category = st.selectbox("Category", ["Any", *categories])
            min_rating = st.slider("Minimum rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
        with c3:
            mode = st.radio("Sort mode", ["Lowest price (Stage 1)", "Weighted recommendations"])
            price_weight = st.slider("Price importance", 0.0, 1.0, 0.5, 0.05)
        ranking = mode == "Weighted recommendations"
        search = st.form_submit_button("Search", type="primary")

    if search:
        if not keyword.strip():
            st.info("Enter a product keyword to search.")
        elif not products:
            st.error("Product data is unavailable. Please retry after the service is available.")
        else:
            eligible = search_products(products, keyword, max_price=max_price or None, brand=selected_brand,
                                       category=selected_category, min_rating=min_rating)
            if ranking:
                results = rank_products(eligible, price_weight=price_weight, rating_weight=1 - price_weight)
            else:
                results = sorted(eligible, key=lambda p: (float(p["price"]), str(p.get("title", "")).casefold()))[:MAX_RESULTS]
            st.subheader(f"{'Recommendations' if ranking else 'Results'} for “{keyword.strip()}”")
            if not results:
                st.info("No products meet all selected conditions. Try a larger budget, lower minimum rating, or another brand/category.")
            else:
                st.caption(f"Showing up to {len(results)} eligible products, {'ranked by weighted score' if ranking else 'ordered by price'}.")
                for product in results:
                    show_product(product, ranking)


if __name__ == "__main__":
    main()
