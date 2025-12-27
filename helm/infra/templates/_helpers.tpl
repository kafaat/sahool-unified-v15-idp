{{/*
Expand the name of the chart.
*/}}
{{- define "infra.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "infra.fullname" -}}
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
{{- define "infra.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "infra.labels" -}}
helm.sh/chart: {{ include "infra.chart" . }}
{{ include "infra.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: sahool
environment: {{ .Values.environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "infra.selectorLabels" -}}
app.kubernetes.io/name: {{ include "infra.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
PostgreSQL labels
*/}}
{{- define "infra.postgresql.labels" -}}
{{ include "infra.labels" . }}
app.kubernetes.io/component: postgresql
{{- end }}

{{/*
PostgreSQL selector labels
*/}}
{{- define "infra.postgresql.selectorLabels" -}}
app.kubernetes.io/name: sahool-postgresql
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: postgresql
{{- end }}

{{/*
Redis labels
*/}}
{{- define "infra.redis.labels" -}}
{{ include "infra.labels" . }}
app.kubernetes.io/component: redis
{{- end }}

{{/*
Redis selector labels
*/}}
{{- define "infra.redis.selectorLabels" -}}
app.kubernetes.io/name: sahool-redis
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: redis
{{- end }}

{{/*
NATS labels
*/}}
{{- define "infra.nats.labels" -}}
{{ include "infra.labels" . }}
app.kubernetes.io/component: nats
{{- end }}

{{/*
NATS selector labels
*/}}
{{- define "infra.nats.selectorLabels" -}}
app.kubernetes.io/name: sahool-nats
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/component: nats
{{- end }}

{{/*
Return the PostgreSQL secret name
*/}}
{{- define "infra.postgresql.secretName" -}}
{{- if .Values.postgresql.auth.existingSecret }}
{{- .Values.postgresql.auth.existingSecret }}
{{- else }}
{{- printf "%s-postgresql-secret" (include "infra.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Return the Redis secret name
*/}}
{{- define "infra.redis.secretName" -}}
{{- if .Values.redis.auth.existingSecret }}
{{- .Values.redis.auth.existingSecret }}
{{- else }}
{{- printf "%s-redis-secret" (include "infra.fullname" .) }}
{{- end }}
{{- end }}

{{/*
Return the namespace
*/}}
{{- define "infra.namespace" -}}
{{- if .Values.namespace.create }}
{{- .Values.namespace.name }}
{{- else }}
{{- .Release.Namespace }}
{{- end }}
{{- end }}
