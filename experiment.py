from dataclasses import dataclass
from statistics import mean

from config import (
    ALT_TASK_TYPE_TIMES_10458,
    ALT_TASK_TYPE_TIMES_SAMETIME,
    MOVE_TIME,
    NUM_RUNS,
    TASK_COUNT_RATIO,
    TASK_COUNT_UAV_FIXED,
    TASK_COUNT_VALUES,
    TASK_MIX_CONFIGS,
    TASK_MIX_UAV_FIXED,
    TASK_POSITION_SEED,
    TASKS_PER_TYPE,
    UAV_COUNTS,
    UAV_START_SEED,
)
from algorithm import simulate_uav_total_time
from simulation import (
    allocate_tasks_centralised_greedy,
    allocate_tasks_distributed_best_cost,
    allocate_tasks_greedy_auction,
    allocate_tasks_random,
    clone_tasks,
    evaluate_mission_completion_time,
    generate_fixed_tasks,
    generate_tasks_from_counts,
    generate_uavs,
)


@dataclass(frozen=True)
class ExperimentRow:
    scenario: str
    method: str
    x_value: str
    run_index: int
    completion_time: float


LINE_METHODS = (
    "greedy_auction",
    "distributed_best_cost",
    "centralised_greedy",
    "random",
)

BAR_METHODS = (
    "greedy_auction",
    "distributed_best_cost",
    "centralised_greedy",
    "random",
)

TASK_TIME_VARIANTS = {
    "default": {"title_suffix": "", "task_type_times": None},
    "10458": {"title_suffix": "(10458)", "task_type_times": ALT_TASK_TYPE_TIMES_10458},
    "sametime": {"title_suffix": "(sametime)", "task_type_times": ALT_TASK_TYPE_TIMES_SAMETIME},
}


def run_single_method(
    method: str,
    num_uavs: int,
    run_index: int,
    fixed_tasks,
    seed_offset: int = 0,
):
    tasks = clone_tasks(fixed_tasks)
    uavs = generate_uavs(
        num_uavs,
        UAV_START_SEED + seed_offset + num_uavs * 1000 + run_index,
    )

    if method == "greedy_auction":
        allocate_tasks_greedy_auction(uavs, tasks, MOVE_TIME)
    elif method == "distributed_best_cost":
        allocate_tasks_distributed_best_cost(
            uavs,
            tasks,
            seed=UAV_START_SEED + 200000 + seed_offset + num_uavs * 1000 + run_index,
            move_time=MOVE_TIME,
        )
    elif method == "centralised_greedy":
        allocate_tasks_centralised_greedy(uavs, tasks, MOVE_TIME)
    elif method == "random":
        allocate_tasks_random(
            uavs,
            tasks,
            seed=UAV_START_SEED + 100000 + seed_offset + num_uavs * 1000 + run_index,
        )
    else:
        raise ValueError(f"Unknown method: {method}")

    completion_time = evaluate_mission_completion_time(uavs, MOVE_TIME)
    return completion_time


def counts_from_ratio(total_tasks: int, ratio: list[int]) -> dict[str, int]:
    task_types = ["rescue", "medicine", "supplies", "bandage"]
    unit = total_tasks // sum(ratio)
    return {
        task_type: ratio_value * unit
        for task_type, ratio_value in zip(task_types, ratio)
    }


def _sort_key(value: str):
    if value.isdigit():
        return (0, int(value))
    return (1, value)


def summarize_rows(rows: list[ExperimentRow]) -> dict[str, dict[str, float]]:
    methods = sorted({row.method for row in rows})
    summary: dict[str, dict[str, float]] = {method: {} for method in methods}

    for method in summary:
        x_values = sorted(
            {row.x_value for row in rows if row.method == method},
            key=_sort_key,
        )
        for x_value in x_values:
            values = [
                row.completion_time
                for row in rows
                if row.method == method and row.x_value == x_value
            ]
            summary[method][x_value] = mean(values)

    return summary


def run_standard_uav_experiments() -> tuple[list[ExperimentRow], dict[str, dict[str, float]], list]:
    fixed_tasks = generate_fixed_tasks(TASK_POSITION_SEED, TASKS_PER_TYPE)
    rows: list[ExperimentRow] = []

    for num_uavs in UAV_COUNTS:
        for run_index in range(NUM_RUNS):
            for method in LINE_METHODS:
                completion_time = run_single_method(
                    method,
                    num_uavs,
                    run_index,
                    fixed_tasks,
                    seed_offset=0,
                )
                rows.append(
                    ExperimentRow(
                        scenario="uav_count",
                        method=method,
                        x_value=str(num_uavs),
                        run_index=run_index,
                        completion_time=completion_time,
                    )
                )

    return rows, summarize_rows(rows), fixed_tasks


def run_standard_uav_experiments_for_task_times(
    variant_key: str,
    task_type_times: dict[str, int],
) -> tuple[list[ExperimentRow], dict[str, dict[str, float]], list]:
    fixed_tasks = generate_fixed_tasks(
        TASK_POSITION_SEED,
        TASKS_PER_TYPE,
        task_type_times=task_type_times,
    )
    rows: list[ExperimentRow] = []

    for num_uavs in UAV_COUNTS:
        for run_index in range(NUM_RUNS):
            for method in LINE_METHODS:
                completion_time = run_single_method(
                    method,
                    num_uavs,
                    run_index,
                    fixed_tasks,
                    seed_offset=30000 + len(variant_key) * 1000,
                )
                rows.append(
                    ExperimentRow(
                        scenario=f"uav_count_{variant_key}",
                        method=method,
                        x_value=str(num_uavs),
                        run_index=run_index,
                        completion_time=completion_time,
                    )
                )

    return rows, summarize_rows(rows), fixed_tasks


def run_task_count_experiments() -> tuple[list[ExperimentRow], dict[str, dict[str, float]]]:
    rows: list[ExperimentRow] = []

    for task_count in TASK_COUNT_VALUES:
        task_counts = counts_from_ratio(task_count, TASK_COUNT_RATIO)
        fixed_tasks = generate_tasks_from_counts(
            TASK_POSITION_SEED + task_count,
            task_counts,
        )
        for run_index in range(NUM_RUNS):
            for method in LINE_METHODS:
                completion_time = run_single_method(
                    method,
                    TASK_COUNT_UAV_FIXED,
                    run_index,
                    fixed_tasks,
                    seed_offset=10000 + task_count * 100,
                )
                rows.append(
                    ExperimentRow(
                        scenario="task_count",
                        method=method,
                        x_value=str(task_count),
                        run_index=run_index,
                        completion_time=completion_time,
                    )
                )

    return rows, summarize_rows(rows)


def run_task_count_experiments_for_task_times(
    variant_key: str,
    task_type_times: dict[str, int],
) -> tuple[list[ExperimentRow], dict[str, dict[str, float]]]:
    rows: list[ExperimentRow] = []

    for task_count in TASK_COUNT_VALUES:
        task_counts = counts_from_ratio(task_count, TASK_COUNT_RATIO)
        fixed_tasks = generate_tasks_from_counts(
            TASK_POSITION_SEED + task_count,
            task_counts,
            task_type_times=task_type_times,
        )
        for run_index in range(NUM_RUNS):
            for method in LINE_METHODS:
                completion_time = run_single_method(
                    method,
                    TASK_COUNT_UAV_FIXED,
                    run_index,
                    fixed_tasks,
                    seed_offset=40000 + len(variant_key) * 1000 + task_count * 100,
                )
                rows.append(
                    ExperimentRow(
                        scenario=f"task_count_{variant_key}",
                        method=method,
                        x_value=str(task_count),
                        run_index=run_index,
                        completion_time=completion_time,
                    )
                )

    return rows, summarize_rows(rows)


def run_task_mix_experiments() -> tuple[list[ExperimentRow], dict[str, dict[str, float]]]:
    rows: list[ExperimentRow] = []
    task_types = ["rescue", "medicine", "supplies", "bandage"]

    for index, (label, counts) in enumerate(TASK_MIX_CONFIGS):
        task_counts = {
            task_type: count for task_type, count in zip(task_types, counts)
        }
        fixed_tasks = generate_tasks_from_counts(
            TASK_POSITION_SEED + 50000 + index,
            task_counts,
        )
        for run_index in range(NUM_RUNS):
            for method in BAR_METHODS:
                completion_time = run_single_method(
                    method,
                    TASK_MIX_UAV_FIXED,
                    run_index,
                    fixed_tasks,
                    seed_offset=20000 + index * 1000,
                )
                rows.append(
                    ExperimentRow(
                        scenario="task_mix",
                        method=method,
                        x_value=label,
                        run_index=run_index,
                        completion_time=completion_time,
                    )
                )

    return rows, summarize_rows(rows)


def run_all_experiments():
    standard_rows, standard_summary, standard_tasks = run_standard_uav_experiments()
    task_count_rows, task_count_summary = run_task_count_experiments()
    task_mix_rows, task_mix_summary = run_task_mix_experiments()
    balance_data = run_uav_balance_experiment()
    uav_count_10458_rows, uav_count_10458_summary, _ = run_standard_uav_experiments_for_task_times(
        "10458",
        ALT_TASK_TYPE_TIMES_10458,
    )
    uav_count_sametime_rows, uav_count_sametime_summary, _ = run_standard_uav_experiments_for_task_times(
        "sametime",
        ALT_TASK_TYPE_TIMES_SAMETIME,
    )
    task_count_10458_rows, task_count_10458_summary = run_task_count_experiments_for_task_times(
        "10458",
        ALT_TASK_TYPE_TIMES_10458,
    )
    task_count_sametime_rows, task_count_sametime_summary = run_task_count_experiments_for_task_times(
        "sametime",
        ALT_TASK_TYPE_TIMES_SAMETIME,
    )

    return {
        "uav_count": {
            "rows": standard_rows,
            "summary": standard_summary,
            "tasks": standard_tasks,
        },
        "task_count": {
            "rows": task_count_rows,
            "summary": task_count_summary,
        },
        "task_mix": {
            "rows": task_mix_rows,
            "summary": task_mix_summary,
        },
        "uav_count_10458": {
            "rows": uav_count_10458_rows,
            "summary": uav_count_10458_summary,
        },
        "uav_count_sametime": {
            "rows": uav_count_sametime_rows,
            "summary": uav_count_sametime_summary,
        },
        "task_count_10458": {
            "rows": task_count_10458_rows,
            "summary": task_count_10458_summary,
        },
        "task_count_sametime": {
            "rows": task_count_sametime_rows,
            "summary": task_count_sametime_summary,
        },
        "uav_balance": balance_data,
    }


def run_uav_balance_experiment() -> dict[str, object]:
    fixed_tasks = generate_fixed_tasks(TASK_POSITION_SEED, TASKS_PER_TYPE)
    uavs = generate_uavs(5, UAV_START_SEED + 900000)
    allocate_tasks_greedy_auction(uavs, clone_tasks(fixed_tasks), MOVE_TIME)

    per_uav_times = {
        f"UAV {uav.uav_id}": simulate_uav_total_time(uav, MOVE_TIME)
        for uav in uavs
    }
    per_uav_task_counts = {
        f"UAV {uav.uav_id}": len(uav.tasks)
        for uav in uavs
    }

    return {
        "num_uavs": 5,
        "tasks": fixed_tasks,
        "per_uav_times": per_uav_times,
        "per_uav_task_counts": per_uav_task_counts,
    }
