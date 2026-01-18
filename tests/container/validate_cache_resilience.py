#!/usr/bin/env python3
"""
Validate GitHub Actions Cache Resilience Configuration

This script validates that all Docker build workflows in the repository
have the cache fallback mechanism properly configured.

It ensures that builds won't fail when GitHub Actions cache is unavailable.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def load_workflow(workflow_path: Path) -> Dict:
    """Load and parse a GitHub Actions workflow file."""
    with open(workflow_path, 'r') as f:
        return yaml.safe_load(f)

def check_cache_config(workflow_data: Dict, workflow_name: str) -> List[Tuple[str, bool, str]]:
    """
    Check if workflow has resilient cache configuration.
    
    Returns:
        List of tuples: (job_name, is_resilient, message)
    """
    results = []
    jobs = workflow_data.get('jobs', {})
    
    for job_name, job_data in jobs.items():
        steps = job_data.get('steps', [])
        
        for step in steps:
            # Check if this step uses docker/build-push-action
            uses = step.get('uses', '')
            if 'docker/build-push-action' not in uses:
                continue
            
            with_config = step.get('with', {})
            cache_from = with_config.get('cache-from', '')
            cache_to = with_config.get('cache-to', '')
            
            # Convert to string if it's a list or multiline
            if isinstance(cache_from, list):
                cache_from = '\n'.join(cache_from)
            if isinstance(cache_to, list):
                cache_to = '\n'.join(cache_to)
            
            # Check for resilient configuration
            has_gha_cache = 'type=gha' in str(cache_from)
            has_inline_fallback = 'type=inline' in str(cache_from)
            uses_inline_cache_to = 'type=inline' in str(cache_to)
            
            if has_gha_cache and has_inline_fallback and uses_inline_cache_to:
                results.append((
                    f"{workflow_name}::{job_name}",
                    True,
                    "✅ Has resilient cache configuration (GHA + inline fallback)"
                ))
            elif has_gha_cache and not has_inline_fallback:
                results.append((
                    f"{workflow_name}::{job_name}",
                    False,
                    "❌ Uses GHA cache without fallback - vulnerable to cache outages"
                ))
            elif 'type=inline' in str(cache_from):
                results.append((
                    f"{workflow_name}::{job_name}",
                    True,
                    "✅ Uses inline cache"
                ))
            else:
                results.append((
                    f"{workflow_name}::{job_name}",
                    True,
                    "ℹ️  No cache configured (acceptable for some workflows)"
                ))
    
    return results

def main():
    """Main validation function."""
    repo_root = Path(__file__).parent.parent.parent
    workflows_dir = repo_root / '.github' / 'workflows'
    
    print("🔍 Validating GitHub Actions Cache Resilience Configuration\n")
    print("=" * 80)
    print()
    
    # Workflows that should have resilient cache configuration
    critical_workflows = [
        'container-tests.yml',
        'ci.yml',
        'release.yml',
        'docker-buildx.yml'
    ]
    
    all_passed = True
    total_checks = 0
    passed_checks = 0
    
    for workflow_file in critical_workflows:
        workflow_path = workflows_dir / workflow_file
        
        if not workflow_path.exists():
            print(f"⚠️  Workflow not found: {workflow_file}")
            continue
        
        print(f"📄 Checking: {workflow_file}")
        print("-" * 80)
        
        try:
            workflow_data = load_workflow(workflow_path)
            results = check_cache_config(workflow_data, workflow_file)
            
            if not results:
                print("  ℹ️  No Docker build steps found (skipped)")
                print()
                continue
            
            for job_name, is_resilient, message in results:
                total_checks += 1
                if is_resilient:
                    passed_checks += 1
                    print(f"  {message}")
                else:
                    all_passed = False
                    print(f"  {message}")
            
            print()
            
        except Exception as e:
            print(f"  ❌ Error parsing workflow: {e}")
            print()
            all_passed = False
    
    # Summary
    print("=" * 80)
    print("\n📊 Summary:")
    print(f"  Total checks: {total_checks}")
    print(f"  Passed: {passed_checks}")
    print(f"  Failed: {total_checks - passed_checks}")
    print()
    
    if all_passed and total_checks > 0:
        print("✅ All workflows have resilient cache configuration!")
        print()
        print("Benefits:")
        print("  • Builds continue when GitHub Actions cache is unavailable")
        print("  • Inline cache provides automatic fallback")
        print("  • No manual intervention needed during cache outages")
        return 0
    elif total_checks == 0:
        print("⚠️  No Docker build steps found to validate")
        return 0
    else:
        print("❌ Some workflows need cache resilience improvements")
        print()
        print("Recommended fix:")
        print("  Replace:")
        print("    cache-from: type=gha,scope=...")
        print("    cache-to: type=gha,scope=...,mode=max")
        print()
        print("  With:")
        print("    cache-from: |")
        print("      type=gha,scope=...")
        print("      type=inline")
        print("    cache-to: type=inline,mode=max")
        return 1

if __name__ == '__main__':
    sys.exit(main())
