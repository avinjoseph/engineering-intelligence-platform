# Payments Service

## Overview
Handles all payment processing via Stripe. Depends on: checkout-service,
fraud-detection, PostgreSQL (payments_db).

## Known issue: Duplicate charges
Duplicate charges can occur when the client retries a payment request after
a timeout, even though the original request succeeded server-side. This is
caused by the retry logic not checking for an existing idempotency key.

### Fix
Always pass an `Idempotency-Key` header on payment creation requests. The
payments service deduplicates based on this key within a 24-hour window.

## Known issue: Webhook delivery delays
Stripe webhook events (payment succeeded, payment failed) can arrive up to
5 minutes late during high load. Do not rely on webhook timing for
user-facing confirmation — poll the payment status endpoint instead for
immediate feedback.

## Database connection pool
max_connections=30 (lower than checkout-service since payment volume is lower)
