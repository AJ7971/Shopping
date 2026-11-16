import pytest

import app


def product(title, price, rating=4.0, brand="Acme", category="phones", **extra):
    return {"title": title, "price": price, "rating": rating, "brand": brand, "category": category, **extra}


def test_combined_constraints_and_inclusive_boundaries():
    products = [product("PHONE A", 100, 4.5), product("Phone B", 101, 5),
                product("Phone C", 100, 4.4, brand="Other"), product("case", 10)]
    got = app.search_products(products, " phone ", max_price=100, brand="Acme", category="phones", min_rating=4.5)
    assert [p["title"] for p in got] == ["PHONE A"]


def test_missing_required_attributes_fail_conservatively():
    products = [product("Phone valid", 10), {"title": "Phone unknown", "price": 2},
                product("Phone bad price", "free")]
    assert app.search_products(products, "phone", brand="Acme", min_rating=4) == [products[0]]


def test_stage_one_price_order_and_five_limit():
    products = [product(f"Phone {n}", 10 - n) for n in range(8)]
    got = app.search_products(products, "PHONE")
    stage_one = sorted(got, key=lambda p: (p["price"], p["title"].casefold()))[:app.MAX_RESULTS]
    assert len(stage_one) == 5
    assert [p["title"] for p in stage_one] == [f"Phone {n}" for n in range(7, 2, -1)]


def test_weighted_ranking_normalization_tie_break_and_limit():
    items = [product("Z Phone", 100, 5, id=2), product("A Phone", 100, 5, id=1), product("Cheap", 10, 1)]
    ranked = app.rank_products(items, price_weight=0.5, rating_weight=0.5, limit=5)
    assert [p["title"] for p in ranked] == ["Cheap", "A Phone", "Z Phone"]
    assert ranked[1]["recommendation_score"] == pytest.approx(0.5)
    assert "price" in ranked[1]["recommendation_explanation"]
    assert len(app.rank_products(items, limit=2)) == 2


def test_all_eligible_products_rank_before_top_five():
    items = [product(f"Phone {n}", 5 + n, 1 + n * 0.5) for n in range(8)]
    best = app.rank_products(items, price_weight=0, rating_weight=1)
    assert best[0]["title"] == "Phone 7"


def test_empty_and_no_match():
    assert app.search_products([product("Phone", 10)], "  ") == []
    assert app.search_products([product("Phone", 10)], "tablet") == []


def test_weight_validation():
    with pytest.raises(ValueError):
        app.rank_products([], price_weight=0.7, rating_weight=0.4)


def test_fetch_validates_api_shape_and_checks_status(monkeypatch):
    class Response:
        def raise_for_status(self): pass
        def json(self): return {"products": [{"title": "Phone"}]}
    monkeypatch.setattr(app.requests, "get", lambda *a, **kw: Response())
    assert app.fetch_products()[0]["title"] == "Phone"
    class Bad(Response):
        def json(self): return {"products": [1]}
    monkeypatch.setattr(app.requests, "get", lambda *a, **kw: Bad())
    with pytest.raises(ValueError): app.fetch_products()


def test_fetch_http_failure_propagates(monkeypatch):
    class Response:
        def raise_for_status(self): raise app.requests.HTTPError("bad status")
    monkeypatch.setattr(app.requests, "get", lambda *a, **kw: Response())
    with pytest.raises(app.requests.HTTPError): app.fetch_products()
