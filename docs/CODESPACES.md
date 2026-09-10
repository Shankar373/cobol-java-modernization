# GitHub Codespaces Guide — Zero-Cost Development Environment

This guide explains how to run heavy COBOL-to-Java modernization, compilation, testing, and dependency workloads in **GitHub Codespaces** using only the free personal-account quotas, offloading CPU, RAM, and disk storage from your local Windows laptop.

---

## 1. Included Quotas & Free-Tier Rules

GitHub personal accounts on the Free plan include:
- **120 core-hours** per calendar month
- **15 GB-month** of Codespaces storage quota per month

> [!IMPORTANT]
> **Understanding 15 GB-month:**  
> The 15 GB-month quota is a monthly storage consumption metric (e.g. 15 GB stored for 1 month, or 30 GB stored for 15 days), **not** the ephemeral VM disk size. The VM root filesystem has 32 GB of working disk space. To avoid exceeding the 15 GB-month storage quota, stopped codespaces should be deleted when not in active use.

### Strict Free-Tier Rules:
1. **Always select 2-core machines.** A 2-core machine burns 2 core-hours per wall-clock hour (giving 60 hours of active monthly usage). 4-core, 8-core, or 16-core machines burn quota 2x to 8x faster and risk unexpected shutdown.
2. **Never enable paid billing or add payment methods.**
3. **Keep prebuilds disabled.** Prebuilds consume both storage and core-hours in the background.

---

## 2. One-Time GitHub Account Configuration

Before creating your Codespace, configure your account-level timeouts to prevent accidental quota consumption:

1. Open your browser and navigate to:  
   **[https://github.com/settings/codespaces](https://github.com/settings/codespaces)**
2. Configure the following settings:
   - **Default idle timeout:** Select **15 minutes** (automatically suspends the Codespace when inactive).
   - **Default retention period:** Select **1 day** (automatically deletes unused stopped codespaces after 24 hours).
3. Under repository settings:
   - Verify that **Codespaces prebuilds** are **disabled** for this repository.

---

## 3. Creating and Starting the Codespace

1. Go to the repository on GitHub: `https://github.com/<owner>/Cobol-to-java-test`.
2. Click the green **Code** button.
3. Select the **Codespaces** tab.
4. Click the three dots (**`...`**) next to "Create codespace on..." and select **New with options...**.
5. Configure the launch dialog:
   - **Branch:** Select your working branch (e.g., `master` or feature branch).
   - **Devcontainer configuration:** `COBOL-to-Java Modernization Platform (Free Tier)`.
   - **Machine type:** Choose **2-core** (do **not** select 4, 8, or 16 cores).
6. Click **Create codespace**.

The first startup uses pre-cached devcontainer base images and completes in ~60–90 seconds.

---

## 4. Installed Toolchain

The devcontainer automatically provisions:
- **Python 3.12** (Standard Library + `requirements-dev.txt` for tests)
- **Eclipse Temurin JDK 17 (LTS)** (`javac`, `java`)
- **Apache Maven 3.9.6** (`mvn`)
- **GnuCOBOL 3.1.2** (`cobc`, `libcob`) installed natively for fast local baseline execution
- **PostgreSQL 16 client** (`psql`)
- **Docker-in-Docker** available on-demand for containerized tests

*Note: Maven dependencies resolve lazily on first build/test rather than downloading hundreds of megabytes during container creation.*

---

## 5. How to Run the Platform

### A. Modernization Interactive UI
Run the built-in HTTP server:
```bash
python ui.py --host 0.0.0.0 --port 8787
```
VS Code automatically detects port 8787 and provides a notification: **"Open in Browser"**. Click it to view the modernization workbench.

### B. CLI Modernization Pipeline
To run the full 13-stage modernization pipeline on the legacy reference repository:
```bash
python cobol_migrate.py --repo legacy --out workspace/my-run
```
Or with native Java track:
```bash
python cobol_migrate.py --repo legacy --out workspace/my-run --native-java
```

### C. Running Tests
Run the differential business equivalence smoke tests:
```bash
python -m pytest -v tests/e2e/differential/storage/test_redefines01.py \
                    tests/e2e/differential/numeric/test_sizeerr01.py \
                    tests/e2e/differential/files/test_filestat01.py
```
Run packaging and manifest regression tests:
```bash
python -m pytest -v tests/test_phase9_manifest.py
```

---

## 6. How to Stop the Codespace (Preserve Quota)

When you are done with your session, stop the Codespace immediately so it does not burn core-hours:

### From within VS Code:
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS) to open the Command Palette.
2. Type **`Codespaces: Stop Current Codespace`** and press **Enter**.

### From GitHub Web Dashboard:
1. Navigate to **[https://github.com/codespaces](https://github.com/codespaces)**.
2. Find your active codespace.
3. Click the three dots (**`...`**) on the right and click **Stop Codespace**.

---

## 7. Storage Management & Deletion

- When a codespace is stopped, its state is preserved, but it still consumes storage against your 15 GB-month quota.
- If you have finished your work and committed your code, delete the Codespace from **[https://github.com/codespaces](https://github.com/codespaces)**:
  - Click `...` -> **Delete**.
- You can recreate a clean Codespace at any time in under 90 seconds.
