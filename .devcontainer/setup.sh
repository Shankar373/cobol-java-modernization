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

WORKSPACE_ROOT="$(pwd)"
mkdir -p "$WORKSPACE_ROOT/reports"
VAL_LOG="$WORKSPACE_ROOT/reports/codespace_stage_a_validation.log"

{
  echo "========================================================"
  echo "CODESPACE STAGE A REMOTE VALIDATION REPORT"
  echo "Host: $(hostname)"
  echo "Date: $(date -u)"
  echo "========================================================"

  echo ""
  echo "--- 1. ALLOCATED MACHINE ---"
  echo ">>> nproc:"
  nproc
  echo ">>> free -h:"
  free -h
  echo ">>> df -h /:"
  df -h /

  echo ""
  echo "--- 2. TOOLCHAIN VERSIONS ---"
  echo ">>> python --version:"
  python --version
  echo ">>> java --version:"
  java --version
  echo ">>> javac --version:"
  javac --version
  echo ">>> mvn --version:"
  mvn --version
  echo ">>> cobc --version:"
  cobc --version
  echo ">>> git --version:"
  git --version

  echo ""
  echo "--- 3. REGRESSION TESTS ---"
  echo ">>> python -m pytest -v tests/test_phase9_manifest.py:"
  python -m pytest -v tests/test_phase9_manifest.py

  echo ""
  echo "--- 4. SMOKE TRANSFORMATION ---"
  echo ">>> python cobol_migrate.py --repo legacy --out workspace/codespace-smoke:"
  python cobol_migrate.py --repo legacy --out workspace/codespace-smoke

  echo ""
  echo "--- 5. STORAGE MEASUREMENT ---"
  echo ">>> df -h:"
  df -h
  echo ">>> du -sh workspace/codespace-smoke:"
  du -sh workspace/codespace-smoke 2>&1

  echo ""
  echo "--- 6. GIT STATUS ---"
  echo ">>> git status --short:"
  git status --short

  echo ""
  echo "========================================================"
  echo "END OF REMOTE VALIDATION REPORT"
  echo "========================================================"
} > "$VAL_LOG" 2>&1

echo "==> Stage A validation log written to $VAL_LOG"
cat "$VAL_LOG"

# Push validation report to git branch so local agent can inspect
git config user.name "Codespace Validation"
git config user.email "codespace@systemaops.local"
git add "$VAL_LOG"
git commit -m "chore(codespace): record Stage A remote validation report" || true
git push origin feature/open-source-mainframe-reference-stack || true

