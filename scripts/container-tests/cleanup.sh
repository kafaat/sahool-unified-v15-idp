#!/bin/bash

################################################################################
# Docker Cleanup Script
# Description: Clean up test containers, images, and volumes
# Usage: ./cleanup.sh [--all] [--force] [--prune]
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
COMPOSE_FILE="${PROJECT_ROOT}/docker-compose.yml"
FORCE_CLEANUP=false
CLEANUP_ALL=false
PRUNE_SYSTEM=false
REMOVE_VOLUMES=false
REMOVE_IMAGES=false
DRY_RUN=false

# Tracking
declare -a REMOVED_CONTAINERS=()
declare -a REMOVED_IMAGES=()
declare -a REMOVED_VOLUMES=()
declare -a CLEANED_NETWORKS=()

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

confirm() {
    local prompt="$1"
    local response

    if [[ "${FORCE_CLEANUP}" == "true" ]]; then
        return 0
    fi

    echo -e -n "${YELLOW}${prompt} [y/N]:${NC} "
    read -r response

    case "${response}" in
        [yY][eE][sS]|[yY])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

################################################################################
# Check Docker
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

    log_success "Docker is available"
}

################################################################################
# Stop and remove containers from docker-compose
################################################################################

cleanup_compose() {
    if [[ ! -f "${COMPOSE_FILE}" ]]; then
        log_warning "Docker Compose file not found: ${COMPOSE_FILE}"
        return 0
    fi

    log_info "Stopping and removing Docker Compose services..."

    local compose_cmd_args=(
        "-f" "${COMPOSE_FILE}"
        "down"
    )

    if [[ "${REMOVE_VOLUMES}" == "true" ]]; then
        compose_cmd_args+=("--volumes")
    fi

    if [[ "${REMOVE_IMAGES}" == "true" ]]; then
        compose_cmd_args+=("--rmi" "all")
    fi

    compose_cmd_args+=("--remove-orphans")

    if [[ "${DRY_RUN}" == "true" ]]; then
        log_info "[DRY RUN] Would run: docker-compose ${compose_cmd_args[*]}"
    else
        if docker-compose "${compose_cmd_args[@]}" 2>&1; then
            log_success "Docker Compose services cleaned up"
        else
            log_warning "Docker Compose cleanup had some issues (may be normal if nothing was running)"
        fi
    fi
}

################################################################################
# Stop and remove all running containers
################################################################################

cleanup_containers() {
    log_info "Checking for running containers..."

    local containers
    mapfile -t containers < <(docker ps -q)

    if [[ ${#containers[@]} -eq 0 ]]; then
        log_info "No running containers found"
        return 0
    fi

    if confirm "Stop and remove ${#containers[@]} running container(s)?"; then
        for container_id in "${containers[@]}"; do
            local container_name
            container_name=$(docker inspect --format='{{.Name}}' "${container_id}" | sed 's/^\///')

            if [[ "${DRY_RUN}" == "true" ]]; then
                log_info "[DRY RUN] Would stop and remove: ${container_name}"
            else
                log_info "Stopping and removing container: ${container_name}"
                if docker stop "${container_id}" > /dev/null 2>&1 && docker rm "${container_id}" > /dev/null 2>&1; then
                    REMOVED_CONTAINERS+=("${container_name}")
                    log_success "✓ Removed ${container_name}"
                else
                    log_error "✗ Failed to remove ${container_name}"
                fi
            fi
        done
    fi
}

################################################################################
# Remove exited containers
################################################################################

cleanup_exited_containers() {
    log_info "Checking for exited containers..."

    local exited_containers
    mapfile -t exited_containers < <(docker ps -a -q -f status=exited)

    if [[ ${#exited_containers[@]} -eq 0 ]]; then
        log_info "No exited containers found"
        return 0
    fi

    if confirm "Remove ${#exited_containers[@]} exited container(s)?"; then
        if [[ "${DRY_RUN}" == "true" ]]; then
            log_info "[DRY RUN] Would remove ${#exited_containers[@]} exited containers"
        else
            docker rm "${exited_containers[@]}" > /dev/null 2>&1 || true
            log_success "Removed ${#exited_containers[@]} exited containers"
        fi
    fi
}

################################################################################
# Remove images
################################################################################

cleanup_images() {
    log_info "Checking for images..."

    # Remove sahool images
    local sahool_images
    mapfile -t sahool_images < <(docker images --format "{{.Repository}}:{{.Tag}}" | grep -E "^sahool/" || true)

    if [[ ${#sahool_images[@]} -gt 0 ]]; then
        if confirm "Remove ${#sahool_images[@]} sahool image(s)?"; then
            for image in "${sahool_images[@]}"; do
                if [[ "${DRY_RUN}" == "true" ]]; then
                    log_info "[DRY RUN] Would remove image: ${image}"
                else
                    log_info "Removing image: ${image}"
                    if docker rmi "${image}" > /dev/null 2>&1; then
                        REMOVED_IMAGES+=("${image}")
                        log_success "✓ Removed ${image}"
                    else
                        log_warning "✗ Failed to remove ${image} (may be in use)"
                    fi
                fi
            done
        fi
    else
        log_info "No sahool images found"
    fi

    # Remove dangling images
    local dangling_images
    mapfile -t dangling_images < <(docker images -f "dangling=true" -q)

    if [[ ${#dangling_images[@]} -gt 0 ]]; then
        if confirm "Remove ${#dangling_images[@]} dangling image(s)?"; then
            if [[ "${DRY_RUN}" == "true" ]]; then
                log_info "[DRY RUN] Would remove ${#dangling_images[@]} dangling images"
            else
                docker rmi "${dangling_images[@]}" > /dev/null 2>&1 || true
                log_success "Removed ${#dangling_images[@]} dangling images"
            fi
        fi
    fi
}

################################################################################
# Remove volumes
################################################################################

cleanup_volumes() {
    log_info "Checking for volumes..."

    local all_volumes
    mapfile -t all_volumes < <(docker volume ls -q)

    if [[ ${#all_volumes[@]} -eq 0 ]]; then
        log_info "No volumes found"
        return 0
    fi

    # Remove unused volumes
    local unused_volumes
    mapfile -t unused_volumes < <(docker volume ls -qf dangling=true)

    if [[ ${#unused_volumes[@]} -gt 0 ]]; then
        if confirm "Remove ${#unused_volumes[@]} unused volume(s)?"; then
            if [[ "${DRY_RUN}" == "true" ]]; then
                log_info "[DRY RUN] Would remove ${#unused_volumes[@]} unused volumes"
            else
                for volume in "${unused_volumes[@]}"; do
                    log_info "Removing volume: ${volume}"
                    if docker volume rm "${volume}" > /dev/null 2>&1; then
                        REMOVED_VOLUMES+=("${volume}")
                        log_success "✓ Removed ${volume}"
                    else
                        log_warning "✗ Failed to remove ${volume}"
                    fi
                done
            fi
        fi
    else
        log_info "No unused volumes found"
    fi
}

################################################################################
# Remove networks
################################################################################

cleanup_networks() {
    log_info "Checking for custom networks..."

    # Remove unused networks
    local unused_networks
    mapfile -t unused_networks < <(docker network ls --filter type=custom -q)

    if [[ ${#unused_networks[@]} -eq 0 ]]; then
        log_info "No custom networks found"
        return 0
    fi

    if confirm "Remove ${#unused_networks[@]} custom network(s)?"; then
        if [[ "${DRY_RUN}" == "true" ]]; then
            log_info "[DRY RUN] Would prune unused networks"
        else
            docker network prune -f > /dev/null 2>&1 || true
            log_success "Pruned unused networks"
        fi
    fi
}

################################################################################
# Prune Docker system
################################################################################

prune_system() {
    log_info "Running Docker system prune..."

    if [[ "${DRY_RUN}" == "true" ]]; then
        log_info "[DRY RUN] Would run: docker system prune -af --volumes"
        return 0
    fi

    local prune_args=("-a" "-f")

    if [[ "${REMOVE_VOLUMES}" == "true" ]]; then
        prune_args+=("--volumes")
    fi

    if docker system prune "${prune_args[@]}"; then
        log_success "Docker system pruned"
    else
        log_error "Failed to prune Docker system"
    fi
}

################################################################################
# Clean build cache
################################################################################

cleanup_build_cache() {
    log_info "Checking build cache..."

    local cache_size
    cache_size=$(docker builder du 2>/dev/null | tail -n1 | awk '{print $2$3}' || echo "0B")

    if [[ "${cache_size}" != "0B" ]]; then
        if confirm "Clear build cache (${cache_size})?"; then
            if [[ "${DRY_RUN}" == "true" ]]; then
                log_info "[DRY RUN] Would clear build cache"
            else
                docker builder prune -af > /dev/null 2>&1 || true
                log_success "Build cache cleared"
            fi
        fi
    else
        log_info "No build cache to clear"
    fi
}

################################################################################
# Show disk usage
################################################################################

show_disk_usage() {
    print_header "Docker Disk Usage"

    docker system df

    echo ""
    log_info "For detailed breakdown, run: docker system df -v"
}

################################################################################
# Show cleanup summary
################################################################################

show_summary() {
    print_header "Cleanup Summary"

    echo "Removed Containers:  ${#REMOVED_CONTAINERS[@]}"
    echo "Removed Images:      ${#REMOVED_IMAGES[@]}"
    echo "Removed Volumes:     ${#REMOVED_VOLUMES[@]}"
    echo ""

    if [[ ${#REMOVED_CONTAINERS[@]} -gt 0 ]]; then
        echo "Containers removed:"
        for container in "${REMOVED_CONTAINERS[@]}"; do
            echo "  - ${container}"
        done
        echo ""
    fi

    if [[ ${#REMOVED_IMAGES[@]} -gt 0 ]]; then
        echo "Images removed:"
        for image in "${REMOVED_IMAGES[@]}"; do
            echo "  - ${image}"
        done
        echo ""
    fi

    show_disk_usage
}

################################################################################
# Clean security reports
################################################################################

cleanup_reports() {
    local report_dir="${PROJECT_ROOT}/security-reports"

    if [[ ! -d "${report_dir}" ]]; then
        log_info "No security reports directory found"
        return 0
    fi

    local report_count
    report_count=$(find "${report_dir}" -type f | wc -l)

    if [[ ${report_count} -eq 0 ]]; then
        log_info "No security reports to clean"
        return 0
    fi

    if confirm "Remove ${report_count} security report(s)?"; then
        if [[ "${DRY_RUN}" == "true" ]]; then
            log_info "[DRY RUN] Would remove ${report_count} security reports"
        else
            rm -rf "${report_dir}"
            log_success "Removed security reports directory"
        fi
    fi
}

################################################################################
# Usage
################################################################################

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Clean up Docker containers, images, volumes, and networks.

OPTIONS:
    -h, --help              Show this help message
    -a, --all               Clean up everything (containers, images, volumes, networks)
    -f, --force             Force cleanup without confirmation
    -p, --prune             Run Docker system prune
    -i, --images            Remove images
    -v, --volumes           Remove volumes
    -n, --networks          Remove networks
    -r, --reports           Clean security reports
    --dry-run               Show what would be done without doing it
    --show-usage            Show disk usage only

EXAMPLES:
    $(basename "$0")                    # Interactive cleanup of containers
    $(basename "$0") -f                 # Force cleanup without prompts
    $(basename "$0") -a -f              # Force cleanup of everything
    $(basename "$0") -i                 # Remove images only
    $(basename "$0") -p                 # Prune system
    $(basename "$0") --dry-run -a       # Dry run of full cleanup

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
            -a|--all)
                CLEANUP_ALL=true
                REMOVE_VOLUMES=true
                REMOVE_IMAGES=true
                shift
                ;;
            -f|--force)
                FORCE_CLEANUP=true
                shift
                ;;
            -p|--prune)
                PRUNE_SYSTEM=true
                shift
                ;;
            -i|--images)
                REMOVE_IMAGES=true
                shift
                ;;
            -v|--volumes)
                REMOVE_VOLUMES=true
                shift
                ;;
            -n|--networks)
                # Networks are cleaned by default
                shift
                ;;
            -r|--reports)
                cleanup_reports
                exit 0
                ;;
            --dry-run)
                DRY_RUN=true
                log_warning "DRY RUN MODE - No actual changes will be made"
                shift
                ;;
            --show-usage)
                show_disk_usage
                exit 0
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
    print_header "Docker Cleanup Tool"

    # Parse arguments
    parse_args "$@"

    # Check Docker
    check_docker

    # Show current disk usage
    log_info "Current Docker disk usage:"
    docker system df
    echo ""

    # Change to project root
    cd "${PROJECT_ROOT}"

    # Cleanup docker-compose services first
    cleanup_compose

    # Clean up based on options
    if [[ "${CLEANUP_ALL}" == "true" ]]; then
        log_info "Performing full cleanup..."
        cleanup_containers
        cleanup_exited_containers
        cleanup_images
        cleanup_volumes
        cleanup_networks
        cleanup_build_cache
        cleanup_reports
    else
        # Stop running containers
        cleanup_containers

        # Remove exited containers
        cleanup_exited_containers

        # Remove images if requested
        if [[ "${REMOVE_IMAGES}" == "true" ]]; then
            cleanup_images
        fi

        # Remove volumes if requested
        if [[ "${REMOVE_VOLUMES}" == "true" ]]; then
            cleanup_volumes
        fi

        # Clean networks
        cleanup_networks
    fi

    # Run system prune if requested
    if [[ "${PRUNE_SYSTEM}" == "true" ]]; then
        prune_system
    fi

    # Show summary
    if [[ "${DRY_RUN}" != "true" ]]; then
        show_summary
        log_success "Cleanup completed!"
    else
        log_info "Dry run completed - no changes were made"
    fi
}

# Run main function
main "$@"
