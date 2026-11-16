---
name: product-search
description: Build, refine, or verify the Streamlit product search app using DummyJSON, ascending numeric prices, and the five lowest-priced matches.
---

# Product search workflow

Use this skill when implementing or changing this project's product search website.

## Query and display products

1. Fetch the product collection from `https://dummyjson.com/products` with a finite timeout. Check the HTTP status before decoding JSON and validate that the response contains a `products` list.
2. Match the user's non-empty keyword against product titles case-insensitively. Trim surrounding whitespace from the keyword.
3. Keep only records with a valid numeric price. Sort matches by numeric price ascending and return at most the first five.
4. Display each selected product's title and price, and display its thumbnail when a usable URL is present. Label all results as sample product information from a dataset, not live retailer offers.

## Empty results and errors

- Ask for a keyword if the submitted query is empty.
- If a valid query has no matching products, show a clear no-results message.
- Catch request timeouts, connection failures, unsuccessful HTTP responses, JSON decoding errors, and malformed response data. Show a concise, helpful error in the interface; do not display a traceback.
- Do not misreport an API error as an empty search result.

## Testing

- Verify title matching without case sensitivity, numeric ascending price order, the five-result maximum, and behavior with fewer than five matches.
- Check blank input and a query with no matches.
- Check malformed products/prices and API errors, including timeout or HTTP failure.
- Prefer tests around small data/filtering functions; use a manual Streamlit check with real API data for the rendered layout.
