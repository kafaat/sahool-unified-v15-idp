{{/*
Expand the name of the chart.
*/}}
{{- define "yolo26-vision-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "yolo26-vision-service.fullname" -}}
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
{{- define "yolo26-vision-service.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "yolo26-vision-service.labels" -}}
helm.sh/chart: {{ include "yolo26-vision-service.chart" . }}
{{ include "yolo26-vision-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: vision
app.kubernetes.io/part-of: sahool
environment: {{ .Values.environment }}
deploymentSlot: {{ .Values.deploymentSlot }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "yolo26-vision-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "yolo26-vision-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "yolo26-vision-service.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "yolo26-vision-service.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
