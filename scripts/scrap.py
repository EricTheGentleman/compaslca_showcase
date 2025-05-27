import json
from pathlib import Path

def fix_volume_ratio(json_dir):
    json_dir = Path(json_dir)
    for file_path in json_dir.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            geom_data = data.get("Element Geometry Data", {})
            compas_volume = geom_data.get("Quantities (COMPAS)", {}).get("Net Volume")
            bbox_volume = geom_data.get("Bounding Box Volume")

            if compas_volume and bbox_volume and bbox_volume != 0:
                correct_ratio = compas_volume / bbox_volume
                # Round to 3 decimal places
                geom_data["Real Volume to Bounding Box Volume Ratio"] = round(correct_ratio, 3)

                # Write back the corrected JSON
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"Fixed ratio in: {file_path.name}")
            else:
                print(f"Skipping {file_path.name}: Missing or invalid volume values.")

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

# Example usage:
fix_volume_ratio("data/input/HiLo_Demo/step_01a_extract_all/Elements")
