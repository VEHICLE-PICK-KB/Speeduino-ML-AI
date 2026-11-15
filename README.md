# Speeduino Knock-Risk Analysis

An Applied Machine Learning project exploring engine operating conditions associated with elevated knock risk using Speeduino ECU logs from a turbocharged BMW M30 engine.

The project focuses on offline data analysis: preparing log data, examining sensor relationships, and using machine-learning methods to describe operating conditions. It also documents the reasoning behind preprocessing and modelling choices.

## Research question

Can machine learning identify engine operating conditions associated with elevated knock risk from ECU sensor data?

## Data and interpretation

Candidate inputs include engine speed, manifold absolute pressure, intake-air temperature, coolant temperature, air–fuel ratio, and ignition advance. The available channels, units, and sampling characteristics will be recorded after inspecting the source logs.

These channels describe operating conditions; they do not provide confirmed knock measurements. Any domain-informed risk index must be described as a heuristic indicator, rather than a measured knock probability. Clusters describe similarities in the recorded data and require separate interpretation in terms of engine behavior.

## Planned workflow

1. Inspect the original MLG logs and the available CSV conversion/export workflow.
2. Check exported values, column names, units, timestamps, and session boundaries.
3. Handle missing or invalid readings, duplicate records, and discontinuities while preserving the original logs.
4. Explore sensor distributions and relationships across operating conditions.
5. Select and scale features using the Applied Machine Learning course materials.
6. Explore suitable methods such as PCA, K-Means, and Gaussian mixture models, and explain their results using domain knowledge.
7. Document the findings, assumptions, and limitations in a reproducible analysis.

Method selection and implementation will follow the course materials and the characteristics of the available data. Where held-out evaluation is used, sessions/logs will be separated before fitting preprocessing or models, to reduce leakage between adjacent samples. Any synthetic data will be identified separately and excluded from real-data evaluation.

## Repository layout

| Directory | Purpose |
| --- | --- |
| `data/raw/` | Original logs kept locally. |
| `data/processed/` | Converted and cleaned datasets kept locally. |
| `src/` | Data-preparation and analysis modules added as the project develops. |
| `notebooks/` | Exploratory analysis and explanations. |
| `reports/` | Selected figures and project findings prepared for publication. |

This initial repository establishes the project scope and directory structure. The first implementation task is log conversion/export inspection and data cleaning. Runtime dependencies and execution instructions will be added with that implementation.

## Public repository contents

The public repository is intended for source code, analysis explanations, and selected results. Raw and processed logs, ECU calibration files, local environments, credentials, and course handouts are excluded by `.gitignore`. Selected outputs should be checked before publication for identifying details in file paths, timestamps, or metadata.

All analysis runs on a computer, separate from the vehicle and ECU. The project does not control engine settings or provide real-time knock protection.
