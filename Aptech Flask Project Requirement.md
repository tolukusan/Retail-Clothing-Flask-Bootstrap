## 🛍️ Core E-commerce Requirements

| Original Requirement                 | Clarified & Specific Requirements                                                                                                                                                                                                                                                                                                                                                           |
| :----------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Watches, Bags (15 per item type)** | **Product Catalogue:** The database must contain a minimum of 30 products in total (15 watches and 15 bags). Each product must have a **unique SKU**, **name**, **description**, **price**, **stock level**, and at least one **image URL**.                                                                                                                                                |
| **A sign up page and a login page**  | **User Authentication:** 1. Users must be able to **register** using a unique **email address** and a **secure password** (stored as a hash). 2. Users must be able to **log in** using their email and password. 3. The system must use **Flask Sessions** to maintain the user's logged-in state. 4. **Password Reset** functionality is a common implicit requirement (optional for V1). |
| **A cart feature**                   | **Shopping Cart:** 1. The cart must be stored **in the database** (not just the session) and linked to the logged-in user. 2. Users must be able to **add**, **remove**, and **update the quantity** of items in the cart. 3. The cart page must display the **subtotal** and the **total cost**.                                                                                           |
| **A section to view orders**         | **Order History:** 1. Users must be able to view a list of all their **past orders**. 2. Each order view must show the **order date**, **total amount paid**, and the **current status** (e.g., _Processing_, _Shipped_, _Delivered_). 3. The user must be able to click an order to view the **specific items** and quantities bought.                                                     |

---

## 💳 Transactional and Financial Requirements

| Original Requirement      | Clarified & Specific Requirements                                                                                                                                                                                                                                                                                                                                                                                                       |
| :------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Mock payment platform** | **Checkout Process:** 1. The checkout must be a **multi-step process** (e.g., Shipping Details → Payment). 2. The "payment" will be a mock success/fail page, where a successful transaction **reduces the stock level** for all items purchased. 3. A successful transaction must create a new **Order record** and corresponding **Order Item records** in the database.                                                              |
| **A wallet feature**      | **User Wallet (Account Balance):** 1. Users must have a **digital balance** (the "wallet") linked to their account, stored as a decimal value in the database. 2. Users must be able to **"top up"** their wallet balance (using a mock top-up endpoint). 3. The wallet balance must be an **available payment method** at checkout. 4. If an order is purchased using the wallet, the **wallet balance must be deducted** accordingly. |

---

## 🎯 Next Steps

These expanded points give us a much clearer blueprint for your database models and application logic.

The immediate next step, since we deferred database initialisation, should be to define the **Application Factory** in **`app/__init__.py`** and create the basic **User Model** in a separate file like **`app/models.py`**, which will be needed for both the sign-up/login and the wallet feature.
