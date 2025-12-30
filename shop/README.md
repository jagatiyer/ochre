Shop app — Product Units (admin guide)

Simple steps for configuring units in the Django admin (for non-technical users):

1) Create Unit Types (one-time)
   - Go to "Unit types" in the admin and add entries like "Volume" or "Size".
   - The "Name" is what you will see (e.g. Volume). The "Code" is a short identifier (e.g. volume).

2) Create or open a Shop Item
   - In "Shop Items" add a product or open an existing one.

3) Add Product Units for that item
   - Under the product, use the "Product units" inline to add one or more units.
   - For each Product Unit set:
     - Unit type: choose the Unit Type you created (Volume, Size, etc.)
     - Label: what customers will see (e.g. "500 ml", "Large")
     - Price: the sell price for this unit
     - Active: checked = visible to customers; uncheck to hide

4) Set one default unit
   - Mark exactly one Product Unit as the Default for the product.
   - The default is the unit automatically selected on the site.
   - The system enforces a single default when you save (the admin will unset others).

5) Verify on the website
   - Visit the product page and the shop listing to confirm the selector and price match the admin settings.

Notes
- If a product has no Product Units, it behaves like a normal product and shows the base price.
- If multiple units are present, customers must select a unit before adding to cart (or the default will be used).
- For help, contact the developer or the site admin team.
