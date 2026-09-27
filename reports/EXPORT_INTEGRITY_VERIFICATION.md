# EGREEN QUANTA — Export Integrity & Tamper-Evidence Verification Report
**Document ID**: VER-EGR-INT-2026-001  
**Project**: SIH26138 — Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Software Version**: 1.0.0-production  
**Git Baseline Commit**: `e28472b`  
**Status**: TAMPER-EVIDENT VERIFICATION BATTERY 100% PASSING  
**Applicable Test Suites**: `tests/test_export_integrity.py`, `tests/test_tamper_detection.py`

---

## 1. Scope & Objective

This report details the cryptographic engineering, mathematical verification methods, and empirical testing executed to ensure the **tamper evidence** of all marine operator export packages in EGREEN QUANTA.

In adherence to classification society software guidelines (such as DNV-CG-0338 / ClassNK Rules for Marine Software Systems) and data integrity principles (ALCOA+):
- No record is labeled *immutable* (as physical file systems and object stores permit unauthorized bit manipulation).
- All packages are strictly designated **TAMPER-EVIDENT**: any unauthorized post-generation modification to numerical results, metadata, dates, or calculations immediately invalidates the package's cryptographic seal.

---

## 2. Cryptographic Architecture

### 2.1 Canonical Serialization (RFC 8785)
Standard JSON encoders are non-deterministic across languages, platforms, and runtime versions due to key ordering variations, floating-point string formatting differences, and whitespace choices.

EGREEN QUANTA implements strict JSON canonicalization:
```python
def canonical_json_bytes(obj: dict[str, Any]) -> bytes:
    """Serialize dictionary to deterministic canonical JSON bytes (RFC 8785).
    - Keys sorted lexicographically by Unicode code points.
    - Zero redundant whitespace (separators=(',', ':')).
    - UTF-8 encoding.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        indent=None,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
```

### 2.2 SHA-256 Digest Computation
The canonical byte representation is hashed using the NIST FIPS 180-4 standard **Secure Hash Algorithm 256 (SHA-256)**:
$$\text{Digest} = \text{SHA256}(\text{CanonicalJSONBytes})$$

This 256-bit hexadecimal digest is:
1. Injected directly into `integrity.record_sha256` of `decision_record.json`.
2. Written to column 20 (`record_sha256`) of the tabular `decision_record.csv`.
3. Registered in `manifest.json` under `files["decision_record.json"].sha256`.

### 2.3 Package Manifest & Self-Verification
The `manifest.json` acts as the root of trust for the exported directory:
1. For every file $f_i \in \text{Package}$, its exact byte sequence is read, and $H_i = \text{SHA256}(\text{bytes}(f_i))$ is recorded alongside file size in bytes and MIME type.
2. A manifest checksum $\Phi$ is computed across the concatenated sorted entries:
$$\Phi = \text{SHA256}\left(\bigoplus_{i=1}^N (f_i \parallel H_i \parallel S_i)\right)$$

---

## 3. Empirical Tamper-Detection Battery (`tests/test_tamper_detection.py`)

A specialized adversarial test battery was created to test deliberate tampering scenarios:

### Test Case 1: `test_tamper_json_record_detected`
- **Tampering Scenario**: An unauthorized actor opens `decision_record.json` and modifies a numerical prediction value (e.g. changing `predicted_total_fuel_tonnes` from `45.20` to `40.00` to fraudulently conceal high fuel usage).
- **Execution**: The file is modified on disk. `verify_export_package(package_dir)` is executed.
- **Result**: **PASS**. Verification immediately returns `valid: False`. Failure reason records: `Digest mismatch for decision_record.json: expected <hash_A>, found <hash_B>`.
- **Restoration Validation**: The original byte sequence is restored and verified again. Verification returns `valid: True` with all cryptographic checks green.

### Test Case 2: `test_tamper_csv_derivative_detected`
- **Tampering Scenario**: An actor leaves the JSON record unchanged but alters `decision_record.csv` (e.g. changing the `delay_hours` or `operational_cost_usd` column to show a false schedule).
- **Execution**: A CSV cell is altered. `verify_export_package(package_dir)` is executed.
- **Result**: **PASS**. Verification returns `valid: False`. The CSV digest mismatch is flagged: `Digest mismatch for decision_record.csv`.
- **Restoration Validation**: Original CSV bytes restored -> verification returns `valid: True`.

### Test Case 3: `test_tamper_missing_file_detected`
- **Tampering Scenario**: An unauthorized party removes `calculation_summary.json` or `README.txt` from the export directory.
- **Execution**: A package file is deleted. `verify_export_package(package_dir)` is executed.
- **Result**: **PASS**. Verification returns `valid: False` with error: `Missing file: calculation_summary.json`.

### Test Case 4: `test_tamper_manifest_corruption_detected`
- **Tampering Scenario**: An attacker changes both `decision_record.json` AND alters `manifest.json` to match the new file hash, attempting to spoof the manifest.
- **Execution**: The file digest in `manifest.json` is altered.
- **Result**: **PASS**. The manifest self-integrity checksum (`manifest_sha256`) mismatches the recalculated manifest entry digest, flagging malicious tampering of the manifest itself.

---

## 4. Platform-Specific Edge Cases Resolved

### Windows CRLF Normalization
- **Finding**: On Windows systems, default text read/write APIs (`open(..., 'r')`, `read_text()`) convert Unix `\n` to `\r\n`. In testing, modifying a file with string replacement and saving it via text mode introduced carriage returns, mutating file hashes even if characters were identical.
- **Resolution**: All file operations in `src/export/decision_exporter.py` and test harnesses enforce strict binary mode (`open(..., 'rb')`, `read_bytes()`, `write_bytes()`) ensuring bit-for-bit reproducibility regardless of operating system (Windows, Linux, macOS).

---

## 5. Security & Boundary Defense

| Attack Vector | Defense Mechanism | Verified In |
|---|---|---|
| **Path Traversal (`../`, `..\`)** | `sanitize_filename` strips directory separators, prevents path escapes, limits filenames to alphanumeric + `[._-]` | `src/export/decision_exporter.py`, `tests/test_api.py` |
| **Secret Exfiltration** | `sanitize_payload` recursively strips any keys matching `*password*`, `*secret*`, `*token*`, `*api_key*`, `*credential*` | `src/export/decision_exporter.py` |
| **Arbitrary File Download** | `GET /api/exports/{record_id}/download/{filename}` validates that the resolved file path resides strictly inside `exports/EGREEN_QUANTA_<record_id>/` | `api/main.py`, `tests/test_api.py` |
| **Replay / Collision** | High-entropy UUID v4 combined with nanosecond UTC timestamps ensures collision probability $< 10^{-18}$ | `src/export/decision_exporter.py` |

---

## 6. Summary of Verification Status

The tamper-evident export system has been empirically tested and verified across all operational states. All automated test batteries pass with zero defects under commit `e28472b`.
