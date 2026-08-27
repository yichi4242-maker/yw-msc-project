# Multi-UAV Task Allocation for Post-Disaster Emergency Scenarios

## Project Overview
This project studies task allocation in a multi-UAV system for post-disaster emergency scenarios. A 2D grid-based simulation environment is developed to model different rescue tasks distributed across the disaster area.

The main objective of this project is to minimise the overall mission completion time by assigning tasks to multiple UAVs efficiently.

## Implemented Methods
The project includes the following task allocation methods:

- Proposed Greedy + Auction method
- Distributed Best-Cost method
- Centralised Greedy method
- Random Baseline method

## Simulation Setting
- Environment: 20 × 20 grid
- Task types:
  - Rescue
  - Medicine delivery
  - Supply delivery
  - Simple bandaging
- Standard task setting:
  - 24 tasks in total
  - 6 tasks for each task type
- UAV numbers tested:
  - 3, 6, 9, 12
  - Additional experiments with 5 UAVs
- Evaluation metric:
  - Total mission completion time
- Experimental results:
  - Averaged over 30 simulation runs

## Project Structure
- `main.py`: main program entry
- `test.py`: testing script
- `output/`: generated figures and experiment results
- Other Python files: task generation, UAV modelling, allocation algorithms, simulation, and visualisation modules

## How to Run
1. Open the project folder in Python or VS Code.
2. Make sure the required Python environment and libraries are installed.
3. Run the main file:

```bash
python main.py