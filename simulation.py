import random
from collections import defaultdict

from algorithm import rank_tasks, simulate_uav_total_time
from auction import choose_winner
from config import GRID_HEIGHT, GRID_WIDTH, MOVE_TIME, TASK_TYPE_TIMES
from task import Task
from uav import UAV


def generate_fixed_tasks(
    seed: int,
    tasks_per_type: int,
    task_type_times: dict[str, int] = TASK_TYPE_TIMES,
) -> list[Task]:
    rng = random.Random(seed)
    used_positions: set[tuple[int, int]] = set()
    tasks: list[Task] = []
    task_id = 1

    for task_type, execution_time in task_type_times.items():
        for _ in range(tasks_per_type):
            while True:
                position = (rng.randrange(GRID_WIDTH), rng.randrange(GRID_HEIGHT))
                if position not in used_positions:
                    used_positions.add(position)
                    break

            tasks.append(
                Task(
                    task_id=task_id,
                    task_type=task_type,
                    x=position[0],
                    y=position[1],
                    execution_time=execution_time,
                )
            )
            task_id += 1

    return tasks


def generate_tasks_from_counts(
    seed: int,
    task_type_counts: dict[str, int],
    task_type_times: dict[str, int] = TASK_TYPE_TIMES,
) -> list[Task]:
    rng = random.Random(seed)
    used_positions: set[tuple[int, int]] = set()
    tasks: list[Task] = []
    task_id = 1

    for task_type, count in task_type_counts.items():
        execution_time = task_type_times[task_type]
        for _ in range(count):
            while True:
                position = (rng.randrange(GRID_WIDTH), rng.randrange(GRID_HEIGHT))
                if position not in used_positions:
                    used_positions.add(position)
                    break

            tasks.append(
                Task(
                    task_id=task_id,
                    task_type=task_type,
                    x=position[0],
                    y=position[1],
                    execution_time=execution_time,
                )
            )
            task_id += 1

    return tasks


def generate_uavs(num_uavs: int, seed: int) -> list[UAV]:
    rng = random.Random(seed)
    used_positions: set[tuple[int, int]] = set()
    uavs: list[UAV] = []

    while len(uavs) < num_uavs:
        position = (rng.randrange(GRID_WIDTH), rng.randrange(GRID_HEIGHT))
        if position in used_positions:
            continue

        used_positions.add(position)
        uavs.append(
            UAV(
                uav_id=len(uavs) + 1,
                start_x=position[0],
                start_y=position[1],
            )
        )

    return uavs


def clone_tasks(tasks: list[Task]) -> list[Task]:
    return [Task(task.task_id, task.task_type, task.x, task.y, task.execution_time) for task in tasks]


def allocate_tasks_greedy_auction(uavs: list[UAV], tasks: list[Task], move_time: int = MOVE_TIME) -> list[UAV]:
    remaining_tasks = sorted(tasks, key=lambda task: task.task_id)

    while remaining_tasks:
        round_unassigned = [uav for uav in uavs]

        while round_unassigned and remaining_tasks:
            proposals: dict[int, list[UAV]] = defaultdict(list)
            rankings_by_uav: dict[int, list] = {}

            for uav in round_unassigned:
                ranking = rank_tasks(uav.current_planning_position, remaining_tasks, move_time)
                if ranking:
                    rankings_by_uav[uav.uav_id] = ranking
                    proposals[ranking[0].task.task_id].append(uav)

            if not proposals:
                break

            matched_uav_ids: set[int] = set()
            matched_task_ids: set[int] = set()

            for task_id, candidates in proposals.items():
                if len(candidates) != 1:
                    continue

                winner = candidates[0]
                task = rankings_by_uav[winner.uav_id][0].task
                winner.add_task(task)
                matched_uav_ids.add(winner.uav_id)
                matched_task_ids.add(task.task_id)

            contested_groups = [
                candidates for candidates in proposals.values() if len(candidates) > 1
            ]
            contested_groups.sort(key=lambda group: group[0].uav_id)

            for candidates in contested_groups:
                available_for_contest = [
                    task for task in remaining_tasks if task.task_id not in matched_task_ids
                ]
                if not available_for_contest:
                    break

                winner, winning_task = choose_winner(candidates, available_for_contest, move_time)
                winner.add_task(winning_task)
                matched_uav_ids.add(winner.uav_id)
                matched_task_ids.add(winning_task.task_id)

            if not matched_task_ids:
                # Safety fallback for rare pathological ties.
                fallback_uav = min(round_unassigned, key=lambda uav: uav.uav_id)
                fallback_task = rank_tasks(
                    fallback_uav.current_planning_position,
                    remaining_tasks,
                    move_time,
                )[0].task
                fallback_uav.add_task(fallback_task)
                matched_uav_ids.add(fallback_uav.uav_id)
                matched_task_ids.add(fallback_task.task_id)

            remaining_tasks = [
                task for task in remaining_tasks if task.task_id not in matched_task_ids
            ]
            round_unassigned = [
                uav for uav in round_unassigned if uav.uav_id not in matched_uav_ids
            ]

    return uavs


def allocate_tasks_distributed_best_cost(
    uavs: list[UAV],
    tasks: list[Task],
    seed: int,
    move_time: int = MOVE_TIME,
) -> list[UAV]:
    rng = random.Random(seed)
    remaining_tasks = sorted(tasks, key=lambda task: task.task_id)

    while remaining_tasks:
        round_unassigned = [uav for uav in uavs]

        while round_unassigned and remaining_tasks:
            proposals: dict[int, list[UAV]] = defaultdict(list)
            rankings_by_uav: dict[int, list] = {}

            for uav in round_unassigned:
                ranking = rank_tasks(uav.current_planning_position, remaining_tasks, move_time)
                if ranking:
                    rankings_by_uav[uav.uav_id] = ranking
                    proposals[ranking[0].task.task_id].append(uav)

            if not proposals:
                break

            matched_uav_ids: set[int] = set()
            matched_task_ids: set[int] = set()
            skipped_uav_ids: set[int] = set()

            for candidates in proposals.values():
                if len(candidates) == 1:
                    winner = candidates[0]
                    task = rankings_by_uav[winner.uav_id][0].task
                    winner.add_task(task)
                    matched_uav_ids.add(winner.uav_id)
                    matched_task_ids.add(task.task_id)

            contested_groups = [candidates for candidates in proposals.values() if len(candidates) > 1]
            contested_groups.sort(key=lambda group: group[0].uav_id)

            for candidates in contested_groups:
                available_for_contest = [
                    task for task in remaining_tasks if task.task_id not in matched_task_ids
                ]
                if not available_for_contest:
                    break

                ranked_candidates = []
                for uav in candidates:
                    ranking = rank_tasks(uav.current_planning_position, available_for_contest, move_time)
                    if ranking:
                        ranked_candidates.append((uav, ranking[0].cost, ranking[0].task))

                if not ranked_candidates:
                    continue

                best_cost = min(item[1] for item in ranked_candidates)
                best_group = [item for item in ranked_candidates if item[1] == best_cost]
                winner_uav, _, winning_task = rng.choice(best_group)
                winner_uav.add_task(winning_task)
                matched_uav_ids.add(winner_uav.uav_id)
                matched_task_ids.add(winning_task.task_id)
                skipped_uav_ids.update(
                    uav.uav_id for uav in candidates if uav.uav_id != winner_uav.uav_id
                )

            if not matched_task_ids:
                fallback_uav = min(round_unassigned, key=lambda uav: uav.uav_id)
                fallback_task = rank_tasks(
                    fallback_uav.current_planning_position,
                    remaining_tasks,
                    move_time,
                )[0].task
                fallback_uav.add_task(fallback_task)
                matched_uav_ids.add(fallback_uav.uav_id)
                matched_task_ids.add(fallback_task.task_id)

            remaining_tasks = [
                task for task in remaining_tasks if task.task_id not in matched_task_ids
            ]
            round_unassigned = [
                uav
                for uav in round_unassigned
                if uav.uav_id not in matched_uav_ids and uav.uav_id not in skipped_uav_ids
            ]

    return uavs


def allocate_tasks_centralised_greedy(
    uavs: list[UAV],
    tasks: list[Task],
    move_time: int = MOVE_TIME,
) -> list[UAV]:
    remaining_tasks = sorted(tasks, key=lambda task: task.task_id)

    while remaining_tasks:
        best_uav = None
        best_task = None
        best_cost = None

        for uav in uavs:
            ranking = rank_tasks(uav.current_planning_position, remaining_tasks, move_time)
            if not ranking:
                continue

            candidate = ranking[0]
            if (
                best_cost is None
                or candidate.cost < best_cost
                or (candidate.cost == best_cost and candidate.task.task_id < best_task.task_id)
                or (
                    candidate.cost == best_cost
                    and candidate.task.task_id == best_task.task_id
                    and uav.uav_id < best_uav.uav_id
                )
            ):
                best_uav = uav
                best_task = candidate.task
                best_cost = candidate.cost

        if best_uav is None or best_task is None:
            break

        best_uav.add_task(best_task)
        remaining_tasks = [task for task in remaining_tasks if task.task_id != best_task.task_id]

    return uavs


def allocate_tasks_random(uavs: list[UAV], tasks: list[Task], seed: int) -> list[UAV]:
    rng = random.Random(seed)
    shuffled_tasks = list(tasks)
    rng.shuffle(shuffled_tasks)

    for index, task in enumerate(shuffled_tasks):
        uavs[index % len(uavs)].add_task(task)

    return uavs


def evaluate_mission_completion_time(uavs: list[UAV], move_time: int = MOVE_TIME) -> int:
    completion_times = [simulate_uav_total_time(uav, move_time) for uav in uavs]
    return max(completion_times, default=0)
