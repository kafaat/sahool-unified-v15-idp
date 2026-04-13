---
name: skill-creator
description: Generates new AI skills in `.md` format, providing structured name, description, and instructions for future use. TRIGGER when the user asks to "create a new skill", "scaffold a skill file", "add a skill for X", or describes a recurring capability they want packaged as a reusable `.md` skill with YAML frontmatter.
license: Complete terms in LICENSE.txt
---

# Skill Creator (Meta Skill)

## Overview

Automates creation of AI skills by generating fully structured `.md` files.

**Keywords**: skill creation, automation, AI, md, modular

## Features

- Generates skill metadata
- Includes detailed instructions
- Ready-to-use format

## Output Format

- Skill name (slug)
- YAML frontmatter (`name`, `description` with TRIGGER patterns)
- Overview, Features, Output Format, Instructions, Constraints sections

## Instructions

- Accept input goal from the user
- Define role, task, process
- Output structured `.md` skill
- Follow the repository's existing skill conventions (name-kebab-case, TRIGGER-rich description)

## Constraints

- Maintain clarity
- Ensure usability
- Do not overlap with existing skills without justification
