## Restaurant Ordering Management Systems

![CodeQL Analysis](https://github.com/averyark/roms/actions/workflows/github-code-scanning/codeql/badge.svg)
![Python 3.11, 3.10](https://github.com/averyark/roms/actions/workflows/python-package.yml/badge.svg)
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
Goal|API
-|-
Login / GetToken | [account/get_token](http://127.0.0.1:8000/docs#/account/login_account_get_token_get)
Logout / ExpireToken | [account/expire_token](http://127.0.0.1:8000/docs#/account/logout_account_expire_token_delete)
Signup | [account/signup](http://127.0.0.1:8000/docs#/account/signup_account_signup_post)



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
