"""
Failure Taxonomy and Root-Cause Analysis Module.
Categorizes constraint violations and run failures into the 10-class standard taxonomy:
1. assignment
2. capacity
3. fuel_compatibility
4. schedule
5. regulatory
6. numerical
7. stagnation
8. decoder_failure
9. repair_failure
10. other
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


TAXONOMY_CLASSES = [
    "assignment",
    "capacity",
    "fuel_compatibility",
    "schedule",
    "regulatory",
    "numerical",
    "stagnation",
    "decoder_failure",
    "repair_failure",
    "other",
]


def classify_violations(hard_violations: List[str], soft_penalties: Optional[Dict[str, float]] = None) -> Dict[str, int]:
    """Classifies a list of violation strings into taxonomy counts."""
    counts = {c: 0 for c in TAXONOMY_CLASSES}

    for v_str in hard_violations:
        v_lower = v_str.lower()
        if "duplicate" in v_lower or "unfulfilled" in v_lower or "assigned" in v_lower or "demand" in v_lower:
            counts["assignment"] += 1
        elif "deadweight" in v_lower or "capacity" in v_lower or "cargo" in v_lower:
            counts["capacity"] += 1
        elif "fuel" in v_lower or "incompatible fuel" in v_lower:
            counts["fuel_compatibility"] += 1
        elif "schedule" in v_lower or "deadline" in v_lower or "delay" in v_lower or "speed" in v_lower:
            counts["schedule"] += 1
        elif "cii" in v_lower or "fueleu" in v_lower or "regulatory" in v_lower:
            counts["regulatory"] += 1
        elif "nan" in v_lower or "inf" in v_lower:
            counts["numerical"] += 1
        else:
            counts["other"] += 1

    return counts


def generate_failure_taxonomy_report(runs_records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Summarizes failure occurrences across algorithms.
    """
    algo_counts: Dict[str, Dict[str, int]] = {}

    for r in runs_records:
        algo = r["algorithm"]
        if algo not in algo_counts:
            algo_counts[algo] = {c: 0 for c in TAXONOMY_CLASSES}
            algo_counts[algo]["total_runs"] = 0
            algo_counts[algo]["failed_runs"] = 0

        algo_counts[algo]["total_runs"] += 1
        is_feas = bool(r.get("is_feasible", r.get("feasible_at_end", False)))
        if not is_feas:
            algo_counts[algo]["failed_runs"] += 1
            raw_v = r.get("hard_violations", [])
            if isinstance(raw_v, str):
                v_list = [v.strip() for v in raw_v.split(";") if v.strip() and v.strip() != "NONE"]
            else:
                v_list = list(raw_v)
            viol_counts = classify_violations(v_list)
            for c, cnt in viol_counts.items():
                algo_counts[algo][c] += cnt

    report_rows = []
    for algo, data in algo_counts.items():
        row = {"algorithm": algo, "total_runs": data["total_runs"], "failed_runs": data["failed_runs"]}
        for c in TAXONOMY_CLASSES:
            row[c] = data[c]
        report_rows.append(row)

    return pd.DataFrame(report_rows)
