from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    task_id: int
    task_type: str
    x: int
    y: int
    execution_time: int

    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id}, type='{self.task_type}', "
            f"pos=({self.x}, {self.y}), time={self.execution_time})"
        )
