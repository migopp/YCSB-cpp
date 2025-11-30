
"""
benchmark.py

Author: Michael Goppert <goppert@cs.utexas.edu>
Author: Will Bolduc <wbolduc@cs.utexas.edu>
"""

import argparse
import subprocess
import json
from dataclasses import dataclass

parser = argparse.ArgumentParser(description="Customize the YCSB-cpp measurement environment")
parser.add_argument("-d", "--db", nargs="+", help="Database(s) to benchmark")
parser.add_argument("-w", "--workload", nargs="+", help="Workloads on which to benchmark")
parser.add_argument("-m", "--max-threads", type=int, default=1, help="Max number of threads to run on each configuration")
parser.add_argument("-t", "--trials", type=int, default=1, help="Number of trials of configuration to run")

@dataclass
class TrialConfig:
    db_name: str
    workload: str
    threads: int
    dist: str

    def cmd(self):
        req_dist = f"-p requestdistribution={self.dist}" if self.dist != "uniform" else ""
        return f"../build/ycsb -db {self.db_name} -threads {self.threads} -load -run -P ../workloads/workload{self.workload} {req_dist}"

dbs = []
workloads = []
max_threads = 0
trials = 0

def bench_one(cfg):
    c = cfg.cmd()
    print(f"$ {c}")
    r = subprocess.run(c, capture_output=True, text=True, shell=True, check=True)
    raw_o = r.stdout.strip().splitlines()
    data = {
        "load": {
            "runtime": None,
            "operations": None,
            "throughput": None
        },
        "run": {
            "runtime": None,
            "operations": None,
            "throughput": None
        }
    }
    for o in raw_o:
        metric_name, raw_metric_data = o.split(": ")
        data_metric_cat = "bill"
        data_metric_name = "chubbz"
        data_metric_data = float(raw_metric_data)

        if "Run" in metric_name:
            data_metric_cat = "run"
        else:
            data_metric_cat = "load"

        if "runtime" in metric_name:
            data_metric_name = "runtime"
        elif "operations" in metric_name:
            data_metric_name = "operations"
        elif "throughput" in metric_name:
            data_metric_name = "throughput"

        data[data_metric_cat][data_metric_name] = data_metric_data
    return data

def write_one(cfg, data):
    try:
        with open("../raw_data.json", "r") as f:
            old_data = json.load(f)
    except:
        old_data = {
            db: {
                work: {
                    cfg.dist: {
                        str(t): [] for t in range(1, max_threads + 1)
                    }
                } for work in workloads
            } for db in dbs
        }

    old_data.setdefault(cfg.db_name, {}).setdefault(cfg.workload, {}).setdefault(cfg.dist, {}).setdefault(str(cfg.threads), []).append(data)
    with open("../raw_data.json", "w") as f:
        json.dump(old_data, f, indent=4)

def main():
    global dbs, workloads, max_threads, trials

    args = parser.parse_args()
    dbs = args.db
    workloads = args.workload
    max_threads = args.max_threads
    trials = args.trials

    for tc in range(1, max_threads + 1):
        for db in dbs:
            for work in workloads:
                for req_dist in ["uniform", "zipfian"]:
                    for tr in range(trials):
                        cfg = TrialConfig(db, work, tc, req_dist)
                        data = bench_one(cfg)
                        write_one(cfg, data)

if __name__ == "__main__":
    main()
