# Alertmanager Config Overrides (SAHOOL Platform)

> **Context**: `infrastructure/monitoring/alertmanager/alertmanager.yml` ships with sensible
> defaults (e.g. `compliance@sahool.io`, `#sahool-audit-compliance`, standard SMTP) but
> real deployments need environment-specific values — different SMTP hosts, Slack webhook
> URLs, PagerDuty service keys.
>
> Before 2026-04-18 the file used `${VAR:-default}` syntax expecting shell-style
> env substitution. Alertmanager does **not** perform that substitution, and the
> docker-compose mount has no envsubst preprocessing — every placeholder was being
> sent as a literal string to SMTP/Slack/PagerDuty, silently failing delivery.
> That PR removed the broken syntax; per-env overrides now require an explicit
> templating layer. This doc covers the three supported workflows.

---

## Which env vars override what

> **Important — these env vars do nothing on their own.** Setting `SMTP_*`,
> `SLACK_WEBHOOK_URL`, `PAGERDUTY_SERVICE_KEY`, etc. in `.env` or the
> Alertmanager container environment does **not** change alert delivery by
> itself. Alertmanager does not read these names automatically, and this stack
> does not run `envsubst` over `alertmanager.yml`. To apply any override
> below, render it into the final config via one of the workflows in this
> document (envsubst wrapper, init container, or Helm/kustomize).

All names are conventions — not auto-consumed by Alertmanager.

| Env var | Default | Used by receiver(s) |
|---|---|---|
| `SMTP_HOST` | `smtp.gmail.com` | global (all email) |
| `SMTP_PORT` | `587` | global (all email) |
| `SMTP_USERNAME` | *(empty)* | global (all email) |
| `SMTP_PASSWORD` | *(empty)* | global (all email) |
| `SLACK_WEBHOOK_URL` | *(empty)* | global (all slack) |
| `ALERT_EMAIL_AUDIT` | `compliance@sahool.io,sre@sahool.io` | audit-compliance-team |
| `SLACK_CHANNEL_AUDIT` | `#sahool-audit-compliance` | audit-compliance-team |
| `PAGERDUTY_AUDIT_KEY` | *(empty)* | audit-compliance-team |
| `ALERT_EMAIL_DEFAULT` | `devops@sahool.io` | default-notifications |
| `SLACK_CHANNEL_DEFAULT` | `#sahool-alerts` | default-notifications |
| `ALERT_EMAIL_CRITICAL` | `sre@sahool.io,devops@sahool.io` | critical-infrastructure, critical-alerts |
| `SLACK_CHANNEL_CRITICAL` | `#sahool-critical` | critical-infrastructure, critical-alerts |
| `PAGERDUTY_SERVICE_KEY` | *(empty)* | critical-infrastructure |
| `ALERT_EMAIL_DATABASE` | `dba@sahool.io,devops@sahool.io` | database-team |
| `SLACK_CHANNEL_DATABASE` | `#sahool-database` | database-team |
| `ALERT_EMAIL_PERFORMANCE` | `performance@sahool.io` | performance-team |
| `SLACK_CHANNEL_PERFORMANCE` | `#sahool-performance` | performance-team |
| `ALERT_EMAIL_AI_ML` | `ai-team@sahool.io` | ai-ml-team |
| `SLACK_CHANNEL_AI_ML` | `#sahool-ai-ml` | ai-ml-team |
| `ALERT_EMAIL_WARNINGS` | `devops@sahool.io` | warning-notifications |
| `SLACK_CHANNEL_WARNINGS` | `#sahool-warnings` | warning-notifications |
| `ALERT_EMAIL_INFO` | `monitoring@sahool.io` | info-notifications |
| `SLACK_CHANNEL_INFO` | `#sahool-info` | info-notifications |

> **PagerDuty blocks are commented out in the committed default**. Alertmanager
> rejects `service_key: ''` at config-check time, so the two `pagerduty_configs`
> stanzas (`audit-compliance-team`, `critical-infrastructure`) are shipped as
> YAML comments. Your templating layer must uncomment and inject the real key
> (`PAGERDUTY_AUDIT_KEY`, `PAGERDUTY_SERVICE_KEY`) before the final file is
> mounted — `grep -n pagerduty_configs alertmanager.yml` should return two
> uncommented lines in a working render.

---

## Workflow A — envsubst wrapper (docker-compose)

Simplest pre-deploy step; keeps the file template-free in git.

1. Rename `alertmanager.yml` to `alertmanager.yml.tmpl` in a deployment checkout
   (not in git — this is a local rendering step).
2. Substitute back with `${VAR}` references at the values you want to override.
3. Add a one-off render before `docker compose up`:

```bash
# render-alertmanager.sh
# Load KEY=value overrides from .env.alerting safely — `set -a` auto-exports
# every variable assigned by the sourced file, and the shell's own parser
# handles quoting, spaces, and `#` comments correctly (unlike the brittle
# `export $(grep ... | xargs)` idiom).
set -a
. ./.env.alerting
set +a
envsubst < infrastructure/monitoring/alertmanager/alertmanager.yml.tmpl \
  > infrastructure/monitoring/alertmanager/alertmanager.yml
docker compose -f infrastructure/monitoring/docker-compose.monitoring.yml up -d alertmanager
```

**Pros**: no new container, no Helm dep.
**Cons**: manual step; the rendered file shouldn't be committed.

---

## Workflow B — init container (docker-compose, Compose v2.20+)

Let Docker Compose do the substitution at deploy time without human intervention.

```yaml
# Additions to infrastructure/monitoring/docker-compose.monitoring.yml
services:
  alertmanager-config-render:
    image: alpine:3.19
    command:
      - sh
      - -c
      - |
        apk add --no-cache gettext &&
        envsubst < /src/alertmanager.yml.tmpl > /rendered/alertmanager.yml
    volumes:
      - ./alertmanager:/src:ro
      - alertmanager-rendered:/rendered
    environment:
      SMTP_HOST: ${SMTP_HOST:-smtp.gmail.com}
      SMTP_PORT: ${SMTP_PORT:-587}
      # ... rest of env vars from the table above

  alertmanager:
    # existing config ...
    depends_on:
      alertmanager-config-render:
        condition: service_completed_successfully
    volumes:
      - alertmanager-rendered:/etc/alertmanager:ro

volumes:
  alertmanager-rendered:
```

Ship alertmanager.yml as `alertmanager.yml.tmpl` in the `alertmanager/` directory
alongside this compose addition.

**Pros**: idempotent, fully CI-reproducible, uses env vars directly from compose.
**Cons**: adds a container startup; `.tmpl` file diverges from the committed `.yml`.

---

## Workflow C — Helm / kustomize (Kubernetes)

If you're deploying to a Kubernetes cluster, prefer Helm's templating or a
kustomize overlay. Example Helm chart structure:

```
charts/monitoring/
├── Chart.yaml
├── values.yaml            # contains smtp.host, slack.webhookUrl, etc.
└── templates/
    └── alertmanager-config.yaml   # ConfigMap, templated from values
```

Where `templates/alertmanager-config.yaml` does:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
data:
  alertmanager.yml: |
    global:
      smtp_smarthost: '{{ .Values.smtp.host }}:{{ .Values.smtp.port }}'
      smtp_auth_username: '{{ .Values.smtp.username }}'
      # ... and so on
    receivers:
      - name: audit-compliance-team
        email_configs:
          - to: '{{ .Values.receivers.audit.email }}'
        slack_configs:
          - channel: '{{ .Values.receivers.audit.slackChannel }}'
```

**Pros**: proper config-as-code, works with ArgoCD / Flux.
**Cons**: ~200 LOC of templates; investment only worth it for K8s deployments.

---

## Why not `--config.expand-env`?

Alertmanager does ship a `--config.expand-env` flag. Two reasons we don't use it:

1. **Doesn't support `:-default` syntax.** It uses Go's `os.ExpandEnv`, which
   only handles `${VAR}` and `$VAR` — no defaults. Unset vars become empty strings
   silently. That's worse than the current literal-default approach, which at least
   lets a human reader see what the intended default is.
2. **Doesn't cover nested references.** `'${PAGERDUTY_AUDIT_KEY:-${PAGERDUTY_SERVICE_KEY:-}}'`
   (a pattern we had) would never work.

If you want `${VAR}` without defaults on a file you're willing to keep simple,
`--config.expand-env` is a valid alternative to the workflows above.

---

## Smoke check after any change

```bash
# Parse check (any YAML tool)
python -c "import yaml; yaml.safe_load(open('alertmanager.yml'))"

# Alertmanager-specific validation (requires amtool)
amtool check-config alertmanager.yml
```

If `amtool` complains about an unresolved `${...}` placeholder in the literal
file, your render step didn't run.
