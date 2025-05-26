from lca_pipeline.step_01_data_extraction.step_01a_extract_all.run import extract_all
from lca_pipeline.step_01_data_extraction.step_01b_aggregate_elements.run import aggregate_elements
from lca_pipeline.step_01_data_extraction.step_01c_dissect_layers.run import dissect_layers
from lca_pipeline.step_01_data_extraction.step_01d_filter_data.run import filter_data_sheets

def compaslca_module_one():
    extract_all()
    aggregate_elements()
    dissect_layers()
    filter_data_sheets()

if __name__ == "__main__":
    compaslca_module_one()