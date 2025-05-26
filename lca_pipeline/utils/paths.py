# lca_pipeline/utils/paths.py

from pathlib import Path

def get_single_ifc_file():
    # Find project root (e.g. where 'data' folder exists)
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / "data" / "input" / "IFC_model").exists():
            ifc_dir = current / "data" / "input" / "IFC_model"
            break
        current = current.parent
    else:
        raise FileNotFoundError("Could not find 'data/input/IFC_model' from current script location.")

    ifc_files = list(ifc_dir.glob("*.ifc"))
    if len(ifc_files) != 1:
        raise FileNotFoundError(f"Expected exactly one IFC file in {ifc_dir}, but found {len(ifc_files)}.")

    return ifc_files[0]