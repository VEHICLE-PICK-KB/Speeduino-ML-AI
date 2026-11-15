# Speeduino Knock-Risk Analysis

An Applied Machine Learning project exploring engine operating conditions associated with elevated knock risk using Speeduino ECU logs from a turbocharged BMW M30 engine.

The project focuses on offline data: preparing log data, examining sensor data, and using machine-learning methods to appropriately describe operating conditions. It also documents the reasoning behind preprocessing and modelling choices.

## Research question(s)

Can machine learning model(s) identify engine operating conditions associated with elevated knock risk from standalone ECU's sensor data?
Is the prediction accurate and can it be trusted?

## Data and interpretation

Inputs include engine speed, manifold absolute pressure, intake-air temperature, coolant temperature, air–fuel ratio, and ignition advance. The available channels, units, and sampling characteristics will be recorded after inspecting the source logs.

These channels describe operating conditions; they do not provide confirmed knock measurements. Any domain-informed risk index must be described as a heuristic indicator, rather than a measured knock probability. Clusters describe similarities in the recorded data and require separate interpretation in terms of engine behavior.

## Planned workflow

1. Inspect the original MLG logs and the available CSV conversion/export workflow.
2. Check exported values, column names, units, timestamps, and session boundaries.
3. Handle missing or invalid readings while preserving the original logs.
4. Explore sensor value relations across operating conditions.
5. Select and scale features correctly so that different units do not cause errors in results (e.g 1 - > 2 vs. 5000 - > 7000)
6. Explore suitable methods such as PCA, K-Means, and Gaussian mixture models, and see which one is the most reliable.
7. Document the findings and limitations.

Any synthetic data will be identified separately, but may be included in real-data evaluation and comparison too.

## Repository layout

| Directory | Purpose |
| --- | --- |
| `data/raw/` | Original logs kept locally. |
| `data/processed/` | Converted and cleaned datasets kept locally. |
| `src/` | Data-preparation and analysis modules added as the project develops. |
| `notebooks/` | Exploratory analysis and explanations. |
| `reports/` | Selected figures and project findings prepared for publication. |

## Warning

All analysis runs on a computer, separate from the vehicle and ECU. The project does not control engine settings or provide real-time knock protection.
