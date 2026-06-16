# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Searches the available resale clothing listings for items that match the user’s request, including the item description, size, and maximum price. The agent should call this first whenever the user asks to find a clothing item.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): The type of item the user is looking for (e.g black mini skirt)
- `size` (str): The requested clothing size (e.g "S", "M", "8")
- `max_price` (float): the highest price the user is willing to pay

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
A list of matching listing dictionaries sorted by relevance. Each result should include fields such as item name/title, price, size, platform or seller source, condition, and any style/category tags available in the listing data.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
the agent should stop the flow and tell the user that no matching items were found. It should suggest broadening the search, using a less specific description, or raising the price limit. It should not call suggest_outfit without a selected listing.

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Takes the new clothing item selected from the search results and suggests how to style it with pieces from the user’s wardrobe. The agent should call this only after a listing has been found.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): The selected listing from search_listings, including item name/title, price, platform, and condition
- `wardrobe` (dict): The user’s existing wardrobe data, such as tops, bottoms, shoes, outerwear, accessories, and style preferences.

**What it returns:**
<!-- Describe the return value -->

An outfit suggestion describing which wardrobe items to pair with the new item and why they work together. The return should include the selected new item, recommended wardrobe pieces, styling notes, and an overall outfit vibe or aesthetic.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
The agent should still give a general styling suggestion using the new item, but it should clearly say that it could not personalize the outfit based on wardrobe items. 
If the new_item is missing or invalid, the agent should stop and explain that it needs a valid listing first.

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Turns the outfit suggestion into a polished and short fit card or caption that the user could post or save. The agent should call this after an outfit has been successfully suggested.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): The outfit recommendation returned by suggest_outfit, including the new item, wardrobe pieces, styling notes, and overall vibe

**What it returns:**
<!-- Describe the return value -->
A short fit card string that summarizes the new item and styling idea in a casual voice. It should mention the item, price/platform when available, and the main styling idea.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->

If the outfit data is incomplete, the agent should return a simpler summary using whatever information is available, like the item name and one basic styling suggestion. If there is no valid outfit/new item, the agent should not create a fit card and should explain that it needs a completed outfit suggestion first.


---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

Start by extracting the item description, size, and max price from the user's request. Call search_listings() with those values.

After search_listings() runs, check if results is empty. If it is, return an error message suggesting the user broaden their search and stop. If it is not, set selected_item = results[0].

Next, call suggest_outfit(new_item=selected_item, wardrobe=wardrobe). If the wardrobe is empty, return a general styling suggestion using the selected item. Otherwise, return a personalized outfit recommendation.

Finally, call create_fit_card(outfit=outfit, new_item=selected_item). Return the selected listing, outfit suggestion, and fit card to the user. The agent is finished once either no search results are found or the fit card has been successfully generated.


---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

Information is passed between tools through a simple session state dictionary - after `search_listings()` runs, the agent saves the search results and selected item (usually `selected_item = results[0]`). That selected item is then passed into `suggest_outfit()` along with the user’s wardrobe. After that returns, the outfit suggestion is saved in state and passed into `create_fit_card()` with the selected item. The main pieces of state are the original user request, search filters, search results, selected item, wardrobe, outfit suggestion, fit card, and any error message.


---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Tell the user no matching listings were found, suggest broadening the search, changing the size, or increasing the budget, and stop before calling the other tools |
| suggest_outfit | Wardrobe is empty | Give a general styling suggestion for the selected item instead of a personalized wardrobe-based outfit, and clearly say the suggestion is not based on saved wardrobe items in the beginning |
| create_fit_card | Outfit input is missing or incomplete |  Do not generate a full fit card. Instead, return a simpler summary of the selected item and styling idea or explain that a valid outfit suggestion is needed first |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

```text

User Query 
   |
   ▼ 
Planning Loop ──────────────────────────────────────────────────────┐
   |                                                                |
   |-> search_listings(description, size, max_price)                |
   |         |                                                      |
   │         |-- results = []                                       |
   |         |      ▼                                               |
   |         |     ERROR:                                           |
   |         |     "no matching listings found" -> return           |
   |         |                                                      |
   |         |-- results = [item1, item2,...]                       |
   |         |                                                      |
   |       Session: selected_item = results[0]                      |
   │         │                                                      |
   │-> suggest_outfit(selected_item, wardrobe)                      |
   │         │                                                      |
   │         │ wardrobe empty                                       |
   │         │-> Session: outfit_suggestion = general styling advice
   │         │                                                      |
   │         │ wardrobe available                                   |
   │         |-> Session: outfit_suggestion = personalized outfit   |
   │         |                                                      |
   |         |                                                      .
   |-> create_fit_card(outfit_suggestion, selected_item)            .
             |                                                      . 
             | incomplete outfit
             |-> Session: fit_card = simplified summary
             |
             | valid outfit 
             |-> Session: fit_card = generated caption               
             | 
             ▼
          Return session 
             |
          Final response                                            .     
          - Selected listing                                        .
          - Outfit recommendation                                   .
          - Fit card caption                                        |-> error path returns here

 ```  
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

I’ll use Claude to help implement each tool one at a time. For each tool, I’ll give Claude the matching tool spec from this planning doc, including what the tool does, its inputs, return value, and failure mode. For `search_listings`, I’ll also tell it to use `load_listings()` instead of rewriting the data loading logic. I expect Claude to produce code for each function in `tools.py`. Before trusting the code, I’ll check that each function follows the exact input parameters from the starter file and handles its failure case, then I’ll run pytest tests for normal and failure cases.


**Milestone 4 — Planning loop and state management:**
I will use Claude to help wire the tools together into the planning loop. I’ll give it my Architecture diagram, Planning Loop section, State Management section, and Error Handling table from planning.md. I expect it to produce code that calls `search_listings` first, stops early if there are no results, saves the top result in session state, passes that item into `suggest_outfit`, then passes the outfit and item into `create_fit_card`. I’ll verify the code by checking that state is passed between steps correctly and that the agent stops instead of continuing when search returns no results.

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**FitFindr description:** FitFindr helps a user find a clothing listing that matches their request, then uses that item and the user’s wardrobe to suggest a complete outfit and create a short fit card. The search tool runs first when the user asks for an item with filters like price or size; if no listings are found, FitFindr stops and tells the user to broaden or change the search instead of calling the outfit tools with empty results. If a listing is found, FitFindr chooses a relevant item, calls the outfit suggestion tool using the user’s wardrobe, and then turns that outfit into a final fit card.


**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The agent first calls search_listings() to find matching items- it will search for a vintage graphic tee in size M with a maximum price of $30 and returns a list of matching listings sorted by relevance.

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now?-->
The search tool returns several matching listings. The agent selects the top result (e.g a faded band tee for $22) and calls suggest_outfit() using that item along with the user's wardrobe information (baggy jeans and chunky sneakers). 

**Step 3:**
<!-- Continue until the full interaction is complete -->
The outfit suggestion tool returns a styling recommendation. The agent then calls create_fit_card() using the selected item and outfit suggestion to generate a short social-media-style description of the outfit.

**Final output to user:**
<!-- What does the user actually see at the end? -->
The listing, a suggested outfit built around pieces already in their wardrobe, and a fit card caption describing the completed look. If no matching listings are found in Step 1, the agent tells the user that no results were found and suggests changing the search criteria (Steps 2-3 are skipped)