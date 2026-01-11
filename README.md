# Geometric Null Models for Prime Distributions

This repository accompanies the manuscript:

**Residual Spatial Correlations in Geometric Embeddings of Prime Numbers**  
Manuscript in preparation (2026)

---

## Overview

This project investigates the spatial organization of prime numbers through a continuous geometric embedding of the natural numbers into a logarithmic spiral in the plane. Within this embedding, local prime densities are defined using Euclidean neighborhoods, enabling a systematic analysis of local structure across multiple spatial scales.

To assess whether observed local patterns can be explained solely by geometric effects and by the average rarefaction of primes, we introduce a geometric null model inspired by Cramér’s probabilistic model. In this null configuration, the embedding geometry and the global event intensity are preserved, while arithmetic correlations are removed via independent Bernoulli sampling.

By comparing the empirical distributions of local density for the real prime configuration and the null model using non-parametric statistical tests, we detect residual spatial correlations that persist beyond geometric and mean-density effects, particularly at intermediate (mesoscopic) spatial scales.

---

## Scientific goals

- Embed natural numbers and primes in a continuous geometric space
- Define and measure local prime density using spatial neighborhoods
- Construct a calibrated geometric null model of Cramér type
- Compare real and null configurations using distribution-level statistics
- Identify scale-dependent residual spatial correlations
- Test robustness under changes of spatial scale and domain size
---

## Repository structure

```
geometric-null-model-primes/
│
├── README.md
├── LICENSE
├── LICENSEdoc
├── CITATION.cff
│
├── data/
│   ├── E1_base_log_espiral_1M.csv
│   ├── null_on_real_embedding.csv
│   └── radius_sweep_real_embedding.csv
│
├── scripts/
│   ├── generate_embedding.py
│   ├── generate_null_on_real_embedding.py
│   ├── compare_density_on_sampled_points_realembed.py
│   ├── sweep_radius_density_real_embedding.py
│   └── utils/
│       ├── primality.py
│       ├── geometry.py
│       └── sampling.py
│
├── figures/
│   ├── fig_real_vs_null_embedding_side_by_side.png
│   ├── fig_cdf_real_vs_null_R10.png
│   ├── fig_cdf_real_vs_null_R10_KS_zoom.png
│   ├── fig_ks_vs_radius_real_embedding.png
│   └── KS_vs_N_caps.png
│
└── requirements.txt
```

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/tacigomess/geometric-null-model-primes.git
cd geometric-null-model-primes
pip install -r requirements.txt
```

Python ≥ 3.9 is recommended.

---
## Experimental Pipeline and Interpretation

The project is organized as a sequence of numbered experiments (E1–E4), followed by a supplementary robustness analysis.
Each experiment produces well-defined outputs that serve as inputs for subsequent stages.

Together, these experiments allow a controlled investigation of local spatial structure in the geometric distribution of prime numbers.

### First of all: E1 — Generation of the geometric embedding (base dataset)

### E1 — Objective
To construct a continuous geometric embedding of the natural numbers into a logarithmic spiral and to identify the real prime numbers within the analyzed interval. 
This experiment defines the fixed geometric space used throughout the project.


```bash
python E1_generate_log_spiral_dataset_min.py \
  --N 1000000 \
  --b 0.1 \
  --radius_mode adaptive \
  --z_factor 0.1 \
  --block_size 50000 \
  --percentile 95 \
  --out_csv data/E1_base_log_espiral_1M.csv
```

### E1 — Output
`data/E1_base_log_espiral_1M.csv`

-The output directory (/data) is created by the script if it does not exist.

### Typical columns include:

n — natural number

x, y — geometric coordinates

is_prime — arithmetic label (1 if prime, 0 otherwise)

### E1 — Interpretation
This experiment fixes the geometry of the problem. Primes and composite numbers share the same embedding. No statistical hypothesis is tested at this stage; the output simply defines the spatial domain in which all subsequent analyses are performed.

E1 — Notes

-This dataset is intentionally comprehensive. In addition to the features required for the present work, it also includes auxiliary features originally developed for a previous project on prime density halos. These additional features are not used in the current analysis.

-The same base dataset is reused across subsequent projects, ensuring consistency of the geometric embedding and facilitating comparative studies.

---

### E2 — Construction of the geometric null model (Cramér-type)

### E2 — Objective
To generate a statistically controlled null configuration that preserves geometry and global intensity while removing arithmetic correlations among primes.

### E2 — Script
```bash
python generate_null_on_real_embedding.py
```

### E2 — Input

Base dataset generated in E1 : `data/E1_base_log_espiral_1M.csv`

### E2 — Probability model

The null model assigns an independent random event to each embedded point according to a Cramér-type probability law:

```text
p(n) = c / log(n)
```
where:

- n denotes the natural number associated with each geometric point,

- log(n) reflects the asymptotic rarefaction of prime numbers,

- c is a normalization constant chosen so that the expected total number of null events matches the observed number of real primes up to the cutoff N.

```text
c = (number of real primes) / sum(1 / log(n))
```

This calibration ensures that the null model reproduces:

- the correct global intensity,

- the large-scale density decay of primes,

while removing all higher-order arithmetic correlations through independent Bernoulli sampling.


### E2 — Output
`data/null_on_real_embedding.csv`

- Typical terminal output:
```bash
Real primes: 78498 | Null events: 78207 | c = 0.9983
```

### E2 — Interpretation

The null model:

- uses exactly the same geometric coordinates as the real data,

- matches the total number of events,

- reproduces the large-scale rarefaction of primes,

- removes all arithmetic correlations via independent Bernoulli sampling.

- This experiment defines the main null hypothesis of the study.

---

### E3 - Compare local densities (reference scale)

Objective

To test whether the empirical distributions of local prime density in the real configuration and in the null model are statistically compatible at a fixed spatial scale.

This experiment answers a single question:

- Are the real and null local density distributions statistically compatible?

```bash
python scripts/compare_density_on_sampled_points_realembed.py
```

Procedure:
- Uniformly sample spatial centers from the full geometric embedding

- Compute local densities for real and null configurations using KDTree radius queries

- Compare the full empirical distributions using the Kolmogorov–Smirnov test

### E3 — Output

- Typical terminal output:
  
```bash
==== Density on sampled points (same geometry) ====
Mean density (real): 19971.474
Mean density (null): 19901.518

KS test:
KS statistic = 0.0717
p-value      = 3.31e-112
```

Interpretation

Although the mean local densities coincide by construction, the Kolmogorov–Smirnov test compares the entire empirical distributions, not only their averages.
The extremely small p-value indicates that the observed difference is not due to random fluctuations.

In other words, the real and null configurations share the same global intensity, but differ in how local densities are distributed across space. This reflects subtle but systematic spatial organization beyond what is captured by an independent-event model.

### E3 - part 2 - Visualizing

- Generates CDF figures.

Scripts
```bash
python scripts/plot_cdf_real_vs_null.py
python scripts/plot_cdf_real_vs_null_with_KS_and_zoom.py
```

Outputs
- figures/fig_cdf_real_vs_null_R10.png
- figures/fig_cdf_real_vs_null_R10_KS_zoom.png

### E3 - part 2 - Interpretation

- These figures show the empirical cumulative distribution functions (CDFs) of local density for the real and null configurations, with the KS statistic corresponding to the maximum vertical separation between the curves.

---

### E4 - Multi-scale robustness analysis

### E4 - Objective

To assess how the discrepancy between real and null configurations depends on the spatial scale.

Script
```bash
python scripts/sweep_radius_density_real_embedding.py
```

### E4 - Procedure

Repeat the density comparison for multiple neighborhood radii:
```css
R in {2, 5, 10, 20}
```

### E4 - This script:
- repeats the density comparison across multiple R,
- computes KS statistics as a function of scale,

### E4 - Outputs
`data/radius_sweep_real_embedding.csv`

Typical results:
```ini
R=  2.0: mean(real)=2898.05 | mean(null)=2884.38 | KS=0.0413 | p=1.72e-37
R=  5.0: mean(real)=9337.79 | mean(null)=9299.54 | KS=0.0631 | p=7.20e-87
R= 10.0: mean(real)=19971.47 | mean(null)=19901.52 | KS=0.0717 | p=3.31e-112
R= 20.0: mean(real)=45468.66 | mean(null)=45327.84 | KS=0.0518 | p=7.87e-59
```

### E4 – Interpretation 

At all tested radii, the Kolmogorov–Smirnov test strongly rejects the null hypothesis (p ≪ 10⁻⁶), indicating statistically incompatible distributions.

The magnitude of the discrepancy is scale-dependent. The KS statistic reaches its maximum at intermediate radii (R ≈ 10), indicating a regime in which residual spatial correlations are most pronounced.

At small radii, neighborhoods probe immediate proximity and are dominated by discreteness and local rarefaction effects.
At large radii, spatial averaging progressively smooths out local fluctuations, reducing sensitivity to residual correlations.

Here, the term mesoscopic is used in a relative sense, referring to intermediate scales within the explored range of neighborhood radii rather than to an absolute spatial size.


### E4 - part 2 - Generates the KS × R figure

- Generates the KS × R figure

```bash
python scripts/plot_ks_vs_radius_real_embedding.py
```

![Image generated](./figures/fig_ks_vs_radius_real_embedding.png)

Poderia interpretar essa imagem, por favor.



---

### Supplementary experiment — Stability under increasing N

### Supplementary experiment — Objective

To verify that the observed discrepancies are not artifacts of a specific cutoff size.

### Supplementary experiment — Output
`figures/KS_vs_N_caps.png`

![Image generated](./figures/fig_ks_vs_N_same_geometry.png)
Kolmogorov–Smirnov divergence between the empirical distributions of local prime
density for the real configuration and the same-geometry Cramér null model,
as a function of the cutoff N.
The KS statistic remains strictly positive and statistically significant across
all tested values of N, while decreasing smoothly as the domain size increases.
This behavior indicates that the observed discrepancy is not a finite-size (cutoff)
artifact, but rather reflects residual spatial correlations that are progressively
diluted by spatial averaging in larger domains.


### Supplementary experiment – Interpretation
To verify that the detected discrepancy is not an artifact of a specific cutoff, we repeat the analysis for increasing values of N while keeping the neighborhood radius fixed.

The KS statistic remains strictly positive and statistically significant for all tested values of N, while decreasing smoothly as N increases. This behavior indicates that the effect is not a finite-size artifact, but reflects residual spatial correlations that are gradually diluted by spatial averaging in larger domains.



---

Conceptual summary

| Experiment    | Role                        |
| ------------- | --------------------------- |
| E1            | Defines the geometry        |
| E2            | Defines the null hypothesis |
| E3            | Detects local discrepancies |
| E4            | Tests scale robustness      |
| Supplementary | Verifies stability          |

---
### Key takeaway

- If the geometric null model were sufficient, the empirical density distributions of the real and null configurations would be statistically indistinguishable at all scales.
The systematic rejection of the null hypothesis, particularly at intermediate scales, demonstrates the presence of residual spatial correlations in the geometric distribution of prime numbers.

---

## License and citation

Code: MIT License (see LICENSE)

Text and figures: CC BY 4.0
© 2026 Taciana Gomes

A CITATION.cff file is provided for automatic citation.

---

## Contact

**Taciana Gomes**  
Independent researcher  
GitHub: https://github.com/tacigomess
