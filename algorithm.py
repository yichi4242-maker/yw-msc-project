from dataclasses import dataclass
from math import inf

from task import Task
from uav import UAV


@dataclass(frozen=True)
class RankedTask:
    task: Task
    cost: int


def manhattan_distance(start: tuple[int, int], end: tuple[int, int]) -> int:
    return abs(start[0] - end[0]) + abs(start[1] - end[1])


def calculate_cost(position: tuple[int, int], task: Task, move_time: int) -> int:
    distance = manhattan_distance(position, (task.x, task.y))
    return distance * move_time + task.execution_time


def rank_tasks(position: tuple[int, int], tasks: list[Task], move_time: int) -> list[RankedTask]:
    ranking = [
        RankedTask(task=task, cost=calculate_cost(position, task, move_time))
        for task in tasks
    ]
    ranking.sort(key=lambda item: (item.cost, item.task.task_id))
    return ranking


def get_best_task(ranking: list[RankedTask]) -> RankedTask | None:
    return ranking[0] if ranking else None


def get_second_best_task(ranking: list[RankedTask]) -> RankedTask | None:
    return ranking[1] if len(ranking) >= 2 else None


def loss_if_best_is_removed(ranking: list[RankedTask]) -> float:
    best = get_best_task(ranking)
    second_best = get_second_best_task(ranking)

    if best is None:
        return -inf

    if second_best is None:
        return inf

    return second_best.cost - best.cost


def simulate_uav_total_time(uav: UAV, move_time: int) -> int:
    total_time = 0
    current_position = (uav.start_x, uav.start_y)

    for task in uav.tasks:
        total_time += calculate_cost(current_position, task, move_time)
        current_position = (task.x, task.y)

    return total_time
