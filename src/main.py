import shutil

import pandas as pd
import yaml
from loguru import logger

from aggregation import aggregate_orders, aggregate_payments, merge_financials
from ingestion import discover_input_files
from report import write_report
from transform import transform_order, transform_payment
from validation import validate
from utils import setup_logging, get_orders_and_payments

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    setup_logging(config["log_dir"])

    logger.info("Starting the data processing pipeline...")
    logger.info("Loading files from input directory...")

    orders_file, payments_file = None, None

    ORDERS_REQUIRED = {
        "order_id", "date", "client_name", "product", "quantity", "unit_price"
    }

    PAYMENTS_REQUIRED = {
        "payment_id", "date", "client", "payment_amount"
    }

    try:
        files = discover_input_files(config["input_dir"])
        orders_file, payments_file = get_orders_and_payments(files)
    except Exception as e:
        logger.error(f"Error during file discovery: {e}")
        return  # Stop execution if input files are not found
    
    orders_df = transform_order(validate(pd.read_csv(orders_file), ORDERS_REQUIRED))
    payments_df = transform_payment(validate(pd.read_csv(payments_file), PAYMENTS_REQUIRED))

    orders_summary = aggregate_orders(orders_df)
    payments_summary = aggregate_payments(payments_df)

    final_report = merge_financials(orders_summary, payments_summary)

    output_file = write_report(
        final_report,
        config["output_dir"],
        "receivables_summary",
    )

    # Archive processed files
    shutil.move(orders_file, config["archive_dir"])
    shutil.move(payments_file, config["archive_dir"])

    logger.info(f"Receivables report generated → {output_file}")

if __name__ == "__main__":
    main()