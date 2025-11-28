"""
graph.py

Author: Michael Goppert <goppert@cs.utexas.edu>
Author: Will Bolduc <wbolduc@cs.utexas.edu>
"""
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import subprocess
from dataclasses import dataclass, field

@dataclass
class GraphConfig:
    linestyles: dict[str, str] = field(default_factory=dict)
    colors: dict[str, str] = field(default_factory=dict)
    markers: dict[str, str] = field(default_factory=dict)

    def __init__(self, filtered_data):
        self.linestyles = {}
        self.colors = {}
        self.markers = {}

        num_dbs = len(filtered_data)
        if num_dbs > 4:
            raise NotImplementedError
        l_list = ["solid", "dotted", "dashed", "dashdot"]
        c_list = plt.cm.Greys(np.linspace(0.3, 0.8, num_dbs))
        m_list = ["o", "s", "^", "d"]

        i = 0
        for db, _ in filtered_data.items():
            self.linestyles[db] = l_list[i]
            self.colors[db] = c_list[i]
            self.markers[db] = m_list[i]
            i += 1

@dataclass
class GraphTask:
    workload: str
    stage: str
    metric: str
    dbs: list[str] = field(default_factory=list)

    def __str__(self):
        me2 = ""
        for db in self.dbs:
            me2 += db + "-"
        me2 += self.workload + "-" + self.stage + "-" + self.metric
        return me2

    def axes(self):
        x = "number of threads"
        units = ""
        if self.metric == "runtime":
            units = "sec"
        elif self.metric == "operations":
            units = "mops"
        else:
            units = "mops/sec"
        y = f"{self.stage} - {self.metric} ({units})"
        return (x, y)

    def title(self):
        if self.workload == "a":
            return "50% Reads, 50% Updates"
        elif self.workload == "b":
            return "95% Reads, 5% Updates"
        elif self.workload == "c":
            return "100% Reads"
        elif self.workload == "d":
            return "95% Reads, 5% Inserts"
        elif self.workload == "e":
            return "95% Scans, 5% Inserts"
        elif self.workload == "f":
            return "50% Reads, 50% RMW"
        else:
            raise NotImplementedError

def read_all():
    with open("../filtered_data.json", "r") as f:
        return json.load(f)

def extract_from(task, data):
    # Should all have data for same set of thread counts. (?)
    x = [int(i) for i in data[task.dbs[0]][task.workload]]
    base = {db: {"mean": [0 for i in x], "std": [0 for i in x]} for db in task.dbs}
    for i in x:
        for db in task.dbs:
            base[db]["mean"][i-1] = data[db][task.workload][str(i)][task.stage][task.metric]["mean"]
            base[db]["std"][i-1] = data[db][task.workload][str(i)][task.stage][task.metric]["std"]
            if task.metric == "throughput":
                base[db]["mean"][i-1] /= 1000000
    return (x, base)

def graph_one(cfg, task, data):
    plt.figure(figsize=(6, 4))

    x, y_map = extract_from(task, data)
    for db in y_map:
        y = y_map[db]["mean"]
        std = y_map[db]["std"]
        plt.errorbar(x, y, yerr=std, fmt=cfg.markers[db], linestyle=cfg.linestyles[db], color=cfg.colors[db], capsize=4, label=db.split("_db")[0])

    x_axis, y_axis = task.axes()
    tit = task.title()
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(tit)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.subplots_adjust(right=0.75)
    plt.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False)

    subprocess.run(["mkdir", "-p", "../graphs"])
    plt.savefig(f"../graphs/{str(task)}", dpi=300, bbox_inches="tight")
    plt.close()

def main():
    filtered_data = read_all()
    cfg = GraphConfig(filtered_data)

    # Tasks.
    ojdk_only_workloada_throughput = GraphTask("a", "run", "throughput", ["ojdkchm_db"])

    # Run 'em.
    graph_one(cfg, ojdk_only_workloada_throughput, filtered_data)

if __name__ == "__main__":
    main()
