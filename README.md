# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.

## Tool Inventory

### 1. `load_listings`

**Inputs:**  
None

**Outputs:**  
`listings: list[dict]`

**Purpose:**  
Loads the mock secondhand listings from `data/listings.json` so the agent can search available items.

---

### 2. `search_listings`

**Purpose:**
Searches the mock secondhand listings dataset for clothing items that match the user's request.

**Inputs:**

`description (str)`: Keywords describing the item the user wants, such as "vintage graphic tee"

`size (str | None)`: Optional size filter. If None, the search does not filter by size.

`max_price (float | None)`: Optional price ceiling. If None, the search does not filter by price.

**Output:**
Returns a list of matching listing dictionaries sorted by relevance. Each listing contains fields such as id, title, description, category, style_tags, size, condition, price, colors, brand, and platform.

**Error handling:**
If no listings match, the tool returns an empty list instead of throwing an error.

---


### 3. `suggest_outfit`

**Purpose:**
Suggests how to style the selected thrifted item using the user's wardrobe.

**Inputs:**

`new_item (dict)`: The listing selected from search_listings.

`wardrobe (dict)`: The user's wardrobe, including an items list.

**Output:**
Returns a non-empty outfit suggestion string. If the wardrobe has items, the suggestion tries to pair the new item with specific wardrobe pieces. If the wardrobe is empty, it gives more general styling advice.

**Error handling:**
If new_item is missing or invalid, the tool returns a message saying it needs a valid listing first. If the LLM call fails, it returns a fallback styling suggestion instead of crashing

---

### 4. `create_fit_card`

**Purpose:**
Turns the outfit suggestion into a short, casual fit-card caption.

**Inputs:**

`outfit (str)`: The outfit suggestion returned by suggest_outfit

`new_item (dict)`: The selected listing from search_listings

**Output:**
Returns a short caption-style string that mentions the item, price/platform when available, and the overall outfit vibe.

**Error handling:**
If the outfit string is empty or missing, the tool returns a message explaining that no outfit suggestion was provided. If item details are missing, it returns a message saying it needs a valid item first

## Planning Loop Explanation

The agent starts by creating a new session dict to track the query, parsed search parameters, search results, selected item, wardrobe, outfit suggestion, fit card, and any error. It then parses the user query into description, size, and max_price.

Next, the agent calls search_listings(description, size, max_price). If the returned results list is empty, the agent sets `session["error"]`, leaves `session["fit_card"]` as None, and returns early without calling `suggest_outfit` or `create_fit_card.`

If search results exist, the agent sets session["selected_item"] to be the top result. It then calls `suggest_outfit(selected_item, wardrobe)` and saves the result in session["outfit_suggestion"]. Finally, it calls `create_fit_card(outfit_suggestion, selected_item)`, stores the result in session["fit_card"], and returns the completed session.


## State Management Approach

The agent stores intermediate results in a shared `session` dictionary. This helps each step pass information clearly to the next step.

Example session structure:

```python
session = {
    "user_request": "find me a vintage grunge top",
    "listings": [...],
    "search_results": [...],
    "selected_item": {...},
    "outfit_suggestion": {...},
    "fit_card": "...",
    "error": None
}
```

The key state transitions are:

- `user_request` is saved at the beginning.
- `search_results` stores the listings returned from the search tool.
- `selected_item` stores the listing chosen for the recommendation.
- `outfit_suggestion` stores the output from the styling tool.
- `fit_card` stores the final response
- `error` stores a user-facing error message if the agent cannot complete the task

I verified state flow by printing the selected item before `suggest_outfit()` and the outfit suggestion before `create_fit_card()`. The selected item returned from search was the same dictionary passed into the outfit tool, and the outfit suggestion returned from `suggest_outfit `was the same text passed into create_fit_card.

## Error Handling

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Returns an empty list. The planning loop sets session["error"] to a helpful message and returns early without calling the other tools. Example tested: "designer ballgown size XXS under $5" returned "no listings found..." and stopped the flow. |
| suggest_outfit | Wardrobe is empty | Returns general styling advice for the selected item. Example tested: passing {"items": []} still returned a non-empty suggestion. |
| create_fit_card | Outfit input is missing or incomplete | Returns a message explaining that no outfit suggestion was provided instead of raising an exception. Example tested: create_fit_card("", new_item) returned an informative fallback message. |

## Spec Reflection

One way the spec helped was that it made the tool order very clear before I started writing code/asking LLM to implement them. Since I had already written out the inputs, outputs, and failure modes for each tool, it was easier to check whether the implementation actually matched the intended behavior.

One instance my implementation diverged from the original spec was the search scoring. My first version returned a vintage knit vest for a “vintage graphic tee” query because it matched broad words like “vintage” and “tops.” I adjusted the search scoring to better prioritize more specific matches in the title and style tags so that graphic tee results (e.g Graphic Tee — 2003 Tour Bootleg Style) ranked higher.

## AI Usage

### Instance 1
  
**What I gave the AI:**
I gave Claude my Tool 1, Tool 2, and Tool 3 specs from planning.md, including the input parameters, return values, and failure modes.

**What it produced:**  
Claude helped draft the first versions of `search_listings`, `suggest_outfit`, and `create_fit_card`.

**What I changed or overrode:**  
I reviewed the generated code against my spec and changed parts that were too generic. For example, I improved `search_listings` so it weighted title and style-tag matches more heavily instead of treating every keyword equally. I also added fallback behavior so the outfit tool would return a useful message if the LLM call failed.

### Instance 2

**What I gave the AI:**
I gave Claude my Architecture diagram, Planning Loop section, State Management section, and Error Handling table.

**What it produced:**  
Claude helped generate the planning loop structure in agent.py, including creating a session dictionary, parsing the query, calling the tools in order, and storing results in session state.

**What I changed or overrode:**  
I made sure the no-results branch returned early after search_listings returned an empty list. At first, the later tools were still being called even when there were no listings from a minior bug, so I fixed the control flow to stop before `suggest_outfit.`

### Instance 3

**What I gave the AI:**
I gave Claude my completed `handle_query()` implementation and asked it to review the logic for the Gradio handler including how the session dictionary was mapped to the listing, outfit suggestion, and fit card output panels.

**What it produced:**
Claude reviewed the implementation and suggested a few small improvements related to output formatting and edge-case handling.

**What I changed or overrode:**
I adjusted the implementation, specifically output formatting so the selected listing displayed in a more readable way and added an early return for empty user queries