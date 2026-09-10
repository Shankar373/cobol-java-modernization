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
echo "==> Start the platform UI with: python ui.py --host 0.0.0.0 --port 8787"
