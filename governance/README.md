# SAHOOL Governance Pack v1

هذا المجلد يفرض حوكمة المنصة تلقائيًا عبر:

- **Kyverno** (Policy as Code)
- **GitOps** (ArgoCD)
- **CI Guards**
- **Backstage Templates**

## القواعد المفروضة

| القاعدة                     | الوصف                      |
| --------------------------- | -------------------------- |
| `restrict-latest-tag`       | منع استخدام `image:latest` |
| `require-resource-limits`   | فرض تحديد CPU/Memory       |
| `require-governance-labels` | فرض labels الحوكمة         |
| `baseline-security`         | منع privileged containers  |

## Labels المطلوبة

```yaml
sahool.io/owner: "<owner>"
sahool.io/team: "<team>"
sahool.io/lifecycle: "experimental|internal|production|deprecated|retired"
sahool.io/tier: "tier-1|tier-2|tier-3"
```

## الهيكل

```
governance/
├── policies/kyverno/     # سياسات Kyverno
├── schemas/              # JSON Schemas
└── templates/            # Backstage Templates
```

## التطبيق

السياسات تُطبَّق تلقائيًا عبر ArgoCD من:

```
gitops/argocd/applications/sahool-governance-policies.yaml
```

أي خدمة بدون Owner/Lifecycle/Tier سيتم منعها.
