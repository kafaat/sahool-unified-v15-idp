# SAHOOL GitHub Security Infrastructure
# Terraform configuration for GitHub organization security

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }

  cloud {
    organization = "kafaat-devops"
    workspaces {
      name = "sahoop-github-security"
    }
  }
}

provider "github" {
  owner = var.github_organization
}

# Variables
variable "github_organization" {
  type        = string
  description = "GitHub organization name"
}

variable "snyk_token" {
  type        = string
  sensitive   = true
  description = "Snyk API token"
}

variable "jwt_secret" {
  type        = string
  sensitive   = true
  description = "JWT signing secret"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "Database password"
}

variable "teams" {
  type = map(object({
    name        = string
    description = string
    privacy     = string
    members     = list(string)
    permission  = optional(string, "push")
  }))
  description = "Team configurations"
  default     = {}
}

# Data source for the repository
data "github_repository" "sahool" {
  full_name = "${var.github_organization}/sahool-unified-v15-idp"
}

# Repository Security Settings
resource "github_repository_security_and_analysis" "sahool" {
  repository = data.github_repository.sahool.name

  security_and_analysis {
    secret_scanning {
      status = "enabled"
    }
    secret_scanning_push_protection {
      status = "enabled"
    }
  }
}

# Branch Protection for main
resource "github_branch_protection" "main" {
  repository_id = data.github_repository.sahool.node_id
  pattern       = "main"

  required_status_checks {
    strict   = true
    contexts = ["ci", "security-scan", "lint"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    require_code_owner_reviews      = true
    required_approving_review_count = 1
    require_last_push_approval      = true
  }

  enforce_admins = false

  allows_deletions    = false
  allows_force_pushes = false

  required_linear_history = false
}

# Branch Protection for develop
resource "github_branch_protection" "develop" {
  repository_id = data.github_repository.sahool.node_id
  pattern       = "develop"

  required_status_checks {
    strict   = true
    contexts = ["ci", "lint"]
  }

  required_pull_request_reviews {
    dismiss_stale_reviews           = true
    required_approving_review_count = 1
  }

  allows_deletions    = false
  allows_force_pushes = false
}

# Teams
resource "github_team" "teams" {
  for_each = var.teams

  name        = each.value.name
  description = each.value.description
  privacy     = each.value.privacy
}

# Team Repository Access
resource "github_team_repository" "team_access" {
  for_each = var.teams

  team_id    = github_team.teams[each.key].id
  repository = data.github_repository.sahool.name
  permission = each.value.permission
}

# GitHub Actions Secrets
resource "github_actions_secret" "snyk_token" {
  repository      = data.github_repository.sahool.name
  secret_name     = "SNYK_TOKEN"
  plaintext_value = var.snyk_token
}

resource "github_actions_secret" "jwt_secret" {
  repository      = data.github_repository.sahool.name
  secret_name     = "JWT_SECRET"
  plaintext_value = var.jwt_secret
}

resource "github_actions_secret" "db_password" {
  repository      = data.github_repository.sahool.name
  secret_name     = "DB_PASSWORD"
  plaintext_value = var.db_password
}

# Dependabot Security Updates
resource "github_repository_dependabot_security_updates" "sahool" {
  repository = data.github_repository.sahool.name
  enabled    = true
}

# Outputs
output "repository_url" {
  value       = data.github_repository.sahool.html_url
  description = "Repository URL"
}

output "teams_created" {
  value       = [for t in github_team.teams : t.name]
  description = "List of created teams"
}

output "branch_protection_enabled" {
  value       = true
  description = "Branch protection status"
}
