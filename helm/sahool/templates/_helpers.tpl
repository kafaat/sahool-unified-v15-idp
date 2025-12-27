{{/*
Expand the name of the chart.
*/}}
{{- define "sahool.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "sahool.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "sahool.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "sahool.labels" -}}
helm.sh/chart: {{ include "sahool.chart" . }}
{{ include "sahool.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "sahool.selectorLabels" -}}
app.kubernetes.io/name: {{ include "sahool.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "sahool.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "sahool.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database URL
*/}}
{{- define "sahool.databaseUrl" -}}
{{- if .Values.postgresql.enabled }}
postgres://{{ .Values.postgresql.auth.username }}:{{ .Values.postgresql.auth.password }}@{{ include "sahool.fullname" . }}-postgresql:5432/{{ .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalDatabase.url }}
{{- end }}
{{- end }}

{{/*
NATS URL
*/}}
{{- define "sahool.natsUrl" -}}
{{- if .Values.nats.enabled }}
nats://{{ include "sahool.fullname" . }}-nats:4222
{{- else }}
{{- .Values.externalNats.url }}
{{- end }}
{{- end }}

{{/*
Redis URL
*/}}
{{- define "sahool.redisUrl" -}}
{{- if .Values.redis.enabled }}
redis://{{ include "sahool.fullname" . }}-redis-master:6379/0
{{- else }}
{{- .Values.externalRedis.url }}
{{- end }}
{{- end }}

{{/*
Service-specific fullname
Usage: {{ include "sahool.service.fullname" (dict "root" . "service" .Values.services.fieldCore) }}
*/}}
{{- define "sahool.service.fullname" -}}
{{- $root := .root -}}
{{- $service := .service -}}
{{- printf "%s-%s" (include "sahool.fullname" $root) $service.name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Service-specific labels
Usage: {{ include "sahool.service.labels" (dict "root" . "service" .Values.services.fieldCore) }}
*/}}
{{- define "sahool.service.labels" -}}
{{- $root := .root -}}
{{- $service := .service -}}
{{ include "sahool.labels" $root }}
app.kubernetes.io/component: {{ $service.name }}
sahool.io/package: {{ $service.package }}
{{- end }}

{{/*
Service-specific selector labels
*/}}
{{- define "sahool.service.selectorLabels" -}}
{{- $root := .root -}}
{{- $service := .service -}}
{{ include "sahool.selectorLabels" $root }}
app.kubernetes.io/component: {{ $service.name }}
{{- end }}

{{/*
Image name with registry
Usage: {{ include "sahool.image" (dict "root" . "service" .Values.services.fieldCore) }}
*/}}
{{- define "sahool.image" -}}
{{- $root := .root -}}
{{- $service := .service -}}
{{- $registry := $root.Values.global.imageRegistry -}}
{{- $repository := $service.image.repository -}}
{{- $tag := $service.image.tag | default $root.Chart.AppVersion -}}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry $repository $tag }}
{{- else }}
{{- printf "%s:%s" $repository $tag }}
{{- end }}
{{- end }}

{{/*
Environment variables - Common
*/}}
{{- define "sahool.commonEnv" -}}
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: sahool-database-secret
      key: url
- name: REDIS_URL
  valueFrom:
    secretKeyRef:
      name: sahool-redis-secret
      key: url
- name: NATS_URL
  value: {{ include "sahool.natsUrl" . }}
- name: JWT_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: {{ .Values.security.jwt.existingSecret }}
      key: secret-key
- name: LOG_LEVEL
  valueFrom:
    configMapKeyRef:
      name: sahool-config
      key: LOG_LEVEL
- name: NODE_ENV
  valueFrom:
    configMapKeyRef:
      name: sahool-config
      key: NODE_ENV
- name: TZ
  valueFrom:
    configMapKeyRef:
      name: sahool-config
      key: TZ
{{- end }}

{{/*
Health check - Liveness probe
*/}}
{{- define "sahool.livenessProbe" -}}
{{- $service := . -}}
livenessProbe:
  httpGet:
    path: /healthz
    port: {{ $service.port }}
    scheme: HTTP
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
{{- end }}

{{/*
Health check - Readiness probe
*/}}
{{- define "sahool.readinessProbe" -}}
{{- $service := . -}}
readinessProbe:
  httpGet:
    path: /ready
    port: {{ $service.port }}
    scheme: HTTP
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  successThreshold: 1
  failureThreshold: 3
{{- end }}

{{/*
Security Context - Pod level
*/}}
{{- define "sahool.podSecurityContext" -}}
runAsNonRoot: true
runAsUser: 1000
fsGroup: 1000
seccompProfile:
  type: RuntimeDefault
{{- end }}

{{/*
Security Context - Container level
*/}}
{{- define "sahool.securityContext" -}}
allowPrivilegeEscalation: false
capabilities:
  drop:
    - ALL
readOnlyRootFilesystem: true
runAsNonRoot: true
runAsUser: 1000
{{- end }}

{{/*
Resource limits
Usage: {{ include "sahool.resources" .Values.services.fieldCore }}
*/}}
{{- define "sahool.resources" -}}
{{- $service := . -}}
resources:
  limits:
    cpu: {{ $service.resources.limits.cpu }}
    memory: {{ $service.resources.limits.memory }}
  requests:
    cpu: {{ $service.resources.requests.cpu }}
    memory: {{ $service.resources.requests.memory }}
{{- end }}

{{/*
Check if service should be deployed based on package tier
Usage: {{ include "sahool.shouldDeploy" (dict "root" . "service" .Values.services.fieldCore) }}
*/}}
{{- define "sahool.shouldDeploy" -}}
{{- $root := .root -}}
{{- $service := .service -}}
{{- $packageTier := $root.Values.packageTier -}}
{{- $servicePackage := $service.package -}}
{{- if and $service.enabled (or (eq $servicePackage "starter") (and (eq $packageTier "professional") (or (eq $servicePackage "starter") (eq $servicePackage "professional"))) (and (eq $packageTier "enterprise") (or (eq $servicePackage "starter") (eq $servicePackage "professional") (eq $servicePackage "enterprise")))) -}}
true
{{- else -}}
false
{{- end }}
{{- end }}
