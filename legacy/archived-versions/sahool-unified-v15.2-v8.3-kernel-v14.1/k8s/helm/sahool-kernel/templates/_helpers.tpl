{{- define "sahool.name" -}}
sahool
{{- end -}}

{{- define "sahool.fullname" -}}
{{- printf "%s" .Release.Name -}}
{{- end -}}

{{- define "sahool.labels" -}}
app.kubernetes.io/name: {{ include "sahool.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | quote }}
{{- end -}}

{{/*
Return image for a service.
*/}}
{{- define "sahool.image" -}}
{{- $svc := .svc -}}
{{- $root := .root -}}
{{- if $svc.image }}
{{- $svc.image -}}
{{- else -}}
{{- printf "%s/%s:%s" $root.Values.image.repository $svc.name $root.Values.image.tag -}}
{{- end -}}
{{- end -}}

{{/*
Workload (Deployment or Rollout) for a service.
*/}}
{{- define "sahool.workload" -}}
{{- $root := .root -}}
{{- $svc := .svc -}}
{{- if $svc.enabled }}
{{- $useRollout := and $root.Values.rollouts.enabled (default true $svc.rollout.enabled) -}}
apiVersion: {{- if $useRollout -}} argoproj.io/v1alpha1 {{- else -}} apps/v1 {{- end }}
kind: {{- if $useRollout -}} Rollout {{- else -}} Deployment {{- end }}
metadata:
  name: {{ include "sahool.fullname" $root }}-{{ $svc.name }}
  labels:
    {{- include "sahool.labels" $root | nindent 4 }}
    sahool/service: {{ $svc.name }}
spec:
  replicas: {{ default 1 $svc.replicas }}
  revisionHistoryLimit: {{ default 2 $root.Values.rollouts.revisionHistoryLimit }}
  selector:
    matchLabels:
      app: {{ include "sahool.fullname" $root }}-{{ $svc.name }}
  template:
    metadata:
      labels:
        app: {{ include "sahool.fullname" $root }}-{{ $svc.name }}
        sahool/service: {{ $svc.name }}
      {{- if $root.Values.prometheus.scrape }}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: {{ $svc.port | quote }}
        prometheus.io/path: {{ default "/metrics" $svc.metricsPath | quote }}
      {{- end }}
    spec:
      securityContext:
        runAsNonRoot: true
      containers:
        - name: {{ $svc.name }}
          image: {{ include "sahool.image" (dict "svc" $svc "root" $root) }}
          imagePullPolicy: {{ $root.Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ $svc.port }}
          env:
            - name: SERVICE_NAME
              value: {{ $svc.name | quote }}
            - name: PORT
              value: {{ $svc.port | quote }}
            {{- range $k, $v := $root.Values.env }}
            - name: {{ $k }}
              value: {{ $v | quote }}
            {{- end }}
            {{- range $k, $v := $svc.env }}
            - name: {{ $k }}
              value: {{ $v | quote }}
            {{- end }}
          readinessProbe:
            httpGet:
              path: {{ default "/healthz" $svc.healthPath | quote }}
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 6
          livenessProbe:
            httpGet:
              path: {{ default "/healthz" $svc.healthPath | quote }}
              port: http
            initialDelaySeconds: 15
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 6
          resources:
            {{- toYaml (default $root.Values.resources $svc.resources) | nindent 12 }}

{{- if $useRollout }}
  strategy:
    canary:
      maxSurge: {{ default "25%" $root.Values.rollouts.canary.maxSurge | quote }}
      maxUnavailable: {{ default 0 $root.Values.rollouts.canary.maxUnavailable }}
      {{- if $root.Values.rollouts.analysis.enabled }}
      analysis:
        templates:
          - templateName: {{ include "sahool.fullname" $root }}-{{ $svc.name }}-analysis
        args:
          - name: namespace
            value: {{ $root.Release.Namespace | quote }}
          - name: podRegex
            value: {{ printf "%s-%s.*" (include "sahool.fullname" $root) $svc.name | quote }}
      {{- end }}
      steps:
        {{- range $i, $s := $root.Values.rollouts.canary.steps }}
        - setWeight: {{ $s.setWeight }}
        {{- if $s.pause }}
        - pause:
            duration: {{ $s.pause.duration | quote }}
        {{- end }}
        {{- if and $root.Values.rollouts.analysis.enabled (default true $s.analysis) }}
        - analysis:
            templates:
              - templateName: {{ include "sahool.fullname" $root }}-{{ $svc.name }}-analysis
            args:
              - name: namespace
                value: {{ $root.Release.Namespace | quote }}
              - name: podRegex
                value: {{ printf "%s-%s.*" (include "sahool.fullname" $root) $svc.name | quote }}
        {{- end }}
        {{- end }}
{{- end }}
---
{{- end }}
{{- end -}}

{{/*
ClusterIP service for a service.
*/}}
{{- define "sahool.svc" -}}
{{- $root := .root -}}
{{- $svc := .svc -}}
{{- if $svc.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "sahool.fullname" $root }}-{{ $svc.name }}
  labels:
    {{- include "sahool.labels" $root | nindent 4 }}
    sahool/service: {{ $svc.name }}
spec:
  type: ClusterIP
  selector:
    app: {{ include "sahool.fullname" $root }}-{{ $svc.name }}
  ports:
    - name: http
      port: {{ $svc.port }}
      targetPort: http
---
{{- end }}
{{- end -}}
