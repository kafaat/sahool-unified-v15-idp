#!/usr/bin/env pwsh
# Deploy SAHOOL to production EKS
param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    [string]$Environment = "production"
)
$ErrorActionPreference = "Stop"

if ($Version -eq "latest") {
    Write-Error "Explicit semver version required for production (e.g. 16.0.1). 'latest' is not allowed."
    exit 1
}

Write-Host "Deploying SAHOOL v$Version to $Environment" -ForegroundColor Cyan

aws eks update-kubeconfig --name sahool-$Environment

helm upgrade --install sahool-v16 ./helm/sahool `
    --namespace sahool-$Environment `
    --create-namespace `
    --set global.environment=$Environment `
    --set global.image.tag=$Version `
    --atomic `
    --wait --timeout 15m

kubectl get pods -n sahool-$Environment
Write-Host "Deployment complete" -ForegroundColor Green
