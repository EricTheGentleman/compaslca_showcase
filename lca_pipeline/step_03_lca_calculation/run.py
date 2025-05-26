from lca_pipeline.step_03_lca_calculation.step_03a_specific_indicators.run import append_indicators
from lca_pipeline.step_03_lca_calculation.step_03b_gross_emissions.run import gross_emissions

def compaslca_module_three():
    append_indicators()
    gross_emissions()

if __name__ == "__main__":
    compaslca_module_three()