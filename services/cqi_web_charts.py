# services/cqi_web_charts.py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import numpy as np

def save_co_cqi_chart(co_attainment, target_levels, output_path):
    labels = sorted(co_attainment.keys())
    achieved = [co_attainment[c]["Attainment_Level"] for c in labels]
    target = [float(target_levels.get(c, 2.0)) for c in labels]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(6, 4))

    plt.bar(x - width/2, achieved, width, label="Achieved")
    plt.bar(x + width/2, target, width, label="Target")

    plt.xticks(x, labels)
    plt.ylim(0, 3)
    plt.ylabel("Attainment Level")
    plt.title("CO Attainment: Targeted vs Achieved")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_po_cqi_chart(po_attainment, target_levels, output_path):
    labels = sorted(po_attainment.keys())
    achieved = [po_attainment[p]["PO_Level"] for p in labels]
    target = [float(target_levels.get(p, 2.0)) for p in labels]

    x = np.arange(len(labels))
    width = 0.35

    plt.figure(figsize=(6, 4))

    plt.bar(x - width/2, achieved, width, label="Achieved")
    plt.bar(x + width/2, target, width, label="Target")

    plt.xticks(x, labels)
    plt.ylim(0, 3)
    plt.ylabel("Attainment Level")
    plt.title("PO Attainment: Targeted vs Achieved")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
