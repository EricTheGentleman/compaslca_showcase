# COMPAS-LCA

COMPAS-LCA is a modular software package which is a prototype for an LLM-based IFC-LCA workflow. 
This is a demo file, with an open-source IFC model ready to process (Duplex.ifc)
Read the user-manual and navigate to "scripts/compas_lca.py" and run the file to access the menu.

User-Manual:
1. Clone the repository to VScode
2. Install dependencies. They can be found in the requirements.txt. You can also follow the instructions of "Installation process"
3. Drag and drop your IFC file into data/input/IFC_model. Note: COMPAS-LCA only supports IFC models of schema 2x3, and there may always only be one IFC model inside of this folder.
4. Specify the configurations in the master config file (config/master_config.yaml). Here all user-defined configurations, such as choosing the LCA database, choosing the LLM provider and inserting the API key, specifying modular prompt instructions, and customizing the IFC data input for the LLM-based matching module can be found. Detailed instructions are provided within the file.
5. When you are content with the configuration settings, you can navigate to scripts/compas_lca.py and run that script. A menu will show in the terminal (in VScode). There you can choose if you want to run the entire pipeline or run (sub)modules. If you want full control over the workflow, it is recommended to run the submodules independently and inspect the intermediate results. The COMPAS-LCA menu also allows for previewing the customized prompts. Detailed descriptions of what each module does is specified under "Module Descriptions"
6. After running the first module, you will have access to metadata and a preliminary bill of quantities of the IFC model. Depending on the chosen provider, a cost estimation will be presented. As a benchmark: running gpt-4o costs approximately 0.01 cents (so if the amount of unique inferences is 200, then the entire LLM-based matching will cost 2 dollars). Furthermore, prompt and models settings can be still adjusted in the master_config.yaml, before proceeding with the second module.

Installation process:
1. install anaconda
2. Create virtual environment: conda create -n compas_lca python=3.9
3. conda activate compas_lca
4. conda install -c conda-forge compas compas_occ
5. pip install compas_ifc
6. pip install openai
7. pip install seaborn
8. pip install yaml
9. Use compas_lca virtual environment for pipeline
10. Or just use requirements.txt

Module Description: (TBA)

You can run module 01d as often as you want and adapt the filter settings in the master_config.yaml inspect the JSON files and if you want to still change it before running the LLM inference, feel free to do so.

If you want to add your own IFC file:
Upload ONE IFC file into the the folder data/input/IFC_model and make sure it is the ONLY one

For LLM inference:
Insert the LLM model specs and API key into the "master_config.yaml"
Check the "master_config.yaml", specify the inputs (or leave default)
You can run the preview prompt command and take a look at an exemplary prompt. You can change the prompt settings and inspect again, until you are happy with your prompt.

Important: Any Element Name that has a string longer than 100 characters might break the traverse method of the inference module. In some operating systems, the "os" library cannot read relative paths that are longer than 250 characters. It is important to manually reduce character count for really long and complex element names, or else the traverser method cannot recursively trace the path of index files (this is especially important when using the OEKOBAUDAT database, since it usually requires 4 unique inferences for definitive material match).


