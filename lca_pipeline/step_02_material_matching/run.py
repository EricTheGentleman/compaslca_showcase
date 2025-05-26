from lca_pipeline.step_02_material_matching.step_02a_inference.run import material_matcher
from lca_pipeline.step_02_material_matching.step_02b_bookkeeping.run import bookkeeper

def compaslca_module_two():
    material_matcher()
    bookkeeper()

if __name__ == "__main__":
    compaslca_module_two()