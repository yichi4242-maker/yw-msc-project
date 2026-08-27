import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from config import (
    OUTPUT_DIR,
    PLOT_FILE,
    RESULT_CSV,
    TASK_COUNT_CSV,
    TASK_COUNT_PLOT_FILE_10458,
    TASK_COUNT_PLOT_FILE_SAMETIME,
    TASK_COUNT_PLOT_FILE,
    TASK_COUNT_VALUES,
    TASK_MAP_PLOT_FILE,
    TASK_MIX_CONFIGS,
    TASK_MIX_CSV,
    TASK_MIX_PLOT_FILE,
    UAV_COUNTS,
    UAV_BALANCE_PLOT_FILE,
    UAV_COUNT_PLOT_FILE_10458,
    UAV_COUNT_PLOT_FILE_SAMETIME,
)
from experiment import ExperimentRow


LINE_STYLE_MAP = {
    "greedy_auction": {"label": "Greedy + Auction", "marker": "o", "color": "#1f77b4"},
    "distributed_best_cost": {"label": "Distributed Best-Cost", "marker": "^", "color": "#2ca02c"},
    "centralised_greedy": {"label": "Centralised Greedy", "marker": "D", "color": "#ff7f0e"},
    "random": {"label": "Random Baseline", "marker": "s", "color": "#7f7f7f"},
}

BAR_LABEL_MAP = {
    "greedy_auction": "Greedy + Auction",
    "distributed_best_cost": "Distributed Best-Cost",
    "centralised_greedy": "Centralised Greedy",
    "random": "Random Baseline",
}


def ensure_output_dir(base_dir: Path) -> Path:
    output_dir = base_dir / OUTPUT_DIR
    output_dir.mkdir(exist_ok=True)
    return output_dir


def save_results_csv(rows: list[ExperimentRow], output_dir: Path, filename: str) -> Path:
    csv_path = output_dir / filename
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["scenario", "method", "x_value", "run_index", "completion_time"])
        for row in rows:
            writer.writerow([row.scenario, row.method, row.x_value, row.run_index, row.completion_time])
    return csv_path


def plot_summary(summary: dict[str, dict[str, float]], output_dir: Path) -> Path:
    plot_path = output_dir / PLOT_FILE

    plt.figure(figsize=(8, 5))
    for method, style in LINE_STYLE_MAP.items():
        if method not in summary:
            continue
        plt.plot(
            UAV_COUNTS,
            [summary[method][str(count)] for count in UAV_COUNTS],
            marker=style["marker"],
            color=style["color"],
            linewidth=2,
            label=style["label"],
        )

    plt.title("Average Mission Completion Time vs Number of UAVs")
    plt.xlabel("Number of UAVs")
    plt.ylabel("Average Mission Completion Time")
    plt.xticks(UAV_COUNTS)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=200)
    plt.close()

    return plot_path


def plot_summary_to_file(
    summary: dict[str, dict[str, float]],
    output_dir: Path,
    filename: str,
    title: str,
    x_values: list[int],
    x_label: str,
) -> Path:
    plot_path = output_dir / filename

    plt.figure(figsize=(8, 5))
    for method, style in LINE_STYLE_MAP.items():
        if method not in summary:
            continue
        plt.plot(
            x_values,
            [summary[method][str(count)] for count in x_values],
            marker=style["marker"],
            color=style["color"],
            linewidth=2,
            label=style["label"],
        )

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel("Average Mission Completion Time")
    plt.xticks(x_values)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=200)
    plt.close()

    return plot_path


def plot_task_count_summary(summary: dict[str, dict[str, float]], output_dir: Path) -> Path:
    return plot_summary_to_file(
        summary,
        output_dir,
        TASK_COUNT_PLOT_FILE,
        "Average Mission Completion Time vs Number of Tasks",
        TASK_COUNT_VALUES,
        "Number of Tasks",
    )


def plot_task_mix_summary(summary: dict[str, dict[str, float]], output_dir: Path) -> Path:
    plot_path = output_dir / TASK_MIX_PLOT_FILE
    labels = [label for label, _ in TASK_MIX_CONFIGS]
    x = np.arange(len(labels))
    methods = [
        "greedy_auction",
        "distributed_best_cost",
        "centralised_greedy",
        "random",
    ]
    width = 0.18

    plt.figure(figsize=(10, 5))
    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]
    colors = {
        "greedy_auction": "#1f77b4",
        "distributed_best_cost": "#2ca02c",
        "centralised_greedy": "#ff7f0e",
        "random": "#7f7f7f",
    }

    for method, offset in zip(methods, offsets):
        plt.bar(
            x + offset,
            [summary[method][label] for label in labels],
            width=width,
            color=colors[method],
            label=BAR_LABEL_MAP[method],
        )

    plt.title("Average Mission Completion Time vs Task Type Allocation")
    plt.xlabel("Task Type Allocation (rescue:medicine:supplies:bandage)")
    plt.ylabel("Average Mission Completion Time")
    plt.xticks(x, labels)
    plt.grid(True, axis="y", linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=200)
    plt.close()

    return plot_path


def plot_task_map(tasks, output_dir: Path) -> Path:
    plot_path = output_dir / TASK_MAP_PLOT_FILE
    color_map = {
        "rescue": "#d73027",
        "medicine": "#4575b4",
        "supplies": "#1a9850",
        "bandage": "#fdae61",
    }
    label_map = {
        "rescue": "Rescue",
        "medicine": "Medicine",
        "supplies": "Supplies",
        "bandage": "Bandage",
    }

    plt.figure(figsize=(7, 7))
    for task_type in color_map:
        type_tasks = [task for task in tasks if task.task_type == task_type]
        plt.scatter(
            [task.x for task in type_tasks],
            [task.y for task in type_tasks],
            s=70,
            color=color_map[task_type],
            label=label_map[task_type],
        )

    plt.title("Standard Task Map in 20x20 Grid")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.xlim(-0.5, 19.5)
    plt.ylim(-0.5, 19.5)
    plt.xticks(range(0, 20, 2))
    plt.yticks(range(0, 20, 2))
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path, dpi=200)
    plt.close()

    return plot_path


def plot_uav_balance(
    per_uav_times: dict[str, int],
    per_uav_task_counts: dict[str, int],
    output_dir: Path,
) -> Path:
    plot_path = output_dir / UAV_BALANCE_PLOT_FILE
    labels = list(per_uav_times.keys())
    time_values = list(per_uav_times.values())
    task_count_values = [per_uav_task_counts[label] for label in labels]
    x = np.arange(len(labels))
    width = 0.36

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    bars_time = ax1.bar(x - width / 2, time_values, width=width, color="#4c78a8", label="Completion Time")
    bars_count = ax2.bar(x + width / 2, task_count_values, width=width, color="#f28e2b", label="Task Count")

    ax1.set_title("Per-UAV Balance for One Greedy + Auction Run")
    ax1.set_xlabel("UAV")
    ax1.set_ylabel("Completion Time")
    ax2.set_ylabel("Number of Assigned Tasks")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.grid(True, axis="y", linestyle="--", alpha=0.35)

    for bar, value in zip(bars_time, time_values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.5,
            str(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    for bar, value in zip(bars_count, task_count_values):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.05,
            str(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper right")

    fig.tight_layout()
    fig.savefig(plot_path, dpi=200)
    plt.close(fig)

    return plot_path


def plot_task_count_summary_10458(summary: dict[str, dict[str, float]], output_dir: Path) -> Path:
    return plot_summary_to_file(
        summary,
        output_dir,
        TASK_COUNT_PLOT_FILE_10458,
        "Average Mission Completion Time vs Number of Tasks (10458)",
        TASK_COUNT_VALUES,
        "Number of Tasks",
    )


def plot_task_count_summary_sametime(summary: dict[str, dict[str, float]], output_dir: Path) -> Path:
    return plot_summary_to_file(
        summary,
        output_dir,
        TASK_COUNT_PLOT_FILE_SAMETIME,
        "Average Mission Completion Time vs Number of Tasks (sametime)",
        TASK_COUNT_VALUES,
        "Number of Tasks",
    )


def plot_uav_summary_10458(summary: dict[str, dict[str, float]], output_dir: Path) -> Path:
    return plot_summary_to_file(
        summary,
        output_dir,
        UAV_COUNT_PLOT_FILE_10458,
        "Average Mission Completion Time vs Number of UAVs (10458)",
        UAV_COUNTS,
        "Number of UAVs",
    )


def plot_uav_summary_sametime(summary: dict[str, dict[str, float]], output_dir: Path) -> Path:
    return plot_summary_to_file(
        summary,
        output_dir,
        UAV_COUNT_PLOT_FILE_SAMETIME,
        "Average Mission Completion Time vs Number of UAVs (sametime)",
        UAV_COUNTS,
        "Number of UAVs",
    )
