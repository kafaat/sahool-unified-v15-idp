#!/bin/bash

################################################################################
# Docker Build Script
# Description: Build all Docker images with proper tagging
# Usage: ./build-all.sh [--tag TAG] [--push] [--parallel]
################################################################################

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Configuration
TAG="${TAG:-latest}"
REGISTRY="${REGISTRY:-}"
PUSH_IMAGES=false
PARALLEL_BUILD=false
NO_CACHE=false
BUILD_ARGS=()
MAX_PARALLEL_JOBS=4

# Build tracking
declare -a BUILD_JOBS=()
declare -a BUILT_IMAGES=()
declare -a FAILED_BUILDS=()

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $*${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

################################################################################
# Find all Dockerfiles and determine image names
################################################################################

find_dockerfiles() {
    local dockerfiles=()

    # Find all Dockerfiles (excluding test and archive)
    while IFS= read -r -d '' file; do
        # Skip test Dockerfiles and archived ones
        if [[ "$file" =~ \.test$ ]] || [[ "$file" =~ /archive/ ]]; then
            continue
        fi
        dockerfiles+=("$file")
    done < <(find "${PROJECT_ROOT}" \
        -type f \
        \( -name "Dockerfile" -o -name "Dockerfile.*" \) \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -not -path "*/dist/*" \
        -not -path "*/build/*" \
        -not -path "*/archive/*" \
        -print0)

    printf '%s\n' "${dockerfiles[@]}"
}

################################################################################
# Determine image name from Dockerfile path
################################################################################

get_image_name() {
    local dockerfile="$1"
    local dir_name
    local image_name

    # Get the directory containing the Dockerfile
    dir_name="$(basename "$(dirname "${dockerfile}")")"

    # If it's a service, use the service name
    if [[ "${dockerfile}" =~ /apps/services/([^/]+) ]]; then
        image_name="${BASH_REMATCH[1]}"
    elif [[ "${dockerfile}" =~ /apps/([^/]+) ]]; then
        image_name="${BASH_REMATCH[1]}"
    elif [[ "${dockerfile}" =~ /infrastructure/([^/]+)/([^/]+) ]]; then
        image_name="${BASH_REMATCH[1]}-${BASH_REMATCH[2]}"
    else
        # Use directory name
        image_name="${dir_name}"
    fi

    # Sanitize image name
    image_name=$(echo "${image_name}" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9._-]/-/g')

    # Add registry prefix if specified
    if [[ -n "${REGISTRY}" ]]; then
        echo "${REGISTRY}/${image_name}"
    else
        echo "sahool/${image_name}"
    fi
}

################################################################################
# Build a single Docker image
################################################################################

build_image() {
    local dockerfile="$1"
    local image_name="$2"
    local context_dir
    local relative_path="${dockerfile#${PROJECT_ROOT}/}"

    # Determine build context (directory containing Dockerfile)
    context_dir="$(dirname "${dockerfile}")"

    log_info "Building ${CYAN}${image_name}:${TAG}${NC} from ${relative_path}"

    # Build docker build arguments
    local docker_build_args=(
        "build"
        "-f" "${dockerfile}"
        "-t" "${image_name}:${TAG}"
        "-t" "${image_name}:latest"
    )

    # Add no-cache if requested
    if [[ "${NO_CACHE}" == "true" ]]; then
        docker_build_args+=("--no-cache")
    fi

    # Add build args
    for arg in "${BUILD_ARGS[@]}"; do
        docker_build_args+=("--build-arg" "${arg}")
    done

    # Add labels
    docker_build_args+=(
        "--label" "org.opencontainers.image.created=$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        "--label" "org.opencontainers.image.version=${TAG}"
        "--label" "org.opencontainers.image.source=https://github.com/sahool/sahool-unified"
    )

    # Add context directory
    docker_build_args+=("${context_dir}")

    # Build the image
    if docker "${docker_build_args[@]}"; then
        log_success "✓ Built ${image_name}:${TAG}"
        BUILT_IMAGES+=("${image_name}:${TAG}")
        return 0
    else
        log_error "✗ Failed to build ${image_name}:${TAG}"
        FAILED_BUILDS+=("${image_name}:${TAG}")
        return 1
    fi
}

################################################################################
# Build all images sequentially
################################################################################

build_sequential() {
    local dockerfiles
    mapfile -t dockerfiles < <(find_dockerfiles)

    if [[ ${#dockerfiles[@]} -eq 0 ]]; then
        log_warning "No Dockerfiles found"
        return 0
    fi

    log_info "Found ${#dockerfiles[@]} Dockerfile(s) to build"
    echo ""

    for dockerfile in "${dockerfiles[@]}"; do
        local image_name
        image_name="$(get_image_name "${dockerfile}")"

        build_image "${dockerfile}" "${image_name}" || true
        echo ""
    done
}

################################################################################
# Build all images in parallel
################################################################################

build_parallel() {
    local dockerfiles
    mapfile -t dockerfiles < <(find_dockerfiles)

    if [[ ${#dockerfiles[@]} -eq 0 ]]; then
        log_warning "No Dockerfiles found"
        return 0
    fi

    log_info "Found ${#dockerfiles[@]} Dockerfile(s) to build in parallel (max ${MAX_PARALLEL_JOBS} jobs)"
    echo ""

    local job_count=0

    for dockerfile in "${dockerfiles[@]}"; do
        local image_name
        image_name="$(get_image_name "${dockerfile}")"

        # Build in background
        build_image "${dockerfile}" "${image_name}" &
        BUILD_JOBS+=($!)

        ((job_count++))

        # Wait if we've reached max parallel jobs
        if [[ ${job_count} -ge ${MAX_PARALLEL_JOBS} ]]; then
            wait -n
            ((job_count--))
        fi
    done

    # Wait for all remaining jobs
    log_info "Waiting for all builds to complete..."
    for job in "${BUILD_JOBS[@]}"; do
        wait "${job}" || true
    done
}

################################################################################
# Push images to registry
################################################################################

push_images() {
    if [[ ${#BUILT_IMAGES[@]} -eq 0 ]]; then
        log_warning "No images to push"
        return 0
    fi

    print_header "Pushing Images to Registry"

    for image in "${BUILT_IMAGES[@]}"; do
        log_info "Pushing ${image}..."
        if docker push "${image}"; then
            log_success "✓ Pushed ${image}"
        else
            log_error "✗ Failed to push ${image}"
        fi
    done
}

################################################################################
# Display build summary
################################################################################

show_summary() {
    print_header "Build Summary"

    echo "Tag:              ${TAG}"
    echo "Registry:         ${REGISTRY:-local}"
    echo "Total Images:     $((${#BUILT_IMAGES[@]} + ${#FAILED_BUILDS[@]}))"
    echo -e "Successful:       ${GREEN}${#BUILT_IMAGES[@]}${NC}"
    echo -e "Failed:           ${RED}${#FAILED_BUILDS[@]}${NC}"
    echo ""

    if [[ ${#BUILT_IMAGES[@]} -gt 0 ]]; then
        echo -e "${GREEN}Successfully Built Images:${NC}"
        for image in "${BUILT_IMAGES[@]}"; do
            echo "  ✓ ${image}"
        done
        echo ""
    fi

    if [[ ${#FAILED_BUILDS[@]} -gt 0 ]]; then
        echo -e "${RED}Failed Builds:${NC}"
        for image in "${FAILED_BUILDS[@]}"; do
            echo "  ✗ ${image}"
        done
        echo ""
    fi

    # Show disk usage
    log_info "Docker disk usage:"
    docker system df
}

################################################################################
# Check Docker daemon
################################################################################

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi

    log_success "Docker is available: $(docker --version)"
}

################################################################################
# Usage
################################################################################

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Build all Docker images in the project with proper tagging.

OPTIONS:
    -h, --help              Show this help message
    -t, --tag TAG           Tag for the images (default: latest)
    -r, --registry REG      Registry prefix (e.g., ghcr.io/org)
    -p, --push              Push images to registry after building
    -j, --parallel          Build images in parallel
    -n, --no-cache          Build without using cache
    -b, --build-arg ARG     Pass build argument (can be used multiple times)
    --max-jobs N            Maximum parallel jobs (default: 4)

EXAMPLES:
    $(basename "$0")                                # Build all with 'latest' tag
    $(basename "$0") -t v1.0.0                      # Build with specific tag
    $(basename "$0") -t v1.0.0 --push               # Build and push
    $(basename "$0") --parallel --max-jobs 8        # Build in parallel
    $(basename "$0") -r ghcr.io/myorg -t v1.0.0    # Build with registry prefix

EOF
    exit 0
}

################################################################################
# Parse Arguments
################################################################################

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                ;;
            -t|--tag)
                TAG="$2"
                shift 2
                ;;
            -r|--registry)
                REGISTRY="$2"
                shift 2
                ;;
            -p|--push)
                PUSH_IMAGES=true
                shift
                ;;
            -j|--parallel)
                PARALLEL_BUILD=true
                shift
                ;;
            -n|--no-cache)
                NO_CACHE=true
                shift
                ;;
            -b|--build-arg)
                BUILD_ARGS+=("$2")
                shift 2
                ;;
            --max-jobs)
                MAX_PARALLEL_JOBS="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done
}

################################################################################
# Main
################################################################################

main() {
    print_header "Docker Image Builder"

    # Parse arguments
    parse_args "$@"

    # Check Docker
    check_docker

    # Change to project root
    cd "${PROJECT_ROOT}"

    # Build images
    if [[ "${PARALLEL_BUILD}" == "true" ]]; then
        build_parallel
    else
        build_sequential
    fi

    # Push if requested
    if [[ "${PUSH_IMAGES}" == "true" ]]; then
        push_images
    fi

    # Show summary
    show_summary

    # Exit with error if any builds failed
    if [[ ${#FAILED_BUILDS[@]} -gt 0 ]]; then
        exit 1
    fi

    log_success "All builds completed successfully!"
    exit 0
}

# Run main function
main "$@"
