
# Choragraph: Deep-Learning Framework for Spatial Proteomics

[![bioRxiv](https://img.shields.io/badge/bioRxiv-10.64898%2F2026.06.27.734956v1-red)](https://www.biorxiv.org/content/10.64898/2026.06.27.734956v1)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://tensorflow.org)

**Choragraph** is a deep-learning based approach to the spatial mapping and analysis of subcellular proteomics. 

By using an ensemble of deep neural networks integrated with **whole-proteome cross-attention** and **Bayesian Variational Inference (BVI)**, Choragraph accomplishes two concurrent objectives:
1. **Context-Dependent Profile Reconstruction**: Reconstruction of missing values in proteomic abundance profiles (typically up to 35%), rescuing thousands of proteins that might otherwise not be analysed.
2. **Multi-Localization Classification**: Maps protein subcellular localisation in a manner that is natively aware of multi-localisation, to identify trafficking and multi-resident proteins.

🌐 Explore the interactive web application showing our *Arabidopsis thaliana* datasets at [choragraph.org](https://choragraph.org).

---

## Multi-Stage Pipeline Workflow

The architecture is partitioned into a 3-step pipeline designed to transition from raw proteomic profiles, which may include missing values, into inferred subcellular localisations and reconstructed/demoised output profiles:

```
[Raw Replicate Profile TSVs & Class Marker CSVs]
│
▼
┌──────────────────────────┐
│ 1. Data Preparation      │  ──► Run via collate_inputs.py; combines replicates, prunces classification labels and archives to .npz
└──────────────────────────┘
│
▼
┌──────────────────────────┐
│ 2. DNN Ensemble Training │  ──► Run via dnn_workflow.py; trains, cross-validates and runs whole-proteome based inference
└──────────────────────────┘
│
▼
┌──────────────────────────┐
│ 3. Collation & Exporter  │  ──► Run via collate_outputs.py; generates p-values and outputs SQLite/TSVs
└──────────────────────────┘

```

---

## 🛠️ Installation & Requirements

Ensure you are using Python 3.8 or greater and clone the repository and install the framework dependencies:

```bash
git clone [https://github.com/tjs23/choragraph.git](https://github.com/tjs23/choragraph.git)
cd choragraph
pip install -r requirements.txt

```

---

## 💻 Command-Line Interface (CLI) Guide

### Step 1: Data Preparation (`collate_inputs.py`)

Combines multiple replicate input proteomic abundance files (`.tsv`) with subcellular marker lists (`.csv`) and prunes the markers prior to DNN training. 

```bash
python collate_inputs.py \
  -r "Arabidopsis_June26" \
  -p 'profiles/replicates*.tsv' \
  -o "markers/organelle_markers.csv" \
  -u "markers/suborganelle_markers.csv" \
  -s EXTRACELLULAR CORTEX PROTEASOMAL RIBOSOMAL

```

* **Key Arguments:**
* `-r`, `--run-tag` *(Required)*: Identifier for the current run.
* `-p`, `--profile-pattern` *(Required)*: Glob pattern for profile TSV files.
* `-o`, `--organelle-markers` *(Required)*: Path to the organelle markers CSV file.
* `-u`, `--suborganelle-markers` *(Required)*: Path to the suborganelle markers CSV file.
* `-s`, `--sensitive-classes`: Space-separated list of classes that should not have a correlation check during marker pruning; these may be sparse, have low counts or be deemed particularly well defined (Default: `EXTRACELLULAR, CORTEX, PROTEASOMAL, RIBOSOMAL`).
* `-d`, `--output-dir`: Directory where output files will be saved (Default: `datasets`).

---

### Step 2: DNN Ensemble Training (`dnn_workflow.py`)

Executes the deep learning pipeline over the generated datasets. Scales the latent vector size based on profile feature length, tracks data splitting, outputs loss metric graphs, and averages multi-model weights.

```bash
python dnn_workflow.py \
  -p "datasets/Arabidopsis_June26.npz" \
  -m 10 \
  -e 75 \
  -b 64 \
  -f 0.35 \
  -n PROTEASOMAL RIBOSOMAL

```

* **Key Arguments:**
* `-d`, `--datasets` *(Required)*: Glob pattern for input dataset files.
* `-m`, `--models-dir`: Directory to store model weights and training plots (Default: `models`).
* `-n`, `--n-models`: Number of models to train (Default: `10`).
* `-e`, `--n-epochs`: Number of epochs to train (Default: `75`).
* `-b`, `--batch-size`: Batch size for training (Default: `64`).
* `-f`, `--max-nan-frac`: Maximum allowed fraction of NaNs (Default: `0.35`).
* `-n`, `--nomix-organelles`: Space-separated list of organelles to exclude from mixing (Default: `PROTEASOMAL, RIBOSOMAL`).
* `--no-overwrite`: Include flag to disable overwriting existing predictions and models.


---

### Step 3: Collation & Database Finalization (`collate_outputs.py`)

Calculates protein multi-localization p-values, aggregates ensemble model outputs, makes best-guess localisations and reconstructed protein profiles. Outputs classification tables and a queryable relational database file. Optionally accepts external classifications for comparison.

```bash
python collate_outputs.py \
  -d "datasets/Arabidopsis_June26.npz" \
  -m "markers/Arabidopsis_OTHER_predictions.csv" \
  -t 0.9999 \
  -f 0.5

```

* **Key Arguments:**
* `-d`, `--datasets` *(Required)*: Glob pattern for input dataset files.
* `-m`, `--comparison-markers`: Optional path to external comparison markers CSV file.
* `-t`, `--score-thresh`: Score threshold for external markers (Default: `0.9999`).
* `-f`, `--max-missing`: Maximum missing data fraction allowed in a profile (Default: `0.5`).
* `--no-reset`: Disable resetting 2D projections.

---

## 📊 Output Artifact Taxonomy

* **`datasets/*.npz`**: Compressed NumPy archives containing input data, training configurations, and predictive ensemble output from the DNN models; compartmental proportions and profile reconstructions

* **`models/*.weights.h5`**: Standardized model checkpoint weight files.

* **`models/*_training.png`**: Multi-epoch loss and learning diagnostic trajectory charts.

* **`datasets/*.sqlite`**: Portable SQL relational databases holding finished protein records, multi-localization parameters, and p-values.

* **`datasets/*_profiles.tsv`**: Tab-separated flat files aligning native (`init`), zero-filled (`zfill`), and fully synthesized (`recon`) coordinates.


---

## 📑 Citation

If you incorporate the Choragraph framework, models, or workflow modules into your spatial proteomics research pipelines, please cite our manuscript:

```bibtex
@article{parsons2026choragraph,
  title={Choragraph: A deep-learning approach for the analysis of spatial proteomics reveals subcellular Arabidopsis protein trafficking routes and multiresidency},
  author={Parsons, Harriet T. and Stevens, Tim J.},
  journal={bioRxiv},
  volume={10.64898/2026.06.27.734956v1},
  year={2026},
  publisher={Cold Spring Harbor Laboratory}
}

```
