---
name: code-review-generic
description: Reviews code for bugs, inefficiencies, and adherence to best practices, providing actionable improvement suggestions. TRIGGER when the user asks for a quick, language-agnostic "code review", "review this snippet", "find bugs", "suggest improvements" on code outside the SAHOOL platform scope. DO NOT TRIGGER for reviews of SAHOOL microservices or shared modules - defer to the SAHOOL-specific code-review.md in `.claude/skills/development/`.
license: Complete terms in LICENSE.txt
---

# Code Review Skill (Generic)

## Overview

Analyzes code to ensure quality, efficiency, and maintainability. Language-agnostic, for snippets and side-projects outside the SAHOOL monorepo.

**Keywords**: code, review, bugs, optimization, best practices

## Features

- Error detection
- Optimization recommendations
- Style enforcement

## Output Format

- Issues found
- Suggested fixes
- Optional summary

## Instructions

- Analyze code line by line
- Highlight errors or inefficiencies
- Suggest improvements

## Constraints

- Maintain accuracy
- Avoid false positives
