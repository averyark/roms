# @fileName: accounting.py
# @creation_date: 18/10/2024
# @authors: averyark

from typing import Annotated, Literal, Optional, List
from datetime import date, time, datetime

from fastapi import Depends, HTTPException, status
from zpl import Label
from PIL import Image

from ..account import authenticate, authenticate_optional, validate_role
from ..api import app
from ..user import User
from ..database import session, to_dict
from ..database.models import VoucherUsesModel, OrderModel, OrderItemModel, TableSessionModel, TableModel, ItemModel

from .voucher import get_total_after_voucher
from .order import get_session_orders
from .table import verify_table_session

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
    print('aaa', receipt_info)
    l = Label(120, 70)
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
    l.write_text(f'TEL: {receipt_info["telephone"]}', char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(receipt_info['registration_number'], char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(f'(SST ID: {DUMMY_SST_ID})', char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 5

    l.origin(5, y_pos)
    l.write_text("(INVOICE)", char_height=3, char_width=3, line_width=60, justification='C')
    l.endorigin()
    y_pos += 6

    # Invoice and Table details
    l.origin(5, y_pos)
    l.write_text(f" Invoice No: {DUMMY_INVOICE_NO}", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(f" Table No: {receipt_info['table_number']}", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()
    y_pos += 3

    l.origin(5, y_pos)
    l.write_text(f" Date Time: {receipt_info['date_time']}", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()
    y_pos += 5

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text("(QTY ITEM)", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text("(RM)", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 2

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 4

    initial_y_pos_1 = y_pos
    initial_y_pos_2 = y_pos

    # Itemized list
    for item in receipt_info['items']:
        l.origin(5, initial_y_pos_1)
        l.write_text(f" {item['quantity']} {item['name']}", char_height=2, char_width=2, line_width=60, justification='L')
        l.endorigin()
        initial_y_pos_1 += 4

    for item in receipt_info['items']:
        l.origin(5, initial_y_pos_2)
        l.write_text(f"{item['price']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
        l.endorigin()
        initial_y_pos_2 += 4

    y_pos += (initial_y_pos_1 - y_pos)  # Space before subtotal
    # Add a separator line
    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 4
    # Add a separator line before totals
    # l.origin(0, y_pos)
    # l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    # l.endorigin()
    # y_pos += 4

    # Totals section
    # l.origin(0, y_pos)
    # l.write_text(" Voucher Applied", char_height=2, char_width=2, line_width=60, justification='L')
    # l.endorigin()

    # for voucher in receipt_info['applied_vouchers']:
    #     l.origin(0, y_pos)
    #     l.write_text(f"{voucher} ", char_height=2, char_width=2, line_width=60, justification='R')
    #     l.endorigin()
    #     y_pos += 4

    l.origin(5, y_pos)
    l.write_text(" Discount", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['discount']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 4

    l.origin(5, y_pos)
    l.write_text(" Subtotal", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['subtotal']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 4

    l.origin(5, y_pos)
    l.write_text(f" GST - {receipt_info['government_tax']*100}%", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['gst_total']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 4

    l.origin(5, y_pos)
    l.write_text(f" SST - {receipt_info['service_tax']*100}%", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['sst_total']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 4

    l.origin(5, y_pos)
    l.write_text(" Rounding Adj", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['rounding_adj']:.2f} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 4

    l.origin(5, y_pos)
    l.write_text(" NET TOTAL", char_height=3, char_width=3, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['net_total']:.2f} ", char_height=3, char_width=3, line_width=60, justification='R')
    l.endorigin()
    y_pos += 5

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 4

    l.origin(5, y_pos)
    l.write_text(" Payment Method", char_height=2, char_width=2, line_width=60, justification='L')
    l.endorigin()

    l.origin(5, y_pos)
    l.write_text(f"{receipt_info['payment_method']} ", char_height=2, char_width=2, line_width=60, justification='R')
    l.endorigin()
    y_pos += 4

    l.origin(5, y_pos)
    l.write_text("-" * 40, char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 4

    l.origin(5, y_pos)
    l.write_text("Thank you, please come again!", char_height=2, char_width=2, line_width=60, justification='C')
    l.endorigin()
    y_pos += 4

    # Save ZPL output
    with open("./receipt.zpl", "w") as file:
        file.write(l.dumpZPL())
        print(l.dumpZPL())  # Print ZPL to console for debugging

    l.preview()
    return l

@app.post('/cashier/receipt', tags=['cashier'])
def print_receipt(
    table_session_id: str,
    payment_method: Literal['Touch n Go', 'Credit Card', 'Debit Card', 'Cash']
):
    print(table_session_id, payment_method)
    table_session = session.query(TableSessionModel).filter(
        TableSessionModel.session_id == table_session_id
    ).one_or_none()

    table = session.query(TableModel).filter(
        TableModel.table_id == table_session.table_id
    ).one_or_none()

    applied_vouchers = session.query(VoucherUsesModel).filter(
        VoucherUsesModel.table_session_id == table_session_id
    ).all()

    order = session.query(OrderModel).filter(
        OrderModel.session_id == table_session_id
    ).one_or_none()

    order_items = session.query(OrderItemModel).filter(
        OrderItemModel.order_id == order.order_id
    ).all()

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
        'payment_method': payment_method
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

@app.patch('/cashier/checkout', tags=['cashier'])
def checkout(
    user: Annotated[
        User, Depends(validate_role(roles=['Manager', "Chef", "Cashier"]))
    ],
    table_session_id: str,
    payment_method: Literal['Touch n Go', 'Credit Card', 'Debit Card', 'Cash']
):
    # grab relevant info
    applied_vouchers = session.query(VoucherUsesModel).filter(
        VoucherUsesModel.table_session_id == TableSessionModel
    ).all()
    order = session.query(OrderModel).filter(
        OrderModel.session_id == table_session_id
    ).one_or_none()
    order_items = session.query(OrderItemModel).filter(
        OrderItemModel.order_id == order.order_id
    ).all()

    price_total = 0
    government_tax_total = 0
    service_tax_total = 0

    for item in order_items:
        price = item.price
        price_total += price
        government_tax_total += price * fetch_setting('government_tax')
        service_tax_total += price * fetch_setting('service_tax')

    # calculate metrics

    pass
