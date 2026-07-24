# Redis Cache

## Usage
Used for: session storage, auth signing key cache, rate limiting counters,
checkout cart cache.

## Known issue: Memory eviction causing cart data loss
Redis is configured with `maxmemory-policy=allkeys-lru`, which means under
memory pressure it evicts the LEAST RECENTLY USED keys — including active
shopping carts, not just expired sessions. This causes users to see an
empty cart randomly during high-traffic periods.

### Fix
Move cart data to a separate Redis instance/db with a stricter eviction
policy (`volatile-lru`, only evicting keys with a TTL set), or move cart
storage to Postgres entirely since it doesn't need Redis-level latency.

## Known issue: Connection pool exhaustion under load
Each service instance opens its own Redis connection pool. Under traffic
spikes with many pod replicas, total connections can exceed Redis's
`maxclients` limit (default 10000), causing connection refused errors.
