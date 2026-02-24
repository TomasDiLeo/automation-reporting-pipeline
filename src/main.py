import yaml
from ingestion import discover_input_files
from utils import setup_logging

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()

    setup_logging(config["log_dir"])

    print("Starting the data processing pipeline...")

    files = discover_input_files(config["input_dir"])

    print(f"Discovered {len(files)} file(s) for processing.")

if __name__ == "__main__":
    main()