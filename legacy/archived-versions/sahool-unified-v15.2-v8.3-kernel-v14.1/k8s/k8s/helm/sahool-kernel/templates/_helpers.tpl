{{- define "sahool.name" -}}
sahool-kernel
{{- end -}}
{{- define "sahool.labels" -}}
app.kubernetes.io/name: {{ include "sahool.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end -}}
