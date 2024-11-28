import paypalrestsdk
from django.conf import settings
from decouple import config

paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": config('PAYPAL_ID'),
    "client_secret": config('PAYPAL_SECRET'),
})

def create_payout(sender_email, receiver_email, amount):
    payout = paypalrestsdk.Payout({
        "sender_batch_header": {
            "sender_batch_id": f"batch_{sender_email}_{receiver_email}",
            "email_subject": "You have a payment",
        },
        "items": [{
            "recipient_type": "EMAIL",
            "receiver": receiver_email,
            "amount": {
                "value": amount,
                "currency": "USD",
            },
            "note": "Payment for your service",
           
        }]
    })

    if payout.create(sync_mode=False):  
        return {"status": "SUCCESS", "payout_batch_id": payout["batch_header"]["payout_batch_id"]}
    else:
        return {"status": "FAILURE", "error": payout.error}
