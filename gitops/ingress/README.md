# Ingress for PR Preview URLs

Requirements:

- DNS wildcard: \*.sahool.internal -> Ingress LB IP
- cert-manager installed

Apply:

- ingress-nginx app
- cert-manager app
- cluster-issuer

Helm will create Ingress per PR environment automatically.
