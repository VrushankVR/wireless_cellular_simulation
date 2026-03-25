# Wireless Cellular Simulation

This project simulates the behavior of a single-cell wireless communication system, specifically focusing on downlink transmission from a Base Station (BS) to multiple randomly distributed Mobile Stations (MSs).

The primary goal of this simulation is to compute the probability of call blocking and call dropping across various system loads, comparing a baseline system (10 Watts transmit power) against an improved system (40 Watts transmit power).

## Key Features

- **Okumura-Hata Path Loss Model**: Calculates large-scale path loss based on rural/urban environments.
- **Log-normal Shadowing**: Models signal power variation due to obstacles.
- **Rayleigh Fading**: Independently generated complex Gaussian variations tracking fast fluctuations and rapid signal dropping.
- **Erlang-B Bottlenecks**: Evaluates user load scaling across the 50 channel constraint to observe genuine capacity-driven blocked calls.

## Output and GOS Analysis

The system iteratively calculates and models up to 1800 simultaneous users logging on to the cellular service to observe when the Grade of Service (GOS) drops below mathematically acceptable thresholds.

- **Baseline System (10W)**: The cell's coverage limits fail to satisfy a 2% blocking target natively.
- **Improved System (40W)**: Power increases overcome signal degradation gaps and serve approximately ~1200 concurrent users before channel capacity triggers the 2% blocking threshold.

Visual plots mapping the Grade of Service over simulated mobile station scaling are included:
- `user_placement.png`
- `blocking_probability.png`
- `dropping_probability.png`

## How to Run

Requirements:
- Python 3
- numpy
- matplotlib

Run the simulation:
```bash
python "656 project.py"
```

The script will compile the stochastic results and regenerate the graphical plots reflecting channel performance.
