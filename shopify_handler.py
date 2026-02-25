from odoo_api import (
    create_or_get_customer,
    create_lead,
    mark_lead_won,
    create_sales_order,
    add_order_line,
    confirm_order,
    create_invoice
)


# ---------------------------
# NEW CUSTOMER
# ---------------------------
def handle_customer(data):

    name = f"{data['first_name']} {data['last_name']}"
    email = data['email']
    phone = data.get('phone', '')

    create_or_get_customer(name, email, phone)


# ---------------------------
# ABANDONED CART
# ---------------------------
def handle_abandoned_cart(data):

    email = data['email']
    value = data['total_price']

    create_lead("Shopify Cart", email, value)


# ---------------------------
# ORDER CREATED / PAID
# ---------------------------
def handle_order(data):

    customer = data["customer"]

    name = f"{customer['first_name']} {customer['last_name']}"
    email = customer["email"]
    phone = customer.get("phone", "")

    partner_id = create_or_get_customer(name, email, phone)

    # Mark previous lead WON
    mark_lead_won(email)

    order_id = create_sales_order(partner_id)

    for item in data["line_items"]:
        add_order_line(
            order_id,
            item["name"],
            item["price"],
            item["quantity"]
        )

    confirm_order(order_id)

    # If payment done → create invoice
    if data["financial_status"] == "paid":
        create_invoice(order_id)