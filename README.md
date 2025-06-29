# COMPAS-LCA

**COMPAS-LCA** is a modular, prototype software package designed to demonstrate an **LLM-based IFC-LCA workflow**.
The entire pipeline is built upon the LCA standard **EN 15978:2011**

This repository includes:
- A demo IFC model: `Duplex.ifc`
- A demo extraction folder of EMPA's HiLo building: `data/input/HiLo_Demo`
- A modular pipeline that allows processing, matching, and lifecycle assessment using configurable LLM prompts

To inspect flow-charts for the modules and architecture, please navigate to: `docs`

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
The current default settings of the master configuration are the best performing settings for KBOB (based upon empirical tests). 

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
- A count of required unique inference in the **Metadata** file.

**Cost Benchmark**: Running GPT-4o costs approximately **$0.01 per inference**. For 200 unique inferences, the total cost would be around **$2.00**.

You can adjust the prompt or model settings before proceeding to the next module by editing `master_config.yaml`.

If you want to do the inference for both KBOB and OEKOBAUDAT, then you can run modules 2-4 with one database configuration in `master_config.yaml`, and then change the database configuration and rerun modules 2-4. All results will be stored in corresponding folders (so no files are overwritten when the database configuration is changed). If you want to run the pipeline with the same database, but different settings inside of the configuration file, then you should be aware that the current project files will be overwritten (so please store them in an external folder, if you want to compare results).

---

## Tips & Warnings

- You can re-run **Module 01d** as many times as you like. Use it to filter and inspect data before LLM inference.
- To **preview the prompt**, use the menu option in `compas_lca.py`. Tweak and rerun until satisfied.
- **Important:** Element names with more than **100 characters** may break the traverser method.
- Some OS environments may not support file paths longer than **250 characters**. Reduce long element names manually to avoid issues.
- This is especially relevant when using the **OEKOBAUDAT** database, which typically requires multiple inferences per material.
- Few-Shot examples are currently only available for **KBOB**! Few-shot examples for **OEKOBAUDAT** will follow soon.
- Sometimes there will be a strong overshoot in the LCA output. This is usually the case if poorly modeled geometries recieve metal materials (with high emissions).
- If this is the case, please double check the quantities in the BoQ and inspect elements such as "metal stud layer", "metal grating", or "balcony".

---

## Module Descriptions

**MODULE 1: IFC Data Extraction**
The IFC data extraction module converts the input IFC model into standardized JSON files that capture geometric, material, and semantic information for each building element and material layer. It enables traceable, analysis-ready data by performing essential inferences for LCA and generating a detailed Bill of Quantities, structured across four specialized submodules. 

*Submodule 01a: Extractor*
Processes IFC models using COMPAS-IFC and COMPAS-OCC to retrieve structured data for each IfcBuildingElement, capturing geometry, materials, metadata, property sets, relationships, and spatial location in a standardized JSON format. It also generates a detailed Bill of Quantities and project metadata, with configurable options for element types, geometry computation, and processing time. Geometry Extraction via COMPAS-OCC and IfcBuildingElement sub-type selection can be specified in `config/master_config.yaml`
- `lca_pipeline/step_01_data_extraction/step_01a_extract_all`

*Submodule 01b: Aggregator*
Reduces redundant LLM API calls by grouping building elements with identical key attributes—such as element type, object type, material relationships, and descriptors, and selecting a single representative from each group. Updates the Bill of Quantities with aggregated values, and logs aggregation statistics in the metadata file.
- `lca_pipeline/step_01_data_extraction/step_01b_aggregate_elements`

*Submodule 01c: Dissector*
Decomposes multi-layer building elements into individual, layer-specific JSON files, each capturing both the material layer details and contextual building element data. It updates the Bill of Quantities and metadata to reflect layer-level breakdown.
- `lca_pipeline/step_01_data_extraction/step_01c_dissect_layers`

*Submodule 01d: Filter*
Finalizes preprocessing by reducing token count and noise in the extracted IFC data, ensuring only semantically relevant information is passed to the LLM. It is configurable via `config/master_config.yaml`, allowing definition of filtering logic—such as attribute selection, empty value removal, and property set prioritization—while also offering preset configurations to balance efficiency with semantic completeness across diverse modeling practices.


**MODULE 2: LLM-Based Material Matching Module**
LM matches each JSON file from the first module to entries in the selected LCA database. The LLM is configured through fully modular and user-definable parameters and prompts, allowing flexible adaptation to different use cases. Based on the resolution of the input data and the degree of semantic and functional alignment, the LLM may associate each element and layer with one, multiple, or no corresponding database entries. The resulting LLM outputs are systematically structured for automated downstream parsing.
- `data/pipeline/step_02_material_matching`

*Submodule 02a: Inference*
The "recursive LCA database traversal algorithm" is used to match IFC elements or layers to the most contextually appropriate material entries in the chosen LCA database (kbob or ökobaudat). It operates in two phases: first, the LLM recursively selects categories by navigating through nodes using simplified category files (llm_categories.json), then, upon reaching a leaf node, it switches to material inference using llm_materials.json. The hierarchically structured databases can be found in `data/input/LCI_database/KBOB` and `data/input/LCI_database/OEKOBAUDAT`. If you want to customize the CSV file to append additional information, use the following scripts to transform the CSV files into the required dissected JSON formats: `lca_pipeline/utils/transformer_kbob.py` and `lca_pipeline/utils/transformer_oekobaudat.py`. The structure of the database will be  organized like a tree, with each node containing metadata (index.json) and optimized input files for efficient LLM processing. This recursive process continues until a material match is found or inference is deemed unreliable, with all steps logged for performance and cost tracking.

The "LLM interface" (`lca_pipeline/step_02_material_matching/step_02a_inference/methods/llm_interface.py`) is used to pass the different models and hyperparameters to the inference task. Model choice can be specified in the master configuration file. The current COMPAS-LCA architecture (as of 29.06.2025) supports:
- OpenAI
  - gpt-4o
  - gpt-4o-mini
  - gpt-4.1
  - gpt-4.1-nano
  - gpt-4.1-mini
  - o3
  - o3-pro-2025-06-10
- Anthropic
  - claude-opus-4-20250514
  - claude-sonnet-4-20250514
  - claude-3-5-haiku-latest
- Gemini
  - gemini-2.5-pro-preview-05-06
  - gemini-2.5-flash-preview-04-17

The prompt builders can be found under: `lca_pipeline/step_02_material_matching/step_02a_inference/methods/prompt_builder_category.py` and `lca_pipeline/step_02_material_matching/step_02a_inference/methods/prompt_builder_material.py`. They leverage the prompt components, which are linked to the variables in the master configuration YAML file. They can be dynamically altered inside of the following files: `lca_pipeline/step_02_material_matching/step_02a_inference/methods/prompt_components_category.py` and `lca_pipeline/step_02_material_matching/step_02a_inference/methods/prompt_components_material.py`

*Submodule 02b: Bookkeeping*
This submodule simply aggragates all individual "steps" of the inference process into one JSON file for each inferred Element or Target Layer

**MODULE 3: LCA Calculation**
Enriches the semantically matched materials for each IFC element or layer with environmental impact indicators from the selected LCA database. It retrieves key attributes such as reference units, densities, and life cycle stage emissions from the database’s index.json, tailored to the standards of sources like KBOB or Ökobaudat. Simultaneously, geometric quantities from the Bill of Quantities are aligned with material units to calculate net environmental impacts. The results are saved in structured JSON files, and the BoQ is updated with statistical summaries (min, max, mean) to support comparative and uncertainty analysis in later stages.
- `lca_pipeline/step_03_lca_calculation`


**MODULE 4: LCA Report Generation**
Generates an LCA report using the updated Bill of Quantities (BoQ), enriched IFC element JSON files, and metadata. It creates a structured output directory with cleaned datasets, summary statistics, and visualizations of environmental impacts. The module produces plots showing per-element emissions, aggregated global warming potential by life cycle stage, and uncertainty ranges to highlight high-impact or high-variability elements. JSON files are standardized and include LLM-inferred material matches and emissions, resulting in a Bill of Materials (BoM). For aggregated elements, emissions and materials are linked to shared ObjectType values rather than individual instances. A comprehensive metadata file and documentation are also produced, detailing API usage, timestamps, and traceability information in compliance with EN 19578:2011.
- `lca_pipeline/step_04_lca_report`
- `data/output/report`