import json

import pytest

import app
import shopping_agent as agent_tools


def item(title, price, rating, **extra):
    return {"title": title, "price": price, "rating": rating, **extra}


def test_search_tool_reuses_stage2_search(monkeypatch):
    products = [item("Phone A", 500, 4.5), item("Tablet B", 300, 4.8)]
    monkeypatch.setattr(app, "fetch_products", lambda: products)
    result = json.loads(agent_tools.search_products("phone"))
    assert result == [products[0]]


def test_filter_tool_applies_hard_constraints_and_unknowns_fail():
    products = [
        item("Phone A", 500, 4.5, brand="Acme", category="phones"),
        item("Phone B", 600, 4.0, brand="Acme", category="phones"),
        item("Phone C", 400, 4.8, category="phones"),
    ]
    filtered = json.loads(agent_tools.filter_products(
        json.dumps(products), "phone", max_price=600, brand="Acme", min_rating=4.0
    ))
    assert [product["title"] for product in filtered] == ["Phone A", "Phone B"]


def test_rank_tool_reuses_weighted_ranking():
    products = [item("Phone A", 500, 4.0), item("Phone B", 300, 4.8)]
    ranked = json.loads(agent_tools.rank_products(json.dumps(products), price_weight=0.5, limit=1))
    assert ranked[0]["title"] == "Phone B"
    assert ranked[0]["recommendation_score"] == pytest.approx(1.0)


def test_agent_registers_three_tools_without_model_call():
    if not agent_tools.SMOLAGENTS_AVAILABLE:
        pytest.skip("smolagents is not installed in this environment")
    class Model:
        pass

    agent = agent_tools.create_shopping_agent(Model())
    assert set(agent.tools) == {"search_products", "filter_products", "rank_products"}


def test_invalid_products_payload_is_rejected():
    with pytest.raises(ValueError, match="list of product objects"):
        agent_tools.filter_products('["not a product object"]', "phone")
