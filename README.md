# Reducing Size Bias in Sampling for Infectious Disease Spread on Networks

This repository implements a set of tools for simulating and analyzing the spread of epidemics on various network topologies. The goal is to explore the dynamics of infectious diseases using network-based models, including the estimation of disease metrics and network structure analysis.

## Features

- Simulation of epidemic spread using the **Susceptible-Infected-Recovered (SIR)** model.
- Comparison of different sampling algorithms (**Random Walk (RW)** and **Metropolis-Hastings Random Walk (MHRW)**) for disease metric estimation.
- Disease metrics such as the number of infected individuals, effective reproduction number, time to infection, and secondary infections.
- Exploration of different network types: **Erdős–Rényi (ER)**, **Small-World (SW)**, and **Scale-Free (SF)** networks.
- Application of algorithms to a **cattle movement network** as a real-world case study.

## Installation

Clone the repository:

```bash
git clone https://github.com/nehabansal26/Epidemics-on-Networks.git

Navigate to the repository folder:

```bash
cd Epidemics-on-Networks

Ensure you have the necessary Python dependencies. Install them using pip:

```bash
pip install -r requirements.txt

## Usage

The repository provides several scripts for different tasks related to epidemic modeling. Below are the steps for using the scripts.

### Step 1: Sample Generation
This step generates random samples from a network based on the given parameters.
```bash
python3 sample_generation.py <network> <start> <end> <sample_size> <walks> <net_dir> <sample_dir>

- network: The type of the network (e.g., bcms).
- start: The start time for the simulation.
- end: The end time for the simulation.
- sample_size: The number of samples to generate.
- walks: The number of walks per sample.
- net_dir: Directory where the network data is stored.
- sample_dir: Directory where the generated samples will be saved.

### Step 2: SIR Simulation
This step runs the SIR model simulation on the network and generates the disease spread data.
```bash
python3 SIR_simulation.py <network> <start> <end> <gamma> <net_dir> <sir_dir>

- gamma: Recovery rate for the SIR model.
-sir_dir: Directory where the simulation results will be stored.

### Step 3: Disease Metric Estimation
This step estimates disease metrics based on the simulation results.
```basg
python3 disease_metric_estimation.py <network> <start> <end> <gamma> <dup> <sir_dir> <net_dir> <sample_dir> <agg_results>

- dup: Flag indicating whether duplicate nodes are allowed in the sample.
- sir_dir: Directory containing the simulation results.
- agg_results: Directory for storing the aggregated results.

### Step 4: Degree Distribution
This step generates degree distribution statistics for the network.
```bash
python3 degree_distribution.py <network> <start> <end> <net_dir> <sample_dir> <agg_results>

- agg_results: Directory containing the aggregated results.

## Example Workflow
Here’s an example workflow for running all steps sequentially:
**Step 1:** Generate samples
python3 sample_generation.py bcms 0 100 10 2 networks samples

**Step 2:** Run SIR simulation
python3 SIR_simulation.py bcms 0 100 0.5 networks sir_results

**Step 3:** Estimate disease metrics
python3 disease_metric_estimation.py bcms 0 100 0.5 False sir_results networks samples aggregated_results

**Step 4:** Calculate degree distribution
python3 degree_distribution.py bcms 0 100 networks samples aggregated_results

## Network Types

This project supports different network topologies, each with unique characteristics:

1. Erdős–Rényi (ER) Network: Randomly generated network with a fixed probability of edge formation between nodes.
2. Small-World (SW) Network: A network with high clustering and short path lengths, resembling real-world social networks.
3. Scale-Free (SF) Network: A network where the degree distribution follows a power law, with a few nodes (hubs) having high degrees.

## Results and Insights

The results are used to explore the effectiveness of the two sampling algorithms (RW and MHRW) in estimating disease metrics like:

- Proportion of infected individuals
- Average number of secondary infections
- Time-to-infection
The study provides insights into how network structure impacts disease spread and how sampling methods can influence epidemic predictions.
