# Kubernetes Deployment Runbook

## Rolling deploys
All services use rolling deployment strategy with maxSurge=1, maxUnavailable=0.
This means zero-downtime deploys under normal conditions.

## Known issue: Pods stuck in CrashLoopBackOff after deploy
Usually caused by one of:
1. A failing readiness/liveness probe (check `kubectl describe pod`)
2. A missing environment variable or secret after a config change
3. An out-of-memory kill (check `kubectl logs --previous` for OOMKilled)

### Fix
Run `kubectl describe pod <pod-name>` first — the Events section almost
always names the exact cause. Roll back with
`kubectl rollout undo deployment/<name>` if the fix isn't immediately clear.

## Known issue: Deploy stuck at "1/2 pods ready"
Often means the new pod's readiness probe is failing due to a slow startup
(e.g. warming a cache, running migrations). Increase
`readinessProbe.initialDelaySeconds` if this is expected behavior, not a bug.
