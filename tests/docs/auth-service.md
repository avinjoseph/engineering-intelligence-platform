# Auth Service

## Token expiry
Access tokens are valid for 15 minutes. Refresh tokens are valid for 30 days.

## Known issue: Login failures spike after deploy
Login failures spike right after a deploy because the JWT signing key cache
isn't invalidated automatically. Users with tokens signed by the old key get
401 errors until the cache expires (default TTL: 10 minutes).

### Fix
Manually flush the signing key cache in Redis after every deploy:
`redis-cli DEL auth:signing_keys`. Consider automating this as a post-deploy
hook.

## Known issue: High latency on /login endpoint
The /login endpoint calls out to the fraud-detection service synchronously,
which adds 200-400ms under normal load and can spike to 2s+ if
fraud-detection is under load itself. Consider making this call async or
adding a circuit breaker.
