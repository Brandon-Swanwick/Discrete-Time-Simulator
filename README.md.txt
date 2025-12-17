# Discrete Time CPU Simulator

A Python-based discrete-event simulator (DES) designed to model and compare various CPU scheduling algorithms. The simulator uses stochastic processes—specifically a Poisson arrival process and exponential service times—to evaluate how different scheduling logic impacts system performance.

## 🚀 Features

The simulator implements four core scheduling disciplines:

1.  **FCFS (First-Come, First-Served):** A non-preemptive algorithm where the CPU processes tasks in the exact order they arrive.
2.  **SRTF (Shortest Remaining Time First):** A preemptive algorithm that always selects the process with the smallest amount of time remaining. 
3.  **HRRN (Highest Response Ratio Next):** A non-preemptive strategy that calculates a response ratio to balance high-priority short tasks with older, waiting tasks to prevent starvation.
4.  **RR (Round Robin):** A preemptive algorithm that rotates through the ready queue, giving each process a fixed time slice (Quantum).



## 📊 Performance Metrics

The simulator runs until **10,000 processes** are completed, then calculates and saves the following data to `simData.txt`:

| Metric | Description |
| :--- | :--- |
| **Avg Turnaround Time** | Total time from process arrival to completion. |
| **Throughput** | Number of processes completed per unit of time. |
| **CPU Utilization** | The ratio of time the CPU was busy vs. total simulation time. |
| **Avg # Proc Ready Q** | The average number of processes waiting in the queue. |

## 🛠 Usage

### Execution
Run the simulator via the command line by passing the required parameters as arguments:

```bash
python3 simulator.py <scheduleType> <lambdaValue> <avgServiceTime> <quantumValue>