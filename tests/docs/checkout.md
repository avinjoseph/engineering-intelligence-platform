# Checkout Service

## Database connection pool
max_connections=50

## Known issue: High latency
High latency happens when the DB pool is exhausted. This typically occurs
during traffic spikes when more than 50 concurrent connections are requested.

### Fix
Increase pool size. Update `max_connections` in the checkout-service config
and redeploy. Monitor pool utilization in Grafana after the change.

## Known issue: 502 errors after deploy
502 errors immediately after a deploy usually mean the readiness probe is
failing because the DB migration hasn't finished. Wait for migration
completion before routing traffic, or increase the readiness probe delay.