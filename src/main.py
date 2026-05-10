from __future__ import annotations

from pathlib import Path

from .collectors.sample_collector import load_sample_jobs
from .collectors.csv_collector import load_jobs_from_csv
from .config_loader import load_config
from .evaluator import evaluate_jobs
from .profile_loader import load_profile
from .writers.csv_writer import write_csv


def main() -> None:
    config = load_config(Path("config/config.json"))
    input_format = config["input"].get("input_format", "sample_json")
    if input_format == "csv":
        jobs = load_jobs_from_csv(Path(config["input"]["csv_jobs_path"]))
    elif input_format == "sample_json":
        jobs = load_sample_jobs(Path(config["input"]["sample_jobs_path"]))
    else:
        raise ValueError(f"未対応のinput_formatです: {input_format}. sample_json または csv を指定してください。")
    profile = load_profile(Path("config/profile.json"))
    results = evaluate_jobs(jobs, config, profile)
    write_csv(Path(config["output"]["result_csv_path"]), results)
    print(f"Wrote {len(results)} rows to {config['output']['result_csv_path']}")


if __name__ == "__main__":
    main()
