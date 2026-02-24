import pandas as pd

def validate(df: pd.DataFrame, required_columns: set[str]) -> pd.DataFrame:
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df
