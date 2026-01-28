#!/usr/bin/env python3
"""
Add 'from __future__ import annotations' to Python files that need it.
This script scans for files using PEP 604 union syntax (X | Y) without the required import.
"""

import os
import re
from pathlib import Path

def has_union_syntax(content: str) -> bool:
    """Check if file uses PEP 604 union syntax in type annotations."""
    # Pattern to match type annotations with | operator
    # Matches patterns like: var: Type | None, def func() -> Type | None, etc.
    pattern = r':\s*\w+\s*\|\s*\w+|->\ *\w+\s*\|\s*\w+'
    return bool(re.search(pattern, content))

def has_future_annotations(content: str) -> bool:
    """Check if file already has 'from __future__ import annotations'."""
    return 'from __future__ import annotations' in content

def add_future_annotations(filepath: Path) -> bool:
    """Add 'from __future__ import annotations' to a Python file if needed."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has the import or doesn't use union syntax
        if has_future_annotations(content) or not has_union_syntax(content):
            return False
        
        # Find the position to insert the import
        lines = content.split('\n')
        insert_pos = 0
        
        # Skip docstrings and comments at the top
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Handle docstrings
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if in_docstring:
                    in_docstring = False
                    insert_pos = i + 1
                else:
                    in_docstring = True
            elif not in_docstring and not stripped.startswith('#') and stripped:
                # Found first non-comment, non-docstring line
                insert_pos = i
                break
        
        # Insert the import
        lines.insert(insert_pos, 'from __future__ import annotations')
        lines.insert(insert_pos + 1, '')  # Add blank line
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    shared_dir = Path(r'd:\PROJECTS\v69\sahool-unified-v15-idp\shared')
    fixed_count = 0
    
    for py_file in shared_dir.rglob('*.py'):
        if add_future_annotations(py_file):
            print(f"Fixed: {py_file.relative_to(shared_dir)}")
            fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
