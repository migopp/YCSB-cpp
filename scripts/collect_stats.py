"""
collect_stats.py

Author: Michael Goppert <goppert@cs.utexas.edu>
Author: Will Bolduc <wbolduc@cs.utexas.edu>
"""

import json
import pandas as pd
from dataclasses import dataclass, field

@dataclass
class StatConfig:
    db_name: str
    workload: str
    threads: str
    data: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)

def read_all():
    with open("../raw_data.json", "r") as f:
        return json.load(f)

def write_one(cfg):
    try:
        with open("../filtered_data.json", "r") as f:
            old_data = json.load(f)
    except:
        old_data = {}

    old_data.setdefault(cfg.db_name, {}).setdefault(cfg.workload, {})[cfg.threads] = cfg.stats
    with open("../filtered_data.json", "w") as f:
        json.dump(old_data, f, indent=4)

def stat_one(cfg):
    raw_load_data = [d["load"] for d in cfg.data]
    raw_run_data = [d["run"] for d in cfg.data]
    load_df = pd.DataFrame(raw_load_data)
    run_df = pd.DataFrame(raw_run_data)
    load_agg = load_df.agg(["mean", "std"])
    run_agg = run_df.agg(["mean", "std"])
    cfg.stats = {
        "load": load_agg.round(3).to_dict(),
        "run": run_agg.round(3).to_dict()
    }

def main():
    raw_data = read_all()
    for db, d_rest in raw_data.items():
        for work, w_rest in d_rest.items():
            for threads, data in w_rest.items():
                cfg = StatConfig(db, work, threads, data)
                stat_one(cfg)
                write_one(cfg)

if __name__ == "__main__":
    main()
