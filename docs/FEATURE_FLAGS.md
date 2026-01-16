# Feature Flags + Experiments

Included components:

- OpenFeature SDK guidance (app-side)
- `flagd` (lightweight) as a local flag provider
- GitOps install manifests for `flagd`
- Suggested A/B experiments model (tenant cohort + percentage rollout)

## How to use

- Services read flags via OpenFeature
- Flags are configured in flagd ConfigMap (GitOps)
- Combine with Rollouts for progressive delivery

## Next steps

- Replace flagd with Unleash or LaunchDarkly if desired
- Add experiment assignment service (optional)
