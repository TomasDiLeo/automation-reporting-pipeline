from pathlib import Path
from datetime import datetime
import pandas as pd


def write_report(df: pd.DataFrame, output_dir: str, prefix: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(output_dir) / f"{prefix}_{timestamp}.csv"

    df.to_csv(output_file, index=False)

    return output_file