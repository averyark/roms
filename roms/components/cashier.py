# @fileName: accounting.py
# @creation_date: 18/10/2024
# @authors: averyark

from typing import Annotated, Literal
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import func

from fastapi import Depends, HTTPException, status
from zpl import Label

from ..account import validate_role
from ..api import app
from ..user import User
from ..database import session
from ..database.models import VoucherUsesModel, OrderModel, OrderItemModel, TableSessionModel, TableModel, ItemModel, AnalyticsCheckoutModel

from .voucher import get_total_after_voucher

DUMMY_SST_ID = 'W10-2210-32100024'
DUMMY_INVOICE_NO = 'INV00001'

settings_literal = Literal['government_tax', 'service_tax', 'restaurant_name', 'restaurant_company', 'registration_number', 'address', 'address_2', 'city', 'state', 'telephone']

settings_temporary = {
    'government_tax': 0.06,
    'service_tax': 0.1,
    'restaurant_name': 'MOROSH BB PARK',
    'restaurant_company': 'MOROSH RESTAURANT Sdn Bhd',
    'registration_number': '202001026768 (1383088-P)',
    'address': 'Lot 7.102.00, Level 7',
    'address_2': 'Pavillion Elite',
    'city': '43300, Kuala Lumpur',
    'state': 'Wilayah Persekutuan, Kuala Lumpur',
    'telephone': '012-345-6789'
}

def fetch_setting(setting: settings_literal = None):
    if not setting is None:
        return settings_temporary[setting]
    else:
        return settings_temporary

def generate_receipt(receipt_info: dict):
    l = Label(110, 70)
    y_pos = 4

    # Header section
    l.origin(5, y_pos)
    l.write_text(receipt_info['restaurant_name'], char_height=4, char_width=4, line_width=60, justification='C')
    l.endorigin()
    y_pos += 6

    l.origin(5, y_pos)
    l.write_text(receipt_info['address'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['address_2'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['city'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['state'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['restaurant_company'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['registration_number'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(f'TEL: {receipt_info["telephone"]}', char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(f'(SST ID: {DUMMY_SST_ID})', char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text("(INVOICE)", char_height=3, char_width=3, line_width=60, justification='C')
    l.endorigin()
    y_pos += 4

    l.origin(0, y_pos)
    l.write_text(f" Table No", char_height=3, char_width=3, line_width=60, justification='R')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f" Invoice No: {DUMMY_INVOICE_NO}", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()
    y_pos += 3

    l.origin(25, y_pos+1.5)
    l.write_text(f"{receipt_info['table_number']}", char_height=2.5, char_width=2.5, line_width=60, justification='C')
    l.endorigin()

    l.origin(25, y_pos+1.5)
    l.write_text(f"{receipt_info['table_number']}", char_height=2.5, char_width=2.5, line_width=60, justification='C')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f" Cashier: {receipt_info['cashier']}", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(f" Date Time: {receipt_info['date_time']}", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text("Qty   Item", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text("Price (MYR)", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 2

    total_quantity = 0
    cumulative_price = 0

    for item in receipt_info['items']:
        l.origin(5, y_pos)
        total_quantity += item['quantity']
        quantity_len = len(str(item['quantity']))
        l.write_text(f" {item['quantity']}{' ' * (6 - quantity_len)} {item['name']}", char_height=2, char_width=2, line_width=60, justification='L')
        l.endorigin()
        l.origin(5, y_pos)
        l.write_text(f"{item['price']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
        cumulative_price += item['price']
        l.endorigin()
        y_pos += 3

    y_pos -= 1

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text(f"{total_quantity} ", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()
    l.origin(5, y_pos)
    l.write_text(f"{cumulative_price:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 2

    l.origin(9.25, y_pos)
    l.write_text("Discount", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['discount']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 3

    l.origin(9.25, y_pos)
    l.write_text("Subtotal", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['subtotal']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 3

    l.origin(9.25, y_pos)
    l.write_text(f"GST - {receipt_info['government_tax']*100}%", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['gst_total']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 3

    l.origin(9.25, y_pos)
    l.write_text(f"SST - {receipt_info['service_tax']*100}%", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['sst_total']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 3

    l.origin(9.25, y_pos)
    l.write_text("Bill rounding", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['rounding_adj']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text("NET TOTAL", char_height=3, char_width=3, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['net_total']:.2f} ", char_height=3, char_width=3, line_width=60, justification='R')
    l.endorigin()
    y_pos += 4

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text(" Payment Method", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['payment_method']} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text("Thank you, please come again!", char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.preview()
    return l.dumpZPL()

@app.post('/cashier/print/receipt', tags=['cashier'])
def print_receipt(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', "Chef", "Cashier"]))
    ],
    table_session_id: str,
    payment_method: Literal['Touch n Go', 'Credit Card', 'Debit Card', 'Cash'],
):
    table_session = session.query(TableSessionModel).filter(
        TableSessionModel.session_id == table_session_id
    ).one_or_none()

    table = session.query(TableModel).filter(
        TableModel.table_id == table_session.table_id
    ).one_or_none()

    applied_vouchers = session.query(VoucherUsesModel).filter(
        VoucherUsesModel.table_session_id == table_session_id
    ).all()

    orders = []
    order_items = []

    for order in session.query(OrderModel).filter(
        OrderModel.session_id == table_session_id,
    ).all():
        orders.append(order)
        for order_item in session.query(OrderItemModel).filter(
            OrderItemModel.order_id == order.order_id
        ).all():
            order_items.append(order_item)

    receipt_info = {
        'table_number': table.table_id,
        'date_time': table_session.start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'items': [],
        'applied_voucher': [],
        'subtotal': 0,
        'gst_total': 0,
        'sst_total': 0,
        'discount': 0,
        'rounding_adj': 0,
        'net_total': 0,
        'payment_method': payment_method,
        'cashier': user.get_name()
    }

    sub_total = 0

    for order_item in order_items:
        price = order_item.price
        sub_total += price

        item = session.query(ItemModel).filter(
            ItemModel.item_id==order_item.item_id
        ).one()

        receipt_info['items'].append({
            'name': item.name,
            'quantity': order_item.quantity,
            'price': price,
        })

    _, voucher_discount = get_total_after_voucher(sub_total, applied_vouchers)

    sub_total -= voucher_discount
    government_tax_total = sub_total * fetch_setting('government_tax')
    service_tax_total = sub_total * fetch_setting('service_tax')
    net_total = sub_total + government_tax_total + service_tax_total

    rounding_adj = round(net_total, 1) - (net_total)

    net_total += rounding_adj

    settings = fetch_setting()

    for k, v in settings.items():
        receipt_info.update({k: v})

    receipt_info.update({
        'subtotal': sub_total,
        'gst_total': government_tax_total,
        'sst_total': service_tax_total,
        'discount': -voucher_discount,
        'rounding_adj': rounding_adj,
        'net_total': net_total
    })

    generate_receipt(receipt_info)

@app.post('/cashier/checkout', tags=['cashier'])
def checkout(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', "Chef", "Cashier"]))
    ],
    table_session_id: str,
    payment_method: Literal['Touch n Go', 'Credit Card', 'Debit Card', 'Cash']
):
    table_session = session.query(TableSessionModel).filter(
        TableSessionModel.session_id == table_session_id
    ).one_or_none()

    if table_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This table session does not exist')

    if table_session.status != "Active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Cannot checkout a completed session')

    table = session.query(TableModel).filter(
        TableModel.table_id == table_session.table_id
    ).one_or_none()

    if table is None:
        raise HTTPException(status_code=status.HTTP_404_BAD_REQUEST, detail='This table does not exist')

    if table.status != "Unavailable":
        table.status = "Available"

    table_session.status = "Completed"

    session.commit()
    session.refresh(table)
    session.refresh(table_session)

    applied_vouchers = session.query(VoucherUsesModel).filter(
        VoucherUsesModel.table_session_id == table_session_id
    ).all()

    orders = []
    order_items = []

    for order in session.query(OrderModel).filter(
        OrderModel.session_id == table_session_id,
    ).all():
        orders.append(order)
        for order_item in session.query(OrderItemModel).filter(
            OrderItemModel.order_id == order.order_id
        ).all():
            order_items.append(order_item)

    receipt_info = {
        'table_number': table.table_id,
        'date_time': table_session.start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        'items': [],
        'applied_voucher': [],
        'subtotal': 0,
        'gst_total': 0,
        'sst_total': 0,
        'discount': 0,
        'rounding_adj': 0,
        'net_total': 0,
        'payment_method': payment_method,
        'cashier': user.get_name()
    }

    sub_total = 0

    for order_item in order_items:
        price = order_item.price
        sub_total += price

        item = session.query(ItemModel).filter(
            ItemModel.item_id==order_item.item_id
        ).one()

        receipt_info['items'].append({
            'name': item.name,
            'quantity': order_item.quantity,
            'price': price,
        })

    _, voucher_discount = get_total_after_voucher(sub_total, applied_vouchers)

    sub_total -= voucher_discount
    government_tax_total = sub_total * fetch_setting('government_tax')
    service_tax_total = sub_total * fetch_setting('service_tax')
    net_total = sub_total + government_tax_total + service_tax_total

    rounding_adj = round(net_total, 1) - (net_total)

    net_total += rounding_adj

    settings = fetch_setting()

    for k, v in settings.items():
        receipt_info.update({k: v})

    receipt_info.update({
        'subtotal': sub_total,
        'gst_total': government_tax_total,
        'sst_total': service_tax_total,
        'discount': -voucher_discount,
        'rounding_adj': rounding_adj,
        'net_total': net_total
    })

    try:
        session.add(AnalyticsCheckoutModel(
            analytics_id = str(uuid4()),
            table_session_id = table_session_id,
            subtotal = sub_total,
            gst_total = government_tax_total,
            sst_total = service_tax_total,
            discount = -voucher_discount,
            rounding_adj = rounding_adj,
            net_total = net_total,
            cashier = user.user_id,
            payment_method = payment_method,
            checkout_time = datetime.now()
        ))
    except Exception as e:
        print(e)
        session.rollback()
    else:
        session.commit()

    generate_receipt(receipt_info)

    return {
        'msg': 'Checkout successful',
        'receipt_info': receipt_info
    }

def to_dict_v2(models):
    return [model.__dict__ for model in models]

@app.get('/cashier/analytics', tags=['Cashier', 'Manager'])
def get_analytics(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', "Chef", "Cashier"]))
    ],
    min_timeframe: datetime,
    max_timeframe: datetime
):

    analytics = session.query(AnalyticsCheckoutModel).filter(
        AnalyticsCheckoutModel.checkout_time >= min_timeframe,
        AnalyticsCheckoutModel.checkout_time <= max_timeframe
    ).all()

    analytics_dict = to_dict_v2(analytics)

    return {
        "msg": "Fetch analytics successful",
        "analytics": analytics_dict or []
    }

def get_stats(timeframe_start, timeframe_end):
    sales_count = session.query(func.count(AnalyticsCheckoutModel.analytics_id)).filter(
        AnalyticsCheckoutModel.checkout_time >= timeframe_start,
        AnalyticsCheckoutModel.checkout_time <= timeframe_end
    ).scalar()

    revenue = session.query(func.sum(AnalyticsCheckoutModel.net_total)).filter(
        AnalyticsCheckoutModel.checkout_time >= timeframe_start,
        AnalyticsCheckoutModel.checkout_time <= timeframe_end
    ).scalar()

    gov_tax = session.query(func.sum(AnalyticsCheckoutModel.gst_total)).filter(
        AnalyticsCheckoutModel.checkout_time >= timeframe_start,
        AnalyticsCheckoutModel.checkout_time <= timeframe_end
    ).scalar()

    service_tax = session.query(func.sum(AnalyticsCheckoutModel.sst_total)).filter(
        AnalyticsCheckoutModel.checkout_time >= timeframe_start,
        AnalyticsCheckoutModel.checkout_time <= timeframe_end
    ).scalar()

    return sales_count, revenue, gov_tax, service_tax

def get_payment_method_stats(timeframe_start, timeframe_end):
    payment_methods = session.query(
        AnalyticsCheckoutModel.payment_method,
        func.count(AnalyticsCheckoutModel.analytics_id).label('count')
    ).filter(
        AnalyticsCheckoutModel.checkout_time >= timeframe_start,
        AnalyticsCheckoutModel.checkout_time <= timeframe_end
    ).group_by(AnalyticsCheckoutModel.payment_method).all()

    total_transactions = sum([method.count for method in payment_methods])
    payment_method_stats = {method.payment_method: (method.count / total_transactions) * 100 for method in payment_methods}

    return payment_method_stats

def generate_analytics_receipt(receipt_info: dict):
    l = Label(110, 70)
    y_pos = 4

    # Header section
    l.origin(5, y_pos)
    l.write_text(receipt_info['restaurant_name'], char_height=4, char_width=4, line_width=60, justification='C')
    l.endorigin()
    y_pos += 6

    l.origin(5, y_pos)
    l.write_text(receipt_info['address'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['address_2'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['city'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['state'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['telephone'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    # Stats section
    stats = receipt_info['stats']
    l.origin(5, y_pos)
    l.write_text("Stats:", char_height=3, char_width=3, line_width=60, justification='L')
    l.endorigin()
    y_pos += 4

    for stat in stats:
        l.origin(5, y_pos)
        l.write_text(stat, char_height=2, char_width=2, line_width=60, justification='L')
        l.endorigin()
        y_pos += 3

    # Payment method stats section
    payment_method_stats = receipt_info['payment_method_stats']
    l.origin(5, y_pos)
    l.write_text("Payment Method Stats:", char_height=3, char_width=3, line_width=60, justification='L')
    l.endorigin()
    y_pos += 4

    for method, percentage in payment_method_stats.items():
        l.origin(5, y_pos)
        l.write_text(f"{method}: {percentage:.2f}%", char_height=2, char_width=2, line_width=60, justification='L')
        l.endorigin()
        y_pos += 3

    l.preview()
    return l.dumpZPL()

@app.post('/cashier/print/stats', tags=['Cashier', 'Manager'])
def print_receipt(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', "Chef", "Cashier"]))
    ]
):
    now = datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = start_of_day - timedelta(days=start_of_day.weekday())
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    stats_today = get_stats(start_of_day, now)
    stats_week = get_stats(start_of_week, now)
    stats_month = get_stats(start_of_month, now)
    stats_year = get_stats(start_of_year, now)

    payment_method_stats = get_payment_method_stats(start_of_year, now)

    receipt_info = {
        'stats': [
            f"Number of Sales today: {stats_today[0]}",
            f"Number of Sales this week: {stats_week[0]}",
            f"Number of Sales this month: {stats_month[0]}",
            f"Number of Sales this year: {stats_year[0]}",
            f"Revenue today: {round(stats_today[1], 2)}",
            f"Revenue this week: {round(stats_week[1], 2)}",
            f"Revenue this month: {round(stats_month[1], 2)}",
            f"Revenue this year: {round(stats_year[1], 2)}",
            f"Government Tax collected today: {round(stats_today[2], 2)}",
            f"Government Tax collected this week: {round(stats_week[2], 2)}",
            f"Government Tax collected this month: {round(stats_month[2], 2)}",
            f"Government Tax collected this year: {round(stats_year[2], 2)}",
            f"Service Tax collected today: {round(stats_today[3], 2)}",
            f"Service Tax collected this week: {round(stats_week[3], 2)}",
            f"Service Tax collected this month: {round(stats_month[3], 2)}",
            f"Service Tax collected this year: {round(stats_year[3], 2)}"
        ],
        'payment_method_stats': payment_method_stats
    }

    settings = fetch_setting()

    for k, v in settings.items():
        receipt_info.update({k: v})

    zpl_receipt = generate_analytics_receipt(receipt_info)

    return {"msg": "Receipt printed successfully", "zpl_receipt": zpl_receipt}
