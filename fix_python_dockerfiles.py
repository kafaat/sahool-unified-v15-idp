#!/usr/bin/env python3
"""
SAHOOL Python Dockerfile Resilience Fixer
==========================================
Automatically updates Python service Dockerfiles with resilient multi-mirror
fallback strategy for pip installations.

This addresses common build failures in restricted network environments where
primary mirrors (like Aliyun) may time out or fail.

Usage:
    python fix_python_dockerfiles.py
"""

import re
from pathlib import Path


def find_python_dockerfiles(root_dir: str = ".") -> list[Path]:
    """Find all Dockerfiles in Python services."""
    dockerfiles = []
    services_dir = Path(root_dir) / "apps" / "services"

    if not services_dir.exists():
        print(f"❌ Services directory not found: {services_dir}")
        return dockerfiles

    for service_dir in services_dir.iterdir():
        if service_dir.is_dir():
            dockerfile = service_dir / "Dockerfile"
            if dockerfile.exists():
                # Check if it's a Python service (has requirements.txt)
                requirements = service_dir / "requirements.txt"
                if requirements.exists():
                    dockerfiles.append(dockerfile)

    return dockerfiles


def needs_update(content: str) -> bool:
    """Check if Dockerfile needs the resilient fallback pattern."""
    # Check if already has the robust fallback pattern with timeouts
    if "timeout=600" in content and "pypi.org/simple" in content:
        return False

    # Check if has pip install (with or without simple fallback)
    if re.search(r"pip install.*-r requirements\.txt", content):
        return True

    return False


def apply_resilient_pattern(content: str) -> tuple[str, bool]:
    """Apply the resilient multi-mirror fallback pattern."""
    modified = False

    # Pattern 1: Simple fallback to Aliyun only (most common issue)
    # Matches: RUN pip install --no-cache-dir -r requirements.txt || \
    #              pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt
    simple_aliyun_pattern = r"RUN pip install --no-cache-dir -r requirements\.txt \|\| \\\s*pip install -i https://mirrors\.aliyun\.com/pypi/simple/ --trusted-host mirrors\.aliyun\.com -r requirements\.txt"
    simple_aliyun_replacement = """# Install dependencies with resilient multi-mirror fallback strategy
# Try official PyPI first with long timeout, then fallback to Aliyun, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \\
    --index-url https://pypi.org/simple \\
    --trusted-host pypi.org \\
    --trusted-host files.pythonhosted.org \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.aliyun.com/pypi/simple/ \\
    --trusted-host mirrors.aliyun.com \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.cloud.tencent.com/pypi/simple \\
    --trusted-host mirrors.cloud.tencent.com \\
    -r requirements.txt"""

    if re.search(simple_aliyun_pattern, content):
        content = re.sub(simple_aliyun_pattern, simple_aliyun_replacement, content, flags=re.DOTALL)
        modified = True
        return content, modified

    # Pattern 1b: Aliyun-only install with --default-timeout
    # Matches: RUN pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt || \
    #              pip install --no-cache-dir --default-timeout=100 --retries=5 -i https://mirrors.aliyun.com/pypi/simple/ ...
    aliyun_default_timeout_pattern = r"RUN pip install --no-cache-dir --default-timeout=\d+ --retries=\d+ -r requirements\.txt \|\|.*?-r requirements\.txt"
    aliyun_default_timeout_replacement = """# Install dependencies with resilient multi-mirror fallback strategy
# Try official PyPI first with long timeout, then fallback to Aliyun, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \\
    --index-url https://pypi.org/simple \\
    --trusted-host pypi.org \\
    --trusted-host files.pythonhosted.org \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.aliyun.com/pypi/simple/ \\
    --trusted-host mirrors.aliyun.com \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.cloud.tencent.com/pypi/simple \\
    --trusted-host mirrors.cloud.tencent.com \\
    -r requirements.txt"""

    if re.search(aliyun_default_timeout_pattern, content, flags=re.DOTALL):
        content = re.sub(aliyun_default_timeout_pattern, aliyun_default_timeout_replacement, content, flags=re.DOTALL)
        modified = True
        return content, modified

    # Pattern 1c: Aliyun-only install with timeout but no PyPI fallback
    # Matches: RUN pip install --no-cache-dir --timeout=300 --retries=10 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
    aliyun_only_pattern = r"RUN pip install --no-cache-dir --timeout=\d+ --retries=\d+ -i https://mirrors\.aliyun\.com/pypi/simple/ -r requirements\.txt"
    aliyun_only_replacement = """# Install dependencies with resilient multi-mirror fallback strategy
# Try official PyPI first with long timeout, then fallback to Aliyun, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \\
    --index-url https://pypi.org/simple \\
    --trusted-host pypi.org \\
    --trusted-host files.pythonhosted.org \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.aliyun.com/pypi/simple/ \\
    --trusted-host mirrors.aliyun.com \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.cloud.tencent.com/pypi/simple \\
    --trusted-host mirrors.cloud.tencent.com \\
    -r requirements.txt"""

    if re.search(aliyun_only_pattern, content):
        content = re.sub(aliyun_only_pattern, aliyun_only_replacement, content)
        modified = True
        return content, modified

    # Pattern 2: Upgrade pip command
    pip_upgrade_pattern = r"RUN pip install --no-cache-dir --upgrade pip \|\| true"
    pip_upgrade_replacement = """# Upgrade pip with resilient fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.aliyun.com/pypi/simple/ \\
    --upgrade pip || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    --index-url https://pypi.org/simple \\
    --trusted-host pypi.org \\
    --trusted-host files.pythonhosted.org \\
    --upgrade pip || true"""

    if re.search(pip_upgrade_pattern, content):
        content = re.sub(pip_upgrade_pattern, pip_upgrade_replacement, content)
        modified = True

    # Pattern 3: Requirements installation (standalone)
    req_install_pattern = r"RUN pip install --no-cache-dir --timeout=\d+ --retries=\d+ -r requirements\.txt"
    req_install_replacement = """# Install dependencies with resilient multi-mirror fallback strategy
# Try Aliyun mirror first (fast in China), fallback to official PyPI, finally Tencent
RUN pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.aliyun.com/pypi/simple/ \\
    --trusted-host mirrors.aliyun.com \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    --index-url https://pypi.org/simple \\
    --trusted-host pypi.org \\
    --trusted-host files.pythonhosted.org \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.cloud.tencent.com/pypi/simple \\
    --trusted-host mirrors.cloud.tencent.com \\
    -r requirements.txt"""

    if re.search(req_install_pattern, content):
        content = re.sub(req_install_pattern, req_install_replacement, content)
        modified = True

    # Pattern 4: Chained RUN commands (upgrade + install + chown)
    chained_pattern = r"RUN pip install --no-cache-dir --upgrade pip \|\| true &&\s*\\\s*pip install --no-cache-dir --timeout=\d+ --retries=\d+ -r requirements\.txt &&\s*\\\s*chown -R sahool:sahool /app"
    chained_replacement = """# Upgrade pip with resilient fallback
RUN pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.aliyun.com/pypi/simple/ \\
    --upgrade pip || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    --index-url https://pypi.org/simple \\
    --trusted-host pypi.org \\
    --trusted-host files.pythonhosted.org \\
    --upgrade pip || true

# Install dependencies with resilient multi-mirror fallback strategy
RUN pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.aliyun.com/pypi/simple/ \\
    --trusted-host mirrors.aliyun.com \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    --index-url https://pypi.org/simple \\
    --trusted-host pypi.org \\
    --trusted-host files.pythonhosted.org \\
    -r requirements.txt || \\
    pip install --no-cache-dir --timeout=600 --retries=5 \\
    -i https://mirrors.cloud.tencent.com/pypi/simple/ \\
    --trusted-host mirrors.cloud.tencent.com \\
    -r requirements.txt

# Set ownership
RUN chown -R sahool:sahool /app"""

    if re.search(chained_pattern, content):
        content = re.sub(chained_pattern, chained_replacement, content)
        modified = True

    return content, modified


def main():
    """Main execution function."""
    print("🔍 Scanning for Python Dockerfiles...")

    dockerfiles = find_python_dockerfiles()

    if not dockerfiles:
        print("❌ No Python Dockerfiles found.")
        return

    print(f"✅ Found {len(dockerfiles)} Python Dockerfiles\n")

    updated_count = 0
    skipped_count = 0

    for dockerfile in dockerfiles:
        service_name = dockerfile.parent.name
        print(f"📄 Processing: {service_name}")

        with open(dockerfile, encoding="utf-8") as f:
            original_content = f.read()

        if not needs_update(original_content):
            print("   ⏭️  Already has resilient pattern, skipping.\n")
            skipped_count += 1
            continue

        updated_content, modified = apply_resilient_pattern(original_content)

        if modified:
            with open(dockerfile, "w", encoding="utf-8") as f:
                f.write(updated_content)
            print("   ✅ Updated with resilient fallback pattern\n")
            updated_count += 1
        else:
            print("   ⚠️  No matching patterns found, skipping.\n")
            skipped_count += 1

    print("=" * 60)
    print("📊 Summary:")
    print(f"   Updated: {updated_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Total:   {len(dockerfiles)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
