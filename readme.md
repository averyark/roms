## Restaurant Ordering Management Systems

### How to use
> [!WARNING]
ROMS is not compatible with python 3.12 or higher. Tests are conducted only in python 3.10 and 3.11

Make sure you have python environment installed. You can find out by looking for the venv folder in the root folder. If you don't see it, run the following:

Windows:
```
python venv venv
venv\scripts\activate.bat
pip install -r requirements.txt
```

MacOs or Linux:
```
python venv venv
venv\bin\activate
pip install -r requirements.txt
```

APIs accessible locally at http://127.0.0.1:8000/, documentation at http://127.0.0.1:8000/docs#/

Sample Accounts:
```
role: Customer
email: customer1@gmail.com
password: somepass12
```
```
role: Manager
email: manager@roms.com
password: manager%password122
```

### API Documentations

#### Manager
1. System Administration: Manage user accounts and credentials.
    - APIs: `/account/add/`, `/account/edit/credentials/`, `/account/edit/user_info/`, `/account/edit/delete/`
2. Order Management: Oversee order details, including viewing and updating order status.
3. Financial Management: Track income, expenses, and profitability.
4. Inventory Control: Maintain product inventory by adding, updating, or removing items (product and ingredients) from the system.
   - APIs: `/inventory/ingredients/add`, `/inventory/ingredients/delete`, `/inventory/ingredients/update`, `/items/add`, `/inventory/items/delete` and `/inventory/items/update`
5. Customer Feedback: Monitor and review customer feedback to improve services.

#### Customer
1. Customer Account Management: Create, manage, login and update personal
information.
2. Product Browsing: Customers can explore a variety menu items available for
purchase.
3. Cart Management: Customers can add, remove, or modify items in their shopping
cart.
4. Order Tracking: Monitor the status of placed orders.
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
