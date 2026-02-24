import pandas as pd


def aggregate_orders(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("client")
        .agg(total_purchased=("order_total", "sum"))
        .reset_index()
    )


def aggregate_payments(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("client")
        .agg(total_paid=("payment_amount", "sum"))
        .reset_index()
    )


def merge_financials(orders_df, payments_df):
    merged = orders_df.merge(payments_df, on="client", how="left")

    merged["total_paid"] = merged["total_paid"].fillna(0)
    merged["outstanding_balance"] = (
        merged["total_purchased"] - merged["total_paid"]
    )

    return merged