app.post('/checkout', async (ctx) => {
  const event = ctx.get('wideEvent');
  const user = ctx.get('user');

  // Add user context
  event.user = {
    id: user.id,
    subscription: user.subscription,
    account_age_days: daysSince(user.createdAt),
    lifetime_value_cents: user.ltv,
  };

  // Add business context as you process
  const cart = await getCart(user.id);
  event.cart = {
    id: cart.id,
    item_count: cart.items.length,
    total_cents: cart.total,
    coupon_applied: cart.coupon?.code,
  };

  // Process payment
  const paymentStart = Date.now();
  const payment = await processPayment(cart, user);

  event.payment = {
    method: payment.method,
    provider: payment.provider,
    latency_ms: Date.now() - paymentStart,
    attempt: payment.attemptNumber,
  };

  // If payment fails, add error details
  if (payment.error) {
    event.error = {
      type: 'PaymentError',
      code: payment.error.code,
      stripe_decline_code: payment.error.declineCode,
    };
  }

  return ctx.json({ orderId: payment.orderId });
});