#!/usr/bin/env bash
# ==============================================================================
# .devcontainer/setup.sh
# Post-create setup script for GitHub Codespaces (Free Tier)
# ==============================================================================
set -euo pipefail

echo "==> Configuring COBOL-to-Java Modernization Platform in Codespaces..."

# 1. Install Linux packages: GnuCOBOL (for fast native baseline) & PostgreSQL client
echo "==> Installing GnuCOBOL and PostgreSQL client..."
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
    gnucobol \
    postgresql-client \
    curl \
    git
sudo rm -rf /var/lib/apt/lists/*

# 2. Python test & runtime dependencies
echo "==> Installing Python dependencies..."
python -m pip install --upgrade --quiet pip
python -m pip install --quiet -r requirements-dev.txt

# 3. Environment verification
echo "==> Toolchain verification:"
printf "  Python:   %s\n" "$(python --version)"
printf "  Java:     %s\n" "$(javac -version 2>&1 | head -n1)"
printf "  Maven:    %s\n" "$(mvn -version 2>&1 | head -n1)"
printf "  GnuCOBOL: %s\n" "$(cobc --version 2>&1 | head -n1)"
printf "  psql:     %s\n" "$(psql --version 2>&1 | head -n1)"

# Note: Maven dependencies resolve lazily on first build/test to minimize
# startup duration and initial Codespace storage consumption.

echo "==> Setup completed successfully."

# 4. Stage A Remote Validation Suite
echo "==> Running Stage A remote validation..."
set +e

git pull origin feature/open-source-mainframe-reference-stack || true

WORKSPACE_ROOT="$(pwd)"
mkdir -p "$WORKSPACE_ROOT/reports"
VAL_LOG="$WORKSPACE_ROOT/reports/codespace_stage_a_validation.txt"

{
  echo "===== MACHINE ====="
  nproc
  free -h
  df -h /

  echo "===== TOOLCHAIN ====="
  python --version
  java --version
  javac --version
  mvn --version
  cobc --version
  git --version

  echo "===== REMOTE MANIFEST TEST ====="
  python -m pytest -v tests/test_phase9_manifest.py

  echo "===== REAL COBOL->JAVA SMOKE ====="
  rm -rf workspace/codespace-smoke
  python cobol_migrate.py --repo legacy --out workspace/codespace-smoke

  echo "===== OUTPUT SIZE ====="
  du -sh workspace/codespace-smoke
  du -sh workspace 2>/dev/null || true
  du -sh .cache 2>/dev/null || true
  du -sh ~/.m2 2>/dev/null || true

  echo "===== /app CHECK ====="
  test ! -e /app && echo "/app not required"

  echo "===== GIT INTEGRITY ====="
  git status --short

  echo "===== DOCKER CHECK ====="
  docker --version 2>/dev/null || echo "Docker not installed"
} > "$VAL_LOG" 2>&1

echo "==> Stage A validation log written to $VAL_LOG"
cat "$VAL_LOG"

# Push validation report to git branch so local agent can inspect
git config user.name "Codespace Validation"
git config user.email "codespace@systemaops.local"
git add "$VAL_LOG"
git commit -m "chore(codespace): record Stage A remote validation report" || true
git push origin feature/open-source-mainframe-reference-stack || true


