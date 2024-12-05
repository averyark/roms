## Restaurant Ordering Management Systems

![CodeQL Analysis](https://github.com/averyark/roms/actions/workflows/github-code-scanning/codeql/badge.svg)
![tests ubuntu](https://github.com/averyark/roms/actions/workflows/tests-ubuntu.yml/badge.svg)
![tests macos](https://github.com/averyark/roms/actions/workflows/tests-macos.yml/badge.svg)
![tests windows](https://github.com/averyark/roms/actions/workflows/tests-windows.yml/badge.svg)
![GitHub commit activity](https://img.shields.io/github/commit-activity/t/averyark/roms)


### How to use
> [!WARNING]
ROMS is only compatible with Python 3.10 and 3.11

Make sure you have python environment installed. Run the following if it is not installed in your directory.

Run FastAPI to use apis locally:
```
FastAPI dev main.py
```

> [!NOTE]
If you're downloading the source directly, you might be starting with a fresh Database

APIs are accessible locally at http://127.0.0.1:8000/, documentation at http://127.0.0.1:8000/docs#/

> [!IMPORTANT]
Some apis require authentication, so you have to login to use them. Below are some sample account you can use.

Alternatively, you can create your own account

Role|Email|Password
-|-|-
Customer|customer1@gmail.com|somepass12
Manager|manager@roms.com|manager%password122

***

### API Documentations

> [!CAUTION]
> It is not recommended that any real passwords are used for testing. Replace the SECRET_KEY in `/roms/credentials` with your own key if you're using it for prod. You can generate your own SECRET_KEY using by running `openssl rand -hex 32` in terminal.


#### Manager
1. System Administration: Manage user accounts and credentials.
    - APIs: `/account/add/`, `/account/edit/credentials/`, `/account/edit/user_info/`, `/account/edit/delete/`
2. Order Management: Oversee order details, including viewing and updating order status.
    - APIs: `/order/add/`, `/order/get/`, `/order/delete`, `/order/item/delete`, `/order/item/edit`, `/order/item/edit_status`
3. Financial Management: Track income, expenses, and profitability.
   - APIs: `/cashier/analytics`, `/cashier/print/stats`
4. Inventory Control: Maintain product inventory by adding, updating, or removing items (product and ingredients) from the system.
   - APIs: `/inventory/ingredients/add`, `/inventory/ingredients/delete`, `/inventory/ingredients/update`, `/items/add`, `/inventory/items/delete` and `/inventory/items/update`
5. Customer Feedback: Monitor and review customer feedback to improve services.
   - APIS: `/review/get`, `/review/add`, `/review/edit`, `/review/delete`

#### Customer
1. Customer Account Management: Create, manage, login and update personal
   - APIs: `/account/expire_token`, `/account/get_token`, `/account/signup`
information.
1. Product Browsing: Customers can explore a variety menu items available for purchase.
   - APIs: `/inventory/items/get`
1. Cart Management: Customers can add, remove, or modify items in their shopping
cart.
   - APIs: `/order/add`
1. Order Tracking: Monitor the status of placed orders.
   - APIs: `/order/get`
2. Dishes Review: Customers can share feedback and suggestions about purchased dishes.
   - APIS:`/review/get`, `/review/add`, `/review/edit`, `/review/delete`

#### Cashier
1. Product Display: Access a digital menu or product catalogue to view available items.
   - APIs: `/inventory/items/get`
2. Manage Discount: Add, delete, or modify discounts or promotions for items / menu.
   - APIs: `/inventory/items/add`, `/inventory/items/edit`, `/inventory/items/delete`,
3. Transaction Completion: Generate receipts for customers.
   - APIs: `/cashier/checkout`
4. Reporting: Generate reports on sales performance and product popularity.
   - APIs: `/cashier/analytics`

#### Chef
1. Recipe Management: Create, update, and delete digital recipes.
   - APIs: `/inventory/items/get`, `/inventory/items/add`, `/inventory/items/edit`, `/inventory/items/delete`
2. Inventory Check: Verify availability of required ingredients.
   - APIs: `/inventory/items/available`
3. Record-keeping: Record production quantities, batch numbers, and expiration dates.
   - APIs: `/inventory/stock_batch/get`, `/inventory/stock_batch/add`, `/inventory/stock_batch/remove`, `/inventory/stock/get`, `/inventory/stock/add`, `/inventory/stock/edit`, `/inventory/stock/remove`
4. Equipment Management: Report equipment malfunctions or maintenance need
   - APIs: `/equipment/remark/get`, `/equipment/remark/add`, `/equipment/remark/add`, `/equipment/remark/delete`
