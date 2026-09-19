import pandas as pd
from pathlib import Path

for name in ["CPS_Poseidon.parquet", "CPS_Triton.parquet", "OSS_Ceto.parquet"]:
    p = Path(f"data/processed/real/fuelcast/{name}")
    if p.exists():
        df = pd.read_parquet(p)
        print(f"{name}: vessel_type = {df['vessel_type'].unique()}, fuel_type = {df['fuel_type'].unique() if 'fuel_type' in df.columns else 'N/A'}")
    else:
        print(f"{name}: not found")
