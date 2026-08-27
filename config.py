GRID_WIDTH = 20
GRID_HEIGHT = 20
MOVE_TIME = 1

TASK_TYPE_TIMES = {
    "rescue": 6,
    "medicine": 2,
    "supplies": 3,
    "bandage": 4,
}

ALT_TASK_TYPE_TIMES_10458 = {
    "rescue": 10,
    "medicine": 4,
    "supplies": 5,
    "bandage": 8,
}

ALT_TASK_TYPE_TIMES_SAMETIME = {
    "rescue": 5,
    "medicine": 5,
    "supplies": 5,
    "bandage": 5,
}

TASKS_PER_TYPE = 6
TOTAL_TASKS = len(TASK_TYPE_TIMES) * TASKS_PER_TYPE
UAV_COUNTS = [3, 6, 9, 12]
NUM_RUNS = 30

TASK_COUNT_UAV_FIXED = 5
TASK_COUNT_VALUES = [5, 10, 15, 20]
TASK_COUNT_RATIO = [2, 1, 1, 1]

TASK_MIX_TOTAL_TASKS = 20
TASK_MIX_UAV_FIXED = 5
TASK_MIX_CONFIGS = [
    ("1:2:8:9", [1, 2, 8, 9]),
    ("3:4:6:7", [3, 4, 6, 7]),
    ("5:5:5:5", [5, 5, 5, 5]),
    ("7:6:4:3", [7, 6, 4, 3]),
    ("9:8:2:1", [9, 8, 2, 1]),
]

TASK_POSITION_SEED = 20260711
UAV_START_SEED = 314159

OUTPUT_DIR = "outputs"
RESULT_CSV = "experiment_results.csv"
PLOT_FILE = "completion_time_vs_uavs.png"
TASK_COUNT_CSV = "task_count_results.csv"
TASK_MIX_CSV = "task_mix_results.csv"
TASK_COUNT_PLOT_FILE = "completion_time_vs_task_count.png"
TASK_MIX_PLOT_FILE = "completion_time_vs_task_mix.png"
TASK_MAP_PLOT_FILE = "task_map_standard_24_tasks.png"
UAV_BALANCE_PLOT_FILE = "uav_balance_greedy_auction.png"
TASK_COUNT_PLOT_FILE_10458 = "completion_time_vs_task_count_10458.png"
TASK_COUNT_PLOT_FILE_SAMETIME = "completion_time_vs_task_count_sametime.png"
UAV_COUNT_PLOT_FILE_10458 = "completion_time_vs_uavs_10458.png"
UAV_COUNT_PLOT_FILE_SAMETIME = "completion_time_vs_uavs_sametime.png"
