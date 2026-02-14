#!/usr/bin/env bash
# =============================================================================
# SAHOOL Helm Chart Generator
# =============================================================================
# Generates standardized Helm charts for SAHOOL platform microservices.
#
# Usage:
#   ./scripts/generate-helm-charts.sh <service-name> <port> [type]
#
# Arguments:
#   service-name  Name of the service (e.g., advisory-service)
#   port          Service port number (e.g., 8093)
#   type          Service type: python (default) or node
#
# Examples:
#   ./scripts/generate-helm-charts.sh advisory-service 8093 python
#   ./scripts/generate-helm-charts.sh iot-service 8117 node
#
# The generated chart follows SAHOOL conventions:
#   - Non-root user sahool (UID 1000)
#   - Read-only root filesystem with emptyDir volumes for /tmp and /.cache
#   - Health probes on /healthz and /readyz
#   - Prometheus metrics annotations
#   - Blue-green deployment support
#   - HPA with CPU and memory scaling
#   - PodDisruptionBudget
#   - ConfigMap for non-secret configuration
#   - Secrets referenced (not created) for JWT, DB URL
#   - Pod anti-affinity for HA
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
SERVICE_NAME="${1:?Usage: $0 <service-name> <port> [python|node]}"
SERVICE_PORT="${2:?Usage: $0 <service-name> <port> [python|node]}"
SERVICE_TYPE="${3:-python}"  # python or node

# ---------------------------------------------------------------------------
# Derived values
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CHART_DIR="${REPO_ROOT}/helm/charts/${SERVICE_NAME}"

APP_VERSION="16.0.0"
CHART_VERSION="1.0.0"

# Resource defaults based on service type
if [[ "$SERVICE_TYPE" == "node" ]]; then
  MEMORY_LIMIT="256Mi"
  MEMORY_REQUEST="128Mi"
  CPU_LIMIT="500m"
  CPU_REQUEST="100m"
  COMPONENT_LABEL="node-service"
else
  MEMORY_LIMIT="512Mi"
  MEMORY_REQUEST="128Mi"
  CPU_LIMIT="500m"
  CPU_REQUEST="100m"
  COMPONENT_LABEL="python-service"
fi

# Derive a description from the service name
SERVICE_DESC="SAHOOL $(echo "$SERVICE_NAME" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g') - Microservice"

# Derive a component keyword (first word of service name)
COMPONENT_KEYWORD="$(echo "$SERVICE_NAME" | cut -d'-' -f1)"

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
if [[ -d "$CHART_DIR" ]]; then
  echo "WARNING: Chart directory already exists: ${CHART_DIR}"
  echo "Overwriting existing chart files..."
fi

echo "Generating Helm chart for: ${SERVICE_NAME}"
echo "  Port:       ${SERVICE_PORT}"
echo "  Type:       ${SERVICE_TYPE}"
echo "  Memory:     ${MEMORY_LIMIT} (limit) / ${MEMORY_REQUEST} (request)"
echo "  Output:     ${CHART_DIR}"
echo ""

# ---------------------------------------------------------------------------
# Create directory structure
# ---------------------------------------------------------------------------
mkdir -p "${CHART_DIR}/templates"

# ---------------------------------------------------------------------------
# Chart.yaml
# ---------------------------------------------------------------------------
cat > "${CHART_DIR}/Chart.yaml" <<YAML
apiVersion: v2
name: ${SERVICE_NAME}
description: ${SERVICE_DESC}
type: application
version: ${CHART_VERSION}
appVersion: "${APP_VERSION}"
keywords:
  - sahool
  - ${COMPONENT_KEYWORD}
  - microservice
maintainers:
  - name: KAFAAT
    email: platform@kafaat.sa
YAML

# ---------------------------------------------------------------------------
# values.yaml
# ---------------------------------------------------------------------------
cat > "${CHART_DIR}/values.yaml" <<YAML
# ${SERVICE_DESC}
# Version: ${APP_VERSION}

replicaCount: 2

image:
  repository: ghcr.io/kafaat/sahool/${SERVICE_NAME}
  tag: "${APP_VERSION}"
  pullPolicy: IfNotPresent

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

service:
  type: ClusterIP
  port: ${SERVICE_PORT}

resources:
  limits:
    cpu: ${CPU_LIMIT}
    memory: ${MEMORY_LIMIT}
  requests:
    cpu: ${CPU_REQUEST}
    memory: ${MEMORY_REQUEST}

environment: staging
deploymentSlot: blue

# Environment variables
env:
  LOG_LEVEL: "INFO"

secrets:
  jwtSecret: ""

database:
  url: ""

nats:
  url: ""

redis:
  url: ""

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 75
  targetMemoryUtilizationPercentage: 80

# Pod Disruption Budget
pdb:
  enabled: true
  minAvailable: 1

# Health probes
probes:
  liveness:
    path: /healthz
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
  readiness:
    path: /readyz
    initialDelaySeconds: 15
    periodSeconds: 5
    timeoutSeconds: 3
    failureThreshold: 3

nodeSelector: {}

tolerations: []

# Pod anti-affinity for high availability
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/name
                operator: In
                values:
                  - ${SERVICE_NAME}
          topologyKey: kubernetes.io/hostname

# Pod annotations
podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "${SERVICE_PORT}"
  prometheus.io/path: "/metrics"

# Security context
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: true
YAML

# ---------------------------------------------------------------------------
# templates/_helpers.tpl
# ---------------------------------------------------------------------------
cat > "${CHART_DIR}/templates/_helpers.tpl" <<'HELPERS'
{{/*
Expand the name of the chart.
*/}}
{{- define "SERVICE_NAME_PLACEHOLDER.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "SERVICE_NAME_PLACEHOLDER.fullname" -}}
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
{{- define "SERVICE_NAME_PLACEHOLDER.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "SERVICE_NAME_PLACEHOLDER.labels" -}}
helm.sh/chart: {{ include "SERVICE_NAME_PLACEHOLDER.chart" . }}
{{ include "SERVICE_NAME_PLACEHOLDER.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: COMPONENT_LABEL_PLACEHOLDER
app.kubernetes.io/part-of: sahool
environment: {{ .Values.environment }}
deploymentSlot: {{ .Values.deploymentSlot }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "SERVICE_NAME_PLACEHOLDER.selectorLabels" -}}
app.kubernetes.io/name: {{ include "SERVICE_NAME_PLACEHOLDER.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "SERVICE_NAME_PLACEHOLDER.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "SERVICE_NAME_PLACEHOLDER.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
HELPERS

# Replace placeholder with actual service name in _helpers.tpl
sed -i "s/SERVICE_NAME_PLACEHOLDER/${SERVICE_NAME}/g" "${CHART_DIR}/templates/_helpers.tpl"
sed -i "s/COMPONENT_LABEL_PLACEHOLDER/${COMPONENT_LABEL}/g" "${CHART_DIR}/templates/_helpers.tpl"

# ---------------------------------------------------------------------------
# templates/deployment.yaml
# ---------------------------------------------------------------------------
cat > "${CHART_DIR}/templates/deployment.yaml" <<'DEPLOYMENT'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}
  labels:
    {{- include "SERVICE_NAME_PLACEHOLDER.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "SERVICE_NAME_PLACEHOLDER.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "SERVICE_NAME_PLACEHOLDER.selectorLabels" . | nindent 8 }}
        environment: {{ .Values.environment }}
        deploymentSlot: {{ .Values.deploymentSlot }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "SERVICE_NAME_PLACEHOLDER.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: SERVICE_PORT_PLACEHOLDER
              protocol: TCP
          env:
            - name: ENVIRONMENT
              value: {{ .Values.environment | quote }}
            - name: DEPLOYMENT_SLOT
              value: {{ .Values.deploymentSlot | quote }}
            - name: SERVICE_PORT
              value: "SERVICE_PORT_PLACEHOLDER"
            {{- range $key, $value := .Values.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}-secrets
                  key: jwt-secret
                  optional: true
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}-secrets
                  key: database-url
                  optional: true
            - name: NATS_URL
              valueFrom:
                configMapKeyRef:
                  name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}-config
                  key: NATS_URL
                  optional: true
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}-config
                  key: REDIS_URL
                  optional: true
          livenessProbe:
            httpGet:
              path: {{ .Values.probes.liveness.path }}
              port: http
            initialDelaySeconds: {{ .Values.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.liveness.periodSeconds }}
            timeoutSeconds: {{ .Values.probes.liveness.timeoutSeconds }}
            failureThreshold: {{ .Values.probes.liveness.failureThreshold }}
          readinessProbe:
            httpGet:
              path: {{ .Values.probes.readiness.path }}
              port: http
            initialDelaySeconds: {{ .Values.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.readiness.periodSeconds }}
            timeoutSeconds: {{ .Values.probes.readiness.timeoutSeconds }}
            failureThreshold: {{ .Values.probes.readiness.failureThreshold }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: cache
              mountPath: /.cache
      volumes:
        - name: tmp
          emptyDir: {}
        - name: cache
          emptyDir: {}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
DEPLOYMENT

sed -i "s/SERVICE_NAME_PLACEHOLDER/${SERVICE_NAME}/g" "${CHART_DIR}/templates/deployment.yaml"
sed -i "s/SERVICE_PORT_PLACEHOLDER/${SERVICE_PORT}/g" "${CHART_DIR}/templates/deployment.yaml"

# ---------------------------------------------------------------------------
# templates/service.yaml
# ---------------------------------------------------------------------------
cat > "${CHART_DIR}/templates/service.yaml" <<'SERVICE'
apiVersion: v1
kind: Service
metadata:
  name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}
  labels:
    {{- include "SERVICE_NAME_PLACEHOLDER.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "SERVICE_NAME_PLACEHOLDER.selectorLabels" . | nindent 4 }}
SERVICE

sed -i "s/SERVICE_NAME_PLACEHOLDER/${SERVICE_NAME}/g" "${CHART_DIR}/templates/service.yaml"

# ---------------------------------------------------------------------------
# templates/hpa.yaml
# ---------------------------------------------------------------------------
cat > "${CHART_DIR}/templates/hpa.yaml" <<'HPA'
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}
  labels:
    {{- include "SERVICE_NAME_PLACEHOLDER.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    {{- if .Values.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if .Values.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 2
          periodSeconds: 60
      selectPolicy: Max
{{- end }}
HPA

sed -i "s/SERVICE_NAME_PLACEHOLDER/${SERVICE_NAME}/g" "${CHART_DIR}/templates/hpa.yaml"

# ---------------------------------------------------------------------------
# templates/configmap.yaml
# ---------------------------------------------------------------------------
cat > "${CHART_DIR}/templates/configmap.yaml" <<'CONFIGMAP'
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}-config
  labels:
    {{- include "SERVICE_NAME_PLACEHOLDER.labels" . | nindent 4 }}
data:
  SERVICE_NAME: "SERVICE_NAME_PLACEHOLDER"
  SERVICE_VERSION: {{ .Chart.AppVersion | quote }}
  LOG_LEVEL: {{ .Values.env.LOG_LEVEL | default "INFO" | quote }}
  LOG_FORMAT: "json"

  # Infrastructure
  {{- if .Values.nats.url }}
  NATS_URL: {{ .Values.nats.url | quote }}
  {{- else }}
  NATS_URL: "nats://nats:4222"
  {{- end }}

  {{- if .Values.redis.url }}
  REDIS_URL: {{ .Values.redis.url | quote }}
  {{- else }}
  REDIS_URL: "redis://redis:6379"
  {{- end }}

  # Feature Flags
  ENABLE_METRICS: "true"
  ENABLE_TRACING: "false"
  METRICS_PORT: "SERVICE_PORT_PLACEHOLDER"
CONFIGMAP

sed -i "s/SERVICE_NAME_PLACEHOLDER/${SERVICE_NAME}/g" "${CHART_DIR}/templates/configmap.yaml"
sed -i "s/SERVICE_PORT_PLACEHOLDER/${SERVICE_PORT}/g" "${CHART_DIR}/templates/configmap.yaml"

# ---------------------------------------------------------------------------
# templates/pdb.yaml
# ---------------------------------------------------------------------------
cat > "${CHART_DIR}/templates/pdb.yaml" <<'PDB'
{{- if .Values.pdb.enabled }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "SERVICE_NAME_PLACEHOLDER.fullname" . }}
  labels:
    {{- include "SERVICE_NAME_PLACEHOLDER.labels" . | nindent 4 }}
spec:
  minAvailable: {{ .Values.pdb.minAvailable }}
  selector:
    matchLabels:
      {{- include "SERVICE_NAME_PLACEHOLDER.selectorLabels" . | nindent 6 }}
{{- end }}
PDB

sed -i "s/SERVICE_NAME_PLACEHOLDER/${SERVICE_NAME}/g" "${CHART_DIR}/templates/pdb.yaml"

# ---------------------------------------------------------------------------
# templates/serviceaccount.yaml
# ---------------------------------------------------------------------------
cat > "${CHART_DIR}/templates/serviceaccount.yaml" <<'SA'
{{- if .Values.serviceAccount.create -}}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "SERVICE_NAME_PLACEHOLDER.serviceAccountName" . }}
  labels:
    {{- include "SERVICE_NAME_PLACEHOLDER.labels" . | nindent 4 }}
  {{- with .Values.serviceAccount.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
automountServiceAccountToken: true
{{- end }}
SA

sed -i "s/SERVICE_NAME_PLACEHOLDER/${SERVICE_NAME}/g" "${CHART_DIR}/templates/serviceaccount.yaml"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "Helm chart generated successfully at: ${CHART_DIR}"
echo ""
echo "Files created:"
find "${CHART_DIR}" -type f | sort | while read -r f; do
  echo "  ${f#${REPO_ROOT}/}"
done
echo ""
echo "Quick start:"
echo "  helm lint ${CHART_DIR}"
echo "  helm template ${SERVICE_NAME} ${CHART_DIR}"
echo "  helm install ${SERVICE_NAME} ${CHART_DIR}"
