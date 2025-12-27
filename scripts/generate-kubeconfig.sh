#!/bin/bash
# SAHOOL Kubeconfig Generator for CI/CD
# Generates base64 encoded kubeconfig for GitHub Actions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -c, --cluster CLUSTER      Cluster name (required)"
    echo "  -x, --context CONTEXT      Kubernetes context (optional, defaults to current)"
    echo "  -n, --namespace NAMESPACE  Default namespace (optional)"
    echo "  -h, --help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --cluster my-cluster"
    echo "  $0 --cluster my-cluster --context production --namespace sahool-production"
    exit 1
}

# Parse arguments
CLUSTER=""
CONTEXT=""
NAMESPACE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--cluster)
            CLUSTER="$2"
            shift 2
            ;;
        -x|--context)
            CONTEXT="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Validate required parameters
if [ -z "$CLUSTER" ]; then
    echo -e "${RED}Error: Cluster name is required${NC}"
    usage
fi

# Use current context if not specified
if [ -z "$CONTEXT" ]; then
    CONTEXT=$(kubectl config current-context)
    echo -e "${YELLOW}Using current context: $CONTEXT${NC}"
fi

echo -e "${GREEN}Generating kubeconfig for CI/CD${NC}"
echo "Cluster: $CLUSTER"
echo "Context: $CONTEXT"
[ -n "$NAMESPACE" ] && echo "Namespace: $NAMESPACE"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
KUBECONFIG_FILE="$TEMP_DIR/kubeconfig"

# Extract current kubeconfig
echo -e "${YELLOW}Extracting kubeconfig...${NC}"

# Get cluster info
CLUSTER_INFO=$(kubectl config view --minify --flatten --context="$CONTEXT")

# Create kubeconfig file
echo "$CLUSTER_INFO" > "$KUBECONFIG_FILE"

# Set default namespace if provided
if [ -n "$NAMESPACE" ]; then
    kubectl config set-context "$CONTEXT" --namespace="$NAMESPACE" --kubeconfig="$KUBECONFIG_FILE" > /dev/null
fi

# Encode to base64
echo -e "${YELLOW}Encoding kubeconfig...${NC}"
ENCODED_CONFIG=$(cat "$KUBECONFIG_FILE" | base64 -w 0)

# Display results
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Kubeconfig Generated Successfully!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${BLUE}Add this to your GitHub repository secrets:${NC}"
echo ""
echo -e "${YELLOW}Secret Name:${NC}"
echo "KUBE_CONFIG_$(echo $CLUSTER | tr '[:lower:]' '[:upper:]' | tr '-' '_')"
echo ""
echo -e "${YELLOW}Secret Value:${NC}"
echo "$ENCODED_CONFIG"
echo ""
echo -e "${BLUE}Steps to add to GitHub:${NC}"
echo "1. Go to your repository on GitHub"
echo "2. Navigate to Settings > Secrets and variables > Actions"
echo "3. Click 'New repository secret'"
echo "4. Name: KUBE_CONFIG_$(echo $CLUSTER | tr '[:lower:]' '[:upper:]' | tr '-' '_')"
echo "5. Value: Paste the encoded value above"
echo "6. Click 'Add secret'"
echo ""

# Save to file option
echo -e "${YELLOW}Save to file? (y/n)${NC}"
read -r SAVE_FILE

if [[ "$SAVE_FILE" =~ ^[Yy]$ ]]; then
    OUTPUT_FILE="kubeconfig-$CLUSTER-$(date +%Y%m%d-%H%M%S).txt"
    echo "$ENCODED_CONFIG" > "$OUTPUT_FILE"
    echo -e "${GREEN}Saved to: $OUTPUT_FILE${NC}"
    echo -e "${RED}WARNING: Keep this file secure and delete after use!${NC}"
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo -e "${GREEN}Done!${NC}"
