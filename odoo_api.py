import xmlrpc.client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("ODOO_URL")
db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USERNAME")
password = os.getenv("ODOO_API_KEY")

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")


# ---------------------------
# CUSTOMER
# ---------------------------
def create_or_get_customer(name, email, phone):

    partner_ids = models.execute_kw(
        db, uid, password,
        'res.partner', 'search',
        [[['email', '=', email]]]
    )

    if partner_ids:
        return partner_ids[0]

    return models.execute_kw(
        db, uid, password,
        'res.partner', 'create',
        [{
            'name': name,
            'email': email,
            'phone': phone
        }]
    )


# ---------------------------
# LEAD (Abandoned Cart)
# ---------------------------
def create_lead(name, email, value):

    return models.execute_kw(
        db, uid, password,
        'crm.lead', 'create',
        [{
            'name': f"Abandoned Cart - {name}",
            'email_from': email,
            'expected_revenue': value
        }]
    )


# ---------------------------
# MARK LEAD WON
# ---------------------------
def mark_lead_won(email):

    leads = models.execute_kw(
        db, uid, password,
        'crm.lead', 'search',
        [[['email_from', '=', email]]]
    )

    if leads:
        models.execute_kw(
            db, uid, password,
            'crm.lead', 'action_set_won',
            [leads]
        )


# ---------------------------
# CREATE SALES ORDER
# ---------------------------
def create_sales_order(partner_id):

    order_id = models.execute_kw(
        db, uid, password,
        'sale.order', 'create',
        [{
            'partner_id': partner_id
        }]
    )

    return order_id


# ---------------------------
# ADD ORDER LINE
# ---------------------------
def add_order_line(order_id, product_name, price, qty):

    product_ids = models.execute_kw(
        db, uid, password,
        'product.product', 'search',
        [[['name', '=', product_name]]]
    )

    if not product_ids:
        product_id = models.execute_kw(
            db, uid, password,
            'product.product', 'create',
            [{
                'name': product_name,
                'type': 'consu',
                'list_price': price
            }]
        )
    else:
        product_id = product_ids[0]

    models.execute_kw(
        db, uid, password,
        'sale.order.line', 'create',
        [{
            'order_id': order_id,
            'product_id': product_id,
            'product_uom_qty': qty,
            'price_unit': price
        }]
    )


# ---------------------------
# CONFIRM ORDER
# ---------------------------
def confirm_order(order_id):

    models.execute_kw(
        db, uid, password,
        'sale.order', 'action_confirm',
        [order_id]
    )


# ---------------------------
# CREATE INVOICE
# ---------------------------
def create_invoice(order_id):

    invoice_ids = models.execute_kw(
        db, uid, password,
        'sale.order', '_create_invoices',
        [order_id]
    )

    return invoice_ids