from dataclasses import dataclass, field

from task import Task


@dataclass
class UAV:
    uav_id: int
    start_x: int
    start_y: int
    tasks: list[Task] = field(default_factory=list)

    @property
    def current_planning_position(self) -> tuple[int, int]:
        if not self.tasks:
            return (self.start_x, self.start_y)

        last_task = self.tasks[-1]
        return (last_task.x, last_task.y)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def reset_tasks(self) -> None:
        self.tasks.clear()

    def __repr__(self) -> str:
        return (
            f"UAV(id={self.uav_id}, start=({self.start_x}, {self.start_y}), "
            f"tasks={len(self.tasks)})"
        )
