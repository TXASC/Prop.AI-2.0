import os
import json
import csv
from datetime import datetime
from app.core.utils.time import utc_now

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")



def write_daily_board(date, board_data, run_id, model_version):
    fname = f"{OUTPUT_DIR}/daily_board_{date}.json"
    artifact = {
        "run_id": run_id,
        "model_version": model_version,
        "date": date,
        "markets": board_data
    }
    with open(fname, "w") as f:
        json.dump(artifact, f, indent=2)



def write_daily_edges(date, edges, run_id, model_version):
    fname = f"{OUTPUT_DIR}/daily_edges_{date}.csv"
    if not edges:
        # Write only header if no edges
        with open(fname, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["run_id", "model_version"])
            writer.writeheader()
        return
    with open(fname, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["run_id", "model_version"] + list(edges[0].keys()))
        writer.writeheader()
        for edge in edges:
            edge_row = {"run_id": run_id, "model_version": model_version}
            edge_row.update(edge)
            writer.writerow(edge_row)



def write_daily_metrics(date, metrics, run_id, model_version):
    fname = f"{OUTPUT_DIR}/daily_metrics_{date}.json"
    artifact = {
        "run_id": run_id,
        "model_version": model_version,
        "date": date,
        "metrics": metrics
    }
    with open(fname, "w") as f:
        json.dump(artifact, f, indent=2)
