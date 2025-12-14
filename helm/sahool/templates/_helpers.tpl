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
