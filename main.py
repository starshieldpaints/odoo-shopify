from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import base64
import os

from shopify_handler import (
    handle_customer,
    handle_abandoned_cart,
    handle_order
)

app = FastAPI()

SHOPIFY_SECRET = os.getenv("SHOPIFY_SECRET")

@app.get("/")
def home():
    return {"status": "Shopify → Odoo Middleware running 🚀"}


# 🔐 Verify Shopify Webhook
def verify_shopify_webhook(data, hmac_header):
    digest = hmac.new(
        SHOPIFY_SECRET.encode("utf-8"),
        data,
        hashlib.sha256
    ).digest()

    computed_hmac = base64.b64encode(digest)

    return hmac.compare_digest(computed_hmac, hmac_header.encode("utf-8"))


@app.post("/webhooks/shopify")
async def shopify_webhook(request: Request):

    raw_body = await request.body()
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")

    if not verify_shopify_webhook(raw_body, hmac_header):
        raise HTTPException(status_code=401, detail="Invalid webhook")

    data = await request.json()
    topic = request.headers.get("X-Shopify-Topic")

    print(f"📩 Received webhook: {topic}")

    try:

        if topic == "customers/create":
            handle_customer(data)

        elif topic == "checkouts/create":
            handle_abandoned_cart(data)

        elif topic == "orders/create":
            handle_order(data)

        else:
            print("⚠️ Unknown topic:", topic)

    except Exception as e:
        print("❌ Error:", str(e))
        raise HTTPException(status_code=500, detail="Processing failed")

    return {"success": True}