# tests/test_tools.py
from tools import search_listings, suggest_outfit, create_fit_card


def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

''' tests for suggest_outfit '''
def test_suggest_outfit_empty_wardrobe():
    new_item = {"title": "Vintage Floral Dress"}
    outfit_suggestion = suggest_outfit(new_item, wardrobe={"items": []})
    assert isinstance(outfit_suggestion, str)
    assert len(outfit_suggestion) > 0
    
def test_suggest_outfit_missing_item():
    result = suggest_outfit({}, wardrobe={"items": ["baggy jeans"]})

    assert isinstance(result, str)
    assert len(result) > 0

def test_create_fit_card_empty_outfit():
    new_item = {
        "title": "Vintage Band Tee",
        "price": 22,
        "platform": "Depop"
    }

    result = create_fit_card("", new_item)

    assert isinstance(result, str)
    assert len(result) > 0


def test_create_fit_card_valid_input():
    outfit = "Pair the vintage band tee with baggy jeans and chunky sneakers for a relaxed 90s look."
    new_item = {
        "title": "Vintage Band Tee",
        "price": 22,
        "platform": "Depop"
    }

    result = create_fit_card(outfit, new_item)

    assert isinstance(result, str)
    assert len(result) > 0
    assert "tee" in result.lower() or "band" in result.lower()

