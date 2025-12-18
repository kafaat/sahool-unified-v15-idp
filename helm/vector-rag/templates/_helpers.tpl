{{/*
Expand the name of the chart.
*/}}
{{- define "vector-rag.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "vector-rag.fullname" -}}
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
{{- define "vector-rag.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "vector-rag.labels" -}}
helm.sh/chart: {{ include "vector-rag.chart" . }}
{{ include "vector-rag.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: sahool-platform
{{- end }}

{{/*
Selector labels
*/}}
{{- define "vector-rag.selectorLabels" -}}
app.kubernetes.io/name: {{ include "vector-rag.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Vector Service labels
*/}}
{{- define "vector-rag.vectorService.labels" -}}
{{ include "vector-rag.labels" . }}
app.kubernetes.io/component: vector-service
{{- end }}

{{/*
Vector Service selector labels
*/}}
{{- define "vector-rag.vectorService.selectorLabels" -}}
{{ include "vector-rag.selectorLabels" . }}
app.kubernetes.io/component: vector-service
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "vector-rag.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "vector-rag.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Secret name for internal API key
*/}}
{{- define "vector-rag.secretName" -}}
{{- if .Values.secrets.internalApiKey.existingSecret }}
{{- .Values.secrets.internalApiKey.existingSecret }}
{{- else }}
{{- include "vector-rag.fullname" . }}-secrets
{{- end }}
{{- end }}

{{/*
Milvus host
*/}}
{{- define "vector-rag.milvusHost" -}}
{{- if .Values.milvus.enabled }}
{{- printf "%s-milvus" .Release.Name }}
{{- else }}
{{- .Values.vectorService.env.MILVUS_HOST }}
{{- end }}
{{- end }}
