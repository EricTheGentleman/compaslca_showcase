from pathlib import Path
from methods.utils import load_yaml_config, copy_boq_to_report, copy_metadata_to_report
from methods.compile_jsons import compile_elements, compile_target_layers
from methods.compile_positives_negatives import collect_match_status
from methods.plots import plot_indicators

def make_path(*parts):
    return Path(*parts)

# Load config
master_config_path = Path("config/master_config.yaml")
master_config = load_yaml_config(master_config_path)
config_database = master_config.get("database_config", {}).get("database")

# Base path setup
db = config_database.lower()
pipeline_base = make_path("data", "pipeline", "step_03_lca_calculation")
output_base = make_path("data", "output", "report", db)

paths = {
    "boq_csv": pipeline_base / "step_03b_gross_emissions" / db / "BoQ.csv",
    
    "input_elements": {
        "gross_emissions": pipeline_base / "step_03b_gross_emissions" / db / "Elements",
        "specific_indicators": pipeline_base / "step_03a_specific_indicators" / db / "Elements",
    },
    "input_target_layers": {
        "gross_emissions": pipeline_base / "step_03b_gross_emissions" / db / "Target_Layers",
        "specific_indicators": pipeline_base / "step_03a_specific_indicators" / db / "Target_Layers",
    },
    
    "output_elements": {
        "gross_emissions": output_base / "elements" / "gross_emissions",
        "specific_indicators": output_base / "elements" / "specific_emissions",
    },
    
    "output_metadata": output_base / "metadata",
    "output_report": output_base,
    
    "input_parent_dir": pipeline_base / "step_03a_specific_indicators" / db,
}


def create_report():
    # Compile elements
    compile_elements(paths["input_elements"]["gross_emissions"], paths["output_elements"]["gross_emissions"])
    compile_elements(paths["input_elements"]["specific_indicators"], paths["output_elements"]["specific_indicators"])

    # Compile target layers
    compile_target_layers(paths["input_target_layers"]["gross_emissions"], paths["output_elements"]["gross_emissions"])
    compile_target_layers(paths["input_target_layers"]["specific_indicators"], paths["output_elements"]["specific_indicators"])

    # Collect match metadata
    collect_match_status(paths["input_parent_dir"], paths["output_metadata"])

    # Copy BoQ
    copy_boq_to_report(paths["boq_csv"], paths["output_report"])

    # Copy and annotate inference metadata
    copy_metadata_to_report(config_database, paths["output_metadata"])

    # Generate plots
    plot_indicators(paths["boq_csv"], paths["output_report"] / "plots", config_database)


if __name__ == "__main__":
    create_report()
    print(f"LCA report generated successfully in {paths['output_report']}.")