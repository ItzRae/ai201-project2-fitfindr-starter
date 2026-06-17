"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()

    # Filter by price and size
    filtered = []
    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue
        if size is not None and size.lower() not in listing["size"].lower():
            continue
        filtered.append(listing)

    # Score by keyword overlap with description
    keywords = set(description.lower().split())

    def score(listing: dict) -> int:
        # Weight fields by specificity — title matches matter most
        fields = [
            (listing.get("title", ""), 3),
            (listing.get("category", ""), 2),
            (" ".join(listing.get("style_tags", [])), 2),
            (listing.get("description", ""), 1),
            (" ".join(listing.get("colors", [])), 1),
            (listing.get("brand", "") or "", 1),
        ]

        total = 0
        for text, weight in fields:
            text_lower = text.lower()
            total += sum(weight for kw in keywords if kw in text_lower)
        return total

    scored = [(score(listing), listing) for listing in filtered]
    results = [listing for s, listing in sorted(scored, key=lambda x: -x[0]) if s > 0]

    return results


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    
    if not new_item:
        return "I need a valid listing before I can suggest an outfit. Try searching for an item first."

    client = _get_groq_client()
    item_summary = (
        f"Title: {new_item.get('title', 'Unknown')}\n"
        f"Category: {new_item.get('category', 'Unknown')}\n"
        f"Colors: {', '.join(new_item.get('colors', []))}\n"
        f"Style tags: {', '.join(new_item.get('style_tags', []))}\n"
        f"Brand: {new_item.get('brand') or 'Unbranded'}\n"
        f"Condition: {new_item.get('condition', 'Unknown')}\n"
        f"Price: ${new_item.get('price', '?')}"
    )

    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        prompt = f"""A user is considering buying this thrifted item:

        {item_summary}

        They haven't shared their wardrobe yet. Give them 1–2 general outfit ideas: 
        what types of pieces pair well with this item, what aesthetic or vibe it suits, 
        and any styling tips. Be specific and practical."""

    else:
        wardrobe_summary = "\n".join(
            f"- {item.get('title', 'Unknown')} ({item.get('category', '?')}, {', '.join(item.get('colors', []))})"
            for item in wardrobe_items
        )
        prompt = f"""A user is considering buying this thrifted item:

        {item_summary}

        Here are pieces already in their wardrobe:
        {wardrobe_summary}

        Suggest 1–2 complete outfits using the new item paired with specific pieces 
        from their wardrobe. Name the wardrobe pieces you're pairing, explain why 
        they work together, and describe the overall vibe of each outfit."""

    try:
        response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # or whatever model you're using
                messages=[
                    {"role": "system", "content": "You are a helpful fashion styling assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
        
        return response.choices[0].message.content

    except Exception:
        return (
            f"I couldn't generate a personalized outfit right now, but "
            f"{new_item.get('title', 'this item')} would pair well with simple basics "
            f"like jeans, sneakers, or a lightweight jacket."
        )
    
    


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    if not outfit or not outfit.strip():
        return "Couldn't create a fit card — no outfit suggestion was provided. Try running suggest_outfit first."

    if not new_item:
        return "Couldn't create a fit card — no item details were provided. Try searching for an item first."

    client = _get_groq_client()

    title = new_item.get("title", "this thrifted find")
    price = new_item.get("price")
    platform = new_item.get("platform", "a resale app")
    price_str = f"${price:.2f}" if price is not None else None

    item_line = f"Item: {title}"
    if price_str:
        item_line += f" — {price_str} on {platform}"
    else:
        item_line += f" (found on {platform})"

    prompt = f"""You're writing an Instagram/TikTok OOTD caption for a thrifted outfit. Keep it 2–4 sentences.

    {item_line}

    Outfit idea:
    {outfit}

    Guidelines:
    - Sound like a real person posting their fit, not a brand ad
    - Mention the item name, price, and platform once each (naturally woven in)
    - Capture the specific vibe of the outfit (don't just say "cute" or "stylish")
    - Each caption should feel fresh — avoid generic openers like "Obsessed with..."

    Write only the caption, no hashtags, no labels."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You write short, punchy OOTD captions for thrift finds. "
                    "Your tone is casual, specific, and genuinely enthusiastic — "
                    "never salesy or generic."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=1.1,
    )

    return response.choices[0].message.content.strip()
