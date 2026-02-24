from pathlib import Path
from loguru import logger


def discover_input_files(input_dir: str) -> list[Path]:
    """
    Scan the input directory for CSV files.
    Returns a list of file paths.
    """
    path = Path(input_dir)

    if not path.exists():
        logger.warning(f"Input directory does not exist: {input_dir}")
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    csv_files = list(path.glob("*.csv"))

    if not csv_files:
        logger.warning("No CSV files found.")
        raise FileNotFoundError("No CSV files found in the input directory.")

    logger.info(f"Discovered {len(csv_files)} file(s).")

    for file in csv_files:
        logger.info(f"Found file: {file.name}")

    return csv_files