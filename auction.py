from algorithm import loss_if_best_is_removed, rank_tasks
from task import Task
from uav import UAV


def choose_winner(
    contenders: list[UAV],
    available_tasks: list[Task],
    move_time: int,
) -> tuple[UAV, Task]:
    ranked_options = {
        uav.uav_id: rank_tasks(uav.current_planning_position, available_tasks, move_time)
        for uav in contenders
    }

    winner = max(
        contenders,
        key=lambda uav: (
            loss_if_best_is_removed(ranked_options[uav.uav_id]),
            -ranked_options[uav.uav_id][0].cost,
            -uav.uav_id,
        ),
    )
    winning_task = ranked_options[winner.uav_id][0].task
    return winner, winning_task
