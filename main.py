from pathlib import Path

from config import RESULT_CSV, TASK_COUNT_CSV, TASK_MIX_CSV
from experiment import run_all_experiments
from visualization import (
    ensure_output_dir,
    plot_summary,
    plot_task_count_summary,
    plot_task_count_summary_10458,
    plot_task_count_summary_sametime,
    plot_task_map,
    plot_task_mix_summary,
    plot_uav_summary_10458,
    plot_uav_summary_sametime,
    plot_uav_balance,
    save_results_csv,
)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    output_dir = ensure_output_dir(base_dir)

    experiment_data = run_all_experiments()

    uav_count_csv = save_results_csv(
        experiment_data["uav_count"]["rows"],
        output_dir,
        RESULT_CSV,
    )
    task_count_csv = save_results_csv(
        experiment_data["task_count"]["rows"],
        output_dir,
        TASK_COUNT_CSV,
    )
    task_mix_csv = save_results_csv(
        experiment_data["task_mix"]["rows"],
        output_dir,
        TASK_MIX_CSV,
    )

    uav_plot_path = plot_summary(experiment_data["uav_count"]["summary"], output_dir)
    task_count_plot_path = plot_task_count_summary(
        experiment_data["task_count"]["summary"],
        output_dir,
    )
    task_count_plot_path_10458 = plot_task_count_summary_10458(
        experiment_data["task_count_10458"]["summary"],
        output_dir,
    )
    task_count_plot_path_sametime = plot_task_count_summary_sametime(
        experiment_data["task_count_sametime"]["summary"],
        output_dir,
    )
    task_mix_plot_path = plot_task_mix_summary(
        experiment_data["task_mix"]["summary"],
        output_dir,
    )
    uav_plot_path_10458 = plot_uav_summary_10458(
        experiment_data["uav_count_10458"]["summary"],
        output_dir,
    )
    uav_plot_path_sametime = plot_uav_summary_sametime(
        experiment_data["uav_count_sametime"]["summary"],
        output_dir,
    )
    task_map_plot_path = plot_task_map(
        experiment_data["uav_count"]["tasks"],
        output_dir,
    )
    uav_balance_plot_path = plot_uav_balance(
        experiment_data["uav_balance"]["per_uav_times"],
        experiment_data["uav_balance"]["per_uav_task_counts"],
        output_dir,
    )

    print("Experiment summary")
    for scenario_name, payload in experiment_data.items():
        print(f"\n{scenario_name}")
        if "summary" in payload:
            for method, values in payload["summary"].items():
                print(f"  {method}")
                for x_value, avg_time in values.items():
                    print(f"    {x_value}: average completion time = {avg_time:.2f}")
        else:
            for uav_label, completion_time in payload["per_uav_times"].items():
                print(f"  {uav_label}: completion time = {completion_time}")

    print(f"\nSaved CSV: {uav_count_csv}")
    print(f"Saved CSV: {task_count_csv}")
    print(f"Saved CSV: {task_mix_csv}")
    print(f"Saved plot: {uav_plot_path}")
    print(f"Saved plot: {task_count_plot_path}")
    print(f"Saved plot: {task_count_plot_path_10458}")
    print(f"Saved plot: {task_count_plot_path_sametime}")
    print(f"Saved plot: {task_mix_plot_path}")
    print(f"Saved plot: {uav_plot_path_10458}")
    print(f"Saved plot: {uav_plot_path_sametime}")
    print(f"Saved plot: {task_map_plot_path}")
    print(f"Saved plot: {uav_balance_plot_path}")


if __name__ == "__main__":
    main()
