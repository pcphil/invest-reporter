"""
Checkout endpoint example using WideEventMiddleware pattern.
Converts the TypeScript test.ts example to Python/FastAPI.
"""

from fastapi import FastAPI, Request
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

# Mock data structures
class User:
    def __init__(self, id: str, subscription: str, created_at: datetime, ltv: int):
        self.id = id
        self.subscription = subscription
        self.created_at = created_at
        self.ltv = ltv

class CartItem:
    def __init__(self, name: str, price: int):
        self.name = name
        self.price = price

class Cart:
    def __init__(self, id: str, items: list[CartItem], coupon: dict = None):
        self.id = id
        self.items = items
        self.coupon = coupon
        self.total = sum(item.price for item in items)

class PaymentResult:
    def __init__(self, method: str, provider: str, attempt: int, order_id: str = None, error: dict = None):
        self.method = method
        self.provider = provider
        self.attempt = attempt
        self.order_id = order_id
        self.error = error

# Helper functions
def days_since(date: datetime) -> int:
    """Calculate days since a given date."""
    return (datetime.now() - date).days

async def get_user(user_id: str) -> User:
    """Mock: Fetch user from database."""
    return User(
        id=user_id,
        subscription="premium",
        created_at=datetime.now() - timedelta(days=365),
        ltv=50000
    )

async def get_cart(user_id: str) -> Cart:
    """Mock: Fetch user's cart."""
    items = [
        CartItem("Widget", 2999),
        CartItem("Gadget", 4999),
    ]
    return Cart(
        id=f"cart-{user_id}",
        items=items,
        coupon={"code": "SAVE10", "discount_percent": 10}
    )

async def process_payment(cart: Cart, user: User) -> PaymentResult:
    """Mock: Process payment through payment provider."""
    # Simulate payment processing
    await asyncio.sleep(0.1)
    
    # Mock successful payment
    return PaymentResult(
        method="credit_card",
        provider="stripe",
        attempt=1,
        order_id=f"order-{int(time.time())}"
    )

# Checkout endpoint using WideEventMiddleware
@app.post('/checkout')
async def checkout(request: Request):
    """
    Checkout endpoint that adds business context to wide_event as it processes.
    Demonstrates the wide_event pattern for comprehensive request tracking.
    """
    event = request.state.wide_event
    
    # Mock user (in real app, extract from auth token)
    user_id = request.headers.get('user-id', 'user-123')
    user = await get_user(user_id)
    
    # Add user context to event
    event['user'] = {
        'id': user.id,
        'subscription': user.subscription,
        'account_age_days': days_since(user.created_at),
        'lifetime_value_cents': user.ltv,
    }
    
    # Add business context as you process
    cart = await get_cart(user.id)
    event['cart'] = {
        'id': cart.id,
        'item_count': len(cart.items),
        'total_cents': cart.total,
        'coupon_applied': cart.coupon['code'] if cart.coupon else None,
    }
    
    # Process payment
    payment_start = time.time()
    payment = await process_payment(cart, user)
    
    event['payment'] = {
        'method': payment.method,
        'provider': payment.provider,
        'latency_ms': (time.time() - payment_start) * 1000,
        'attempt': payment.attempt,
    }
    
    # If payment fails, add error details
    if payment.error:
        event['error'] = {
            'type': 'PaymentError',
            'code': payment.error.get('code'),
            'stripe_decline_code': payment.error.get('decline_code'),
        }
        logger.error(f"Payment failed: {payment.error}")
        return {'error': 'Payment processing failed'}, 400
    
    logger.info(f"Checkout completed for user {user.id}")
    return {'order_id': payment.order_id}


# Alternative: Using add_event_data_batch for cleaner code
@app.post('/checkout/v2')
async def checkout_v2(request: Request):
    """
    Checkout endpoint using add_event_data_batch helper for more concise code.
    """
    import asyncio
    
    user_id = request.headers.get('user-id', 'user-123')
    user = await get_user(user_id)
    
    # Add user context
    request.state.add_event_data('user', {
        'id': user.id,
        'subscription': user.subscription,
        'account_age_days': days_since(user.created_at),
        'lifetime_value_cents': user.ltv,
    })
    
    # Add cart context
    cart = await get_cart(user.id)
    request.state.add_event_data('cart', {
        'id': cart.id,
        'item_count': len(cart.items),
        'total_cents': cart.total,
        'coupon_applied': cart.coupon['code'] if cart.coupon else None,
    })
    
    # Process payment
    payment_start = time.time()
    payment = await process_payment(cart, user)
    
    # Add payment context
    request.state.add_event_data('payment', {
        'method': payment.method,
        'provider': payment.provider,
        'latency_ms': (time.time() - payment_start) * 1000,
        'attempt': payment.attempt,
    })
    
    # Handle payment error
    if payment.error:
        request.state.add_event_data('error', {
            'type': 'PaymentError',
            'code': payment.error.get('code'),
            'stripe_decline_code': payment.error.get('decline_code'),
        })
        return {'error': 'Payment processing failed'}, 400
    
    return {'order_id': payment.order_id}


if __name__ == '__main__':
    import uvicorn
    import asyncio
    
    uvicorn.run(app, host='0.0.0.0', port=8001)
