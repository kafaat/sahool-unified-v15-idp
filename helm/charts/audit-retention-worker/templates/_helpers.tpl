{{/*
Expand the name of the chart.
*/}}
{{- define "audit-retention-worker.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully qualified app name.
*/}}
{{- define "audit-retention-worker.fullname" -}}
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

{{- define "audit-retention-worker.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "audit-retention-worker.labels" -}}
helm.sh/chart: {{ include "audit-retention-worker.chart" . }}
{{ include "audit-retention-worker.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: cronjob-worker
app.kubernetes.io/part-of: sahool
environment: {{ .Values.environment }}
deploymentSlot: {{ .Values.deploymentSlot }}
{{- end }}

{{- define "audit-retention-worker.selectorLabels" -}}
app.kubernetes.io/name: {{ include "audit-retention-worker.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "audit-retention-worker.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "audit-retention-worker.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
