from config import MOVE_TIME, TASK_POSITION_SEED, TASKS_PER_TYPE
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


def run_smoke_test() -> None:
    fixed_tasks = generate_fixed_tasks(TASK_POSITION_SEED, TASKS_PER_TYPE)

    greedy_uavs = generate_uavs(3, 100)
    greedy_tasks = clone_tasks(fixed_tasks)
    allocate_tasks_greedy_auction(greedy_uavs, greedy_tasks, MOVE_TIME)
    assert sum(len(uav.tasks) for uav in greedy_uavs) == len(greedy_tasks)
    assert evaluate_mission_completion_time(greedy_uavs, MOVE_TIME) > 0

    distributed_uavs = generate_uavs(3, 110)
    distributed_tasks = clone_tasks(fixed_tasks)
    allocate_tasks_distributed_best_cost(distributed_uavs, distributed_tasks, seed=111, move_time=MOVE_TIME)
    assert sum(len(uav.tasks) for uav in distributed_uavs) == len(distributed_tasks)
    assert evaluate_mission_completion_time(distributed_uavs, MOVE_TIME) > 0

    centralised_uavs = generate_uavs(3, 120)
    centralised_tasks = clone_tasks(fixed_tasks)
    allocate_tasks_centralised_greedy(centralised_uavs, centralised_tasks, MOVE_TIME)
    assert sum(len(uav.tasks) for uav in centralised_uavs) == len(centralised_tasks)
    assert evaluate_mission_completion_time(centralised_uavs, MOVE_TIME) > 0

    random_uavs = generate_uavs(3, 200)
    random_tasks = clone_tasks(fixed_tasks)
    allocate_tasks_random(random_uavs, random_tasks, seed=300)
    assert sum(len(uav.tasks) for uav in random_uavs) == len(random_tasks)
    assert evaluate_mission_completion_time(random_uavs, MOVE_TIME) > 0

    custom_tasks = generate_tasks_from_counts(
        seed=123,
        task_type_counts={"rescue": 4, "medicine": 2, "supplies": 2, "bandage": 2},
    )
    assert len(custom_tasks) == 10

    custom_time_tasks = generate_tasks_from_counts(
        seed=124,
        task_type_counts={"rescue": 2, "medicine": 2, "supplies": 1, "bandage": 1},
        task_type_times={"rescue": 10, "medicine": 4, "supplies": 5, "bandage": 8},
    )
    assert custom_time_tasks[0].execution_time in {10, 4, 5, 8}

    print("Smoke test passed.")


if __name__ == "__main__":
    run_smoke_test()
