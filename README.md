# COMPAS-LCA

**COMPAS-LCA** is a modular, prototype software package designed to demonstrate an **LLM-based IFC-LCA workflow**.

This repository includes:
- A demo IFC model: `Duplex.ifc`
- A modular pipeline that allows processing, matching, and lifecycle assessment using configurable LLM prompts

To get started, follow the instructions below.

---

## Quick Start

### 1. Clone the Repository
Clone the repository into your local environment (e.g., VS Code).

```bash
git clone https://github.com/your-repo/COMPAS-LCA.git
```

### 2. Install Dependencies

You can either follow the steps below or install directly from `requirements.txt`.

#### Installation Instructions:
1. Install [Anaconda](https://www.anaconda.com/).
2. Create a virtual environment:
   ```bash
   conda create -n compas_lca python=3.9
   conda activate compas_lca
   ```
3. Install the required packages:
   ```bash
   conda install -c conda-forge compas compas_occ
   pip install compas_ifc openai seaborn pyyaml
   ```
4. Make sure you're using the `compas_lca` environment for running the pipeline.

---

## Using Your Own IFC File

1. Place **one** `.ifc` file in:
   ```
   data/input/IFC_model/
   ```
   Only IFC models based on **IFC schema 2x3** are supported. Ensure that **only one IFC file** is present in this folder.

---

## Configuration Setup

All user-defined settings are specified in:
```
config/master_config.yaml
```

Here, you can configure:
- The **LCA database**
- The **LLM provider and API key**
- Custom **prompt instructions**
- Settings for **IFC data input** to the matching module

Each configuration section is documented within the YAML file itself.

---

## Running the Workflow

Navigate to:
```
scripts/compas_lca.py
```

Run the script to launch the **interactive terminal menu** (preferably in VS Code). You can then choose to:

- Run the **full pipeline** with the Duplex.ifc model (or any model of your choice)
- Execute individual **(sub)modules**
- Preview and adjust the **LLM prompt instructions**

**Recommended**: Run modules independently to better inspect intermediate outputs.

If you want to run the demo with the HILO file, the JSONs have already been prepared for you (because extraction takes a long time):

- Navigate to data/input/HiLo_Demo
- There you will find a folder called "step_01a_extract_all" (data/input/HiLo_Demo/step_01a_extract_all)
- Delete the preexisting empty "data/pipeline/step_01_data_extraction/step_01a_extract_all"
- Then simply drag the folder in the HiLo_Demo folder into "data/pipeline/step_01_data_extraction"
- In the pipeline runner, you can now skip 01A and proceed with 01B


---

## After Running the First Module

You will get:
- **Metadata**
- A preliminary **Bill of Quantities (BoQ)**
- An optional **cost estimation**, based on the chosen provider

**Cost Benchmark**: Running GPT-4o costs approximately **$0.01 per inference**. For 200 unique inferences, the total cost would be around **$2.00**.

You can adjust the prompt or model settings before proceeding to the next module by editing `master_config.yaml`.

If you want to do the inference for both KBOB and OEKOBAUDAT, then you can run modules 2-4 with one database configuration in `master_config.yaml`, and then change the database configuration and rerun modules 2-4. All results will be stored in corresponding folders (so no files are overwritten when the database configuration is changed).

---

## Tips & Warnings

- You can re-run **Module 01d** as many times as you like. Use it to filter and inspect data before LLM inference.
- To **preview the prompt**, use the menu option in `compas_lca.py`. Tweak and rerun until satisfied.
- **Important:** Element names with more than **100 characters** may break the traverser method.
- Some OS environments may not support file paths longer than **250 characters**. Reduce long element names manually to avoid issues.
- This is especially relevant when using the **OEKOBAUDAT** database, which typically requires multiple inferences per material.

---

## Module Descriptions (Coming Soon)

Detailed descriptions of each module will be provided here.
