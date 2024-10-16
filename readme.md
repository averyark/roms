## Restaurant Ordering Management Systems

![CodeQL Analysis](https://github.com/averyark/roms/actions/workflows/github-code-scanning/codeql/badge.svg)
![tests ubuntu](https://github.com/averyark/roms/actions/workflows/tests-ubuntu.yml/badge.svg)
![tests macos](https://github.com/averyark/roms/actions/workflows/tests-macos.yml/badge.svg)
![tests windows](https://github.com/averyark/roms/actions/workflows/tests-windows.yml/badge.svg)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
![GitHub commit activity](https://img.shields.io/github/commit-activity/t/averyark/roms)


### How to use
> [!WARNING]
ROMS is only compatible with Python 3.10 and 3.11

Make sure you have python environment installed. Run the following if it is not installed in your directory.

Windows:
```bash
pip install virtualenv
virtualenv -p python3.11 venv
venv\scripts\activate.bat
pip install -r requirements.txt
```

MacOs or Linux:
```shell
pip install virtualenv
virtualenv -p python3.11 venv
venv/bin/activate
pip install -r requirements.txt
```

Install the python 3.11 intepreter if you don't have python 311:\
Windows: Run in Shell
```shell
Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe" -OutFile "Downloads\python-3.11.0-amd64.exe"
Start-Process -FilePath "Downloads\python-3.11.0-amd64.exe" -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0", "Include_pip=1 " -NoNewWindow -Wait
setx path "%path%;C:\Program Files\Python311"
del "Downloads\python-3.11.0-amd64.exe"
```

Run FastAPI to use apis locally:
```
FastAPI dev main.py
```

APIs are accessible locally at http://127.0.0.1:8000/, documentation at http://127.0.0.1:8000/docs#/

> [!IMPORTANT]
Some apis require authentication, so you have to login to use them. Below are some sample account you can use.

Alternatively, you can create your own account

Role|Email|Password
-|-|-
Customer|customer1@gmail.com|somepass12
Manager|manager@roms.com|manager%password122

> More in [Account](#Account)

***

### API Documentations

> [!CAUTION]
> The current SECRET_KEY is exposed, so it is not recommended that any real passwords are used for testing. Replace the SECRET_KEY in `/roms/credentials` with your own key if you're using it for prod. You can generate your own SECRET_KEY using by running `openssl rand -hex 32` in terminal.

### Account
API|Goal|Tag
-|-|-
[account/get_token](http://127.0.0.1:8000/docs#/account/login_account_get_token_get) | Login or retrieve a user session token for authentication | Account
[account/expire_token](http://127.0.0.1:8000/docs#/account/logout_account_expire_token_delete) | Logout or expire the current session token | Account
[account/signup](http://127.0.0.1:8000/docs#/account/signup_account_signup_post) | Creating a new account | Account
[inventory/items/add](http://127.0.0.1:8000/docs#/inventory/inventory_add_item_inventory_items_add_post) | Add a new recipe or item into the inventory | Inventory
[inventory/ingredients/add](http://127.0.0.1:8000/docs#/inventory/ingredients_add_item_inventory_ingredients_add_post) | Add a new ingredient into the inventory | Inventory
[inventory/items/remove](http://127.0.0.1:8000/docs#/inventory/inventory_delete_item_inventory_items_delete_delete) | Remove an item from the inventory | Inventory
[inventory/ingredients/remove](http://127.0.0.1:8000/docs#/inventory/ingredients_delete_item_inventory_ingredients_delete_delete) | Remove an ingredient from the inventory | Inventory
[inventory/items/update](http://127.0.0.1:8000/docs#/inventory/inventory_update_item_inventory_items_update_patch) | Update item details | Inventory
[inventory/ingredient/update](http://127.0.0.1:8000/docs#/inventory/ingredients_update_item_inventory_ingredients_update_patch) | Update ingredient details | Inventory
[order/get](http://127.0.0.1:8000/docs#/order/order_get_order_get__post) | Fetch orders or order history | Order
[order/add](http://127.0.0.1:8000/docs#/order/order_add_order_add__post) | Create a new order | Order
[order/delete](http://127.0.0.1:8000/docs#/order/order_delete_order_delete_delete) | Delete order | Order
[order/item/delete](http://127.0.0.1:8000/docs#/order/order_item_delete_order_item_delete_delete) | Create item of a order | Order
[order/item/edit](http://127.0.0.1:8000/docs#/order/order_item_edit_order_item_edit_patch) | Create item edit | Order
[order/item/edit_status](http://127.0.0.1:8000/docs#/order/order_item_edit_status_order_item_edit_status_patch) | Create item status | Order

#### Manager
1. System Administration: Manage user accounts and credentials.
    - APIs: `/account/add/`, `/account/edit/credentials/`, `/account/edit/user_info/`, `/account/edit/delete/`
2. Order Management: Oversee order details, including viewing and updating order status.
    - APIs: `/order/add/`, `/order/get/`, `/order/delete`, `/order/item/delete`, `/order/item/edit`, `/order/item/edit_status`
3. Financial Management: Track income, expenses, and profitability.
4. Inventory Control: Maintain product inventory by adding, updating, or removing items (product and ingredients) from the system.
   - APIs: `/inventory/ingredients/add`, `/inventory/ingredients/delete`, `/inventory/ingredients/update`, `/items/add`, `/inventory/items/delete` and `/inventory/items/update`
5. Customer Feedback: Monitor and review customer feedback to improve services.

#### Customer
1. Customer Account Management: Create, manage, login and update personal `/account/expire_token`, `/account/get_token`, `/account/signup`
information.
2. Product Browsing: Customers can explore a variety menu items available for
purchase. `/inventory/items/get`
3. Cart Management: Customers can add, remove, or modify items in their shopping
cart. `/order/add`
4. Order Tracking: Monitor the status of placed orders.
    - APIs: `/order/get`
5. Dishes Review: Customers can share feedback and suggestions about purchased
dishes.

#### Cashier
1. Product Display: Access a digital menu or product catalogue to view available items.
2. Manage Discount: Add, delete, or modify discounts or promotions for items / menu.
3. Transaction Completion: Generate receipts for customers.
4. Reporting: Generate reports on sales performance and product popularity.

#### Chef
1. Recipe Management: Create, update, and delete digital recipes.
2. Inventory Check: Verify availability of required ingredients.
3. Record-keeping: Record production quantities, batch numbers, and expiration dates.
4. Equipment Management: Report equipment malfunctions or maintenance need
