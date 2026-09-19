# Installation Guide: Egreen Quanta (v1.0.0)

This guide provides instructions for installing and configuring Egreen Quanta in a clean Python environment.

---

## 1. System Requirements

- **Operating System:** Windows 10/11 (x86_64), Linux (Ubuntu 20.04+, RHEL 8+), or macOS (12.0+).
- **CPU:** 4+ physical cores recommended (16 cores utilized for master benchmarks).
- **RAM:** Minimum 8 GB (16 GB recommended for full fleet simulation).
- **Python Version:** Python 3.10 to 3.14 (tested and locked on CPython 3.14.0).
- **Disk Space:** ~500 MB for repository, telemetry parquet files, and cached physics arrays.

---

## 2. Environment Setup

### 2.1 Clone or Navigate to Repository Root
```bash
cd sih26138_platform
```

### 2.2 Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

Install the frozen production dependencies from `requirements-lock.txt`:
```bash
pip install -r requirements-lock.txt
```

Alternatively, standard dependencies can be installed via:
```bash
pip install numpy scipy pandas pyarrow scikit-learn lightgbm matplotlib pyyaml pytest
```

---

## 4. Verify Installation

Run the automated single-command verification runner:
```bash
python reproduce_release.py
```
If all checks display `PASS`, your environment is fully configured and ready for production inference and jury demonstration.
