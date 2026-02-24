import pandas as pd

COLUMN_ALIASES = {
    "client_name": "client",
}

def standardize_columns(df):
    df = df.rename(columns=lambda c: c.strip().lower())

    for original, canonical in COLUMN_ALIASES.items():
        if original in df.columns:
            df = df.rename(columns={original: canonical})

    return df

def normalize(df: pd.DataFrame) -> pd.DataFrame:

    df["client"] = df["client"].str.strip().str.lower().str.title()
    df["date"] = pd.to_datetime(df["date"], errors="raise")

    return df

def transform_order(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df["order_total"] = df["quantity"] * df["unit_price"]
    return normalize(df)

def transform_payment(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df)
    df["payment_amount"] = df["payment_amount"].astype(float)
    return normalize(df)