"""
Benchmark reproducibility and reporting utilities.
"""

from typing import Dict, Any, List
import pandas as pd


def generate_benchmark_markdown_table(summary_data: List[Dict[str, Any]]) -> str:
    """Format benchmark results as a clean Markdown comparison table."""
    df = pd.DataFrame(summary_data)
    return df.to_markdown(index=False)
