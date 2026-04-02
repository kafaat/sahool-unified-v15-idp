#!/usr/bin/env pwsh
# Deploy SAHOOL to production EKS
param(
    [string]$Environment = "production",
    [string]$Version = "latest"
)
$ErrorActionPreference = "Stop"
Write-Host "Deploying SAHOOL v$Version to $Environment" -ForegroundColor Cyan

aws eks update-kubeconfig --name sahool-$Environment

helm upgrade --install sahool-v16 ./helm/sahool `
    --namespace sahool-$Environment `
    --create-namespace `
    --set global.environment=$Environment `
    --wait --timeout 15m

kubectl get pods -n sahool-$Environment
Write-Host "Deployment complete" -ForegroundColor Green
