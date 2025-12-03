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
        l_list = ["solid", "dotted", "dashed", "dashdot"]
        c_list = plt.cm.Greys(np.linspace(0.3, 0.8, num_dbs))
        m_list = ["o", "s", "^", "d"]

        i = 0
        for db, _ in filtered_data.items():
            self.linestyles[db] = l_list[i % 4]
            self.colors[db] = c_list[i]
            self.markers[db] = m_list[i % 4]
            i += 1

@dataclass
class GraphTask:
    workload: str
    stage: str
    metric: str
    dist: str
    dbs: list[str] = field(default_factory=list)

    def __str__(self):
        me2 = ""
        for db in self.dbs:
            me2 += db + "-"
        me2 += self.workload + "-" + self.stage + "-" + self.metric + "-" + self.dist
        return me2

    def axes(self):
        x = "number of threads"
        units = ""
        if self.metric == "runtime":
            units = "sec"
        elif self.metric == "operations":
            units = "mops"
        elif self.metric == "throughput":
            units = "mops/sec"
        elif "rss" in self.metric:
            units = "kb"
        y = f"{self.stage} - {self.metric} ({units})"
        return (x, y)

    def title(self):
        workload_map = {
            "a": "50% reads, 50% updates",
            "b": "95% reads, 5% updates",
            "c": "100% reads",
            "d": "95% reads, 5% inserts",
            "e": "50% scans, 5% updates",
            "f": "50% reads, 50% rwm",
            "L": "90% bad reads, 5% reads, 5% insert"
        }
        return f"{workload_map[self.workload]}, {self.dist}"

def read_all():
    with open("../filtered_data.json", "r") as f:
        return json.load(f)

def extract_from(task, data):
    # Should all have data for same set of thread counts. (?)
    x = [int(i) for i in data[task.dbs[0]][task.workload][task.dist]]
    base = {db: {"mean": [0 for i in x], "std": [0 for i in x]} for db in task.dbs}
    for i in x:
        for db in task.dbs:
            base[db]["mean"][i-1] = data[db][task.workload][task.dist][str(i)][task.stage][task.metric]["mean"]
            base[db]["std"][i-1] = data[db][task.workload][task.dist][str(i)][task.stage][task.metric]["std"]
            if task.metric == "throughput":
                base[db]["mean"][i-1] /= 1000000
                base[db]["std"][i-1] /= 1000000
    return (x, base)

def graph_one(cfg, task, data):
    plt.figure(figsize=(6, 4))

    x, y_map = extract_from(task, data)
    for db in y_map:
        y = y_map[db]["mean"]
        std = y_map[db]["std"]
        plt.errorbar(
            x, y, yerr=std,
            fmt=cfg.markers[db],
            linestyle=cfg.linestyles[db],
            color=cfg.colors[db],
            ecolor="black",
            capsize=4,
            label=db.split("_db")[0]
        )

    plt.axvline(x=6, color="black", linestyle=":", linewidth=1.5)

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

    # ConcurrentHashMap Uniform
    ojdk_oa_a_thru_u = GraphTask("a", "run", "throughput", "uniform", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_b_thru_u = GraphTask("b", "run", "throughput", "uniform", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_c_thru_u = GraphTask("c", "run", "throughput", "uniform", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_d_thru_u = GraphTask("d", "run", "throughput", "uniform", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_f_thru_u = GraphTask("f", "run", "throughput", "uniform", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    graph_one(cfg, ojdk_oa_a_thru_u, filtered_data)
    graph_one(cfg, ojdk_oa_b_thru_u, filtered_data)
    graph_one(cfg, ojdk_oa_c_thru_u, filtered_data)
    graph_one(cfg, ojdk_oa_d_thru_u, filtered_data)
    graph_one(cfg, ojdk_oa_f_thru_u, filtered_data)

    # ConcurrentHashMap Zipfian
    ojdk_oa_a_thru_z = GraphTask("a", "run", "throughput", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_b_thru_z = GraphTask("b", "run", "throughput", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_c_thru_z = GraphTask("c", "run", "throughput", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_d_thru_z = GraphTask("d", "run", "throughput", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_f_thru_z = GraphTask("f", "run", "throughput", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    graph_one(cfg, ojdk_oa_a_thru_z, filtered_data)
    graph_one(cfg, ojdk_oa_b_thru_z, filtered_data)
    graph_one(cfg, ojdk_oa_c_thru_z, filtered_data)
    graph_one(cfg, ojdk_oa_d_thru_z, filtered_data)
    graph_one(cfg, ojdk_oa_f_thru_z, filtered_data)

    ojdk_oa_a_mrss_z = GraphTask("a", "tot", "max rss", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_b_mrss_z = GraphTask("b", "tot", "max rss", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_c_mrss_z = GraphTask("c", "tot", "max rss", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_d_mrss_z = GraphTask("d", "tot", "max rss", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    ojdk_oa_f_mrss_z = GraphTask("f", "tot", "max rss", "zipfian", ["ojdkchm_oa_db", "ojdkchm_db", "rwl_db"])
    graph_one(cfg, ojdk_oa_a_mrss_z, filtered_data)
    graph_one(cfg, ojdk_oa_b_mrss_z, filtered_data)
    graph_one(cfg, ojdk_oa_c_mrss_z, filtered_data)
    graph_one(cfg, ojdk_oa_d_mrss_z, filtered_data)
    graph_one(cfg, ojdk_oa_f_mrss_z, filtered_data)

    ojdk_a_thru_z = GraphTask("a", "run", "throughput", "zipfian", ["ojdkchm_db", "rwl_db"])
    graph_one(cfg, ojdk_a_thru_z, filtered_data)

    # sync.Map Uniform
    gsm_a_thru_u = GraphTask("a", "run", "throughput", "uniform", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_b_thru_u = GraphTask("b", "run", "throughput", "uniform", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_c_thru_u = GraphTask("c", "run", "throughput", "uniform", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_d_thru_u = GraphTask("d", "run", "throughput", "uniform", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_f_thru_u = GraphTask("f", "run", "throughput", "uniform", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    graph_one(cfg, gsm_a_thru_u, filtered_data)
    graph_one(cfg, gsm_b_thru_u, filtered_data)
    graph_one(cfg, gsm_c_thru_u, filtered_data)
    graph_one(cfg, gsm_d_thru_u, filtered_data)
    graph_one(cfg, gsm_f_thru_u, filtered_data)

    gsm_L_thru_u = GraphTask("L", "run", "throughput", "uniform", ["gsm_db", "gsm_diom_db", "gsm_diom_ii_db"])
    graph_one(cfg, gsm_L_thru_u, filtered_data)

    # sync.Map Zipfian
    gsm_a_thru_z = GraphTask("a", "run", "throughput", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_b_thru_z = GraphTask("b", "run", "throughput", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_c_thru_z = GraphTask("c", "run", "throughput", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_d_thru_z = GraphTask("d", "run", "throughput", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_f_thru_z = GraphTask("f", "run", "throughput", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    graph_one(cfg, gsm_a_thru_z, filtered_data)
    graph_one(cfg, gsm_b_thru_z, filtered_data)
    graph_one(cfg, gsm_c_thru_z, filtered_data)
    graph_one(cfg, gsm_d_thru_z, filtered_data)
    graph_one(cfg, gsm_f_thru_z, filtered_data)

    gsm_a_mrss_z = GraphTask("a", "tot", "max rss", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_b_mrss_z = GraphTask("b", "tot", "max rss", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_c_mrss_z = GraphTask("c", "tot", "max rss", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_d_mrss_z = GraphTask("d", "tot", "max rss", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    gsm_f_mrss_z = GraphTask("f", "tot", "max rss", "zipfian", ["gsm_db", "gsm_diom_ii_db", "rwl_db"])
    graph_one(cfg, gsm_a_mrss_z, filtered_data)
    graph_one(cfg, gsm_b_mrss_z, filtered_data)
    graph_one(cfg, gsm_c_mrss_z, filtered_data)
    graph_one(cfg, gsm_d_mrss_z, filtered_data)
    graph_one(cfg, gsm_f_mrss_z, filtered_data)

    gsm_L_thru_v = GraphTask("L", "run", "throughput", "zipfian", ["gsm_db", "gsm_diom_db", "gsm_diom_ii_db"])
    graph_one(cfg, gsm_L_thru_v, filtered_data)

    # RWLock Uniform
    rwl_b_thru_u = GraphTask("b", "run", "throughput", "uniform", ["rwl_db"])
    graph_one(cfg, rwl_b_thru_u, filtered_data)

    # RWLock Zipfian
    rwl_b_thru_z = GraphTask("b", "run", "throughput", "zipfian", ["rwl_db"])
    graph_one(cfg, rwl_b_thru_z, filtered_data)

    # Uniform
    gsm_ojdk_rwl_a_thru_u = GraphTask("a", "run", "throughput", "uniform", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_b_thru_u = GraphTask("b", "run", "throughput", "uniform", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_c_thru_u = GraphTask("c", "run", "throughput", "uniform", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_d_thru_u = GraphTask("d", "run", "throughput", "uniform", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_f_thru_u = GraphTask("f", "run", "throughput", "uniform", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    graph_one(cfg, gsm_ojdk_rwl_a_thru_u, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_b_thru_u, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_c_thru_u, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_d_thru_u, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_f_thru_u, filtered_data)

    # Zipfian
    gsm_ojdk_rwl_a_thru_z = GraphTask("a", "run", "throughput", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_b_thru_z = GraphTask("b", "run", "throughput", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_c_thru_z = GraphTask("c", "run", "throughput", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_d_thru_z = GraphTask("d", "run", "throughput", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_f_thru_z = GraphTask("f", "run", "throughput", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    graph_one(cfg, gsm_ojdk_rwl_a_thru_z, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_b_thru_z, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_c_thru_z, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_d_thru_z, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_f_thru_z, filtered_data)

    gsm_ojdk_rwl_a_mrss_z = GraphTask("a", "tot", "max rss", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_b_mrss_z = GraphTask("b", "tot", "max rss", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_c_mrss_z = GraphTask("c", "tot", "max rss", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_d_mrss_z = GraphTask("d", "tot", "max rss", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    gsm_ojdk_rwl_f_mrss_z = GraphTask("f", "tot", "max rss", "zipfian", ["gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    graph_one(cfg, gsm_ojdk_rwl_a_mrss_z, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_b_mrss_z, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_c_mrss_z, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_d_mrss_z, filtered_data)
    graph_one(cfg, gsm_ojdk_rwl_f_mrss_z, filtered_data)

    gsm_base_ojdk_rwl_a_thru_z = GraphTask("a", "run", "throughput", "zipfian", ["gsm_db", "ojdkchm_oa_db", "rwl_db"])
    graph_one(cfg, gsm_base_ojdk_rwl_a_thru_z, filtered_data)

    gsm_both_ojdk_rwl_a_thru_z = GraphTask("a", "run", "throughput", "zipfian", ["gsm_db", "gsm_diom_ii_db", "ojdkchm_oa_db", "rwl_db"])
    graph_one(cfg, gsm_both_ojdk_rwl_a_thru_z, filtered_data)

if __name__ == "__main__":
    main()
