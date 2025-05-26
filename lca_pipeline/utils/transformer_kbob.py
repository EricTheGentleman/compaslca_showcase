# Transform KBOB CSV into JSON directory structure for recursive traversal of LLM inference


import csv
import os
import json
from collections import defaultdict

# === CONFIGURATION ===
csv_file_path = "data/input/LCI_database/csv/kbob.csv"   # Your CSV
output_base_dir = "data/input/LCI_database/KBOB"         # Output folder
index_filename = 'index.json'                            # JSON file name

def normalize_folder_name(name):
    return name.strip().replace(" ", "_").replace(",", "").replace("/", "_")

# transforms CSV into hierarchical JSON database
def kbob_transformer():
    materials_by_category = defaultdict(list)

    with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Normalize column names to remove leading/trailing spaces
        reader.fieldnames = [field.strip() for field in reader.fieldnames]
        
        for row in reader:
            # Normalize row keys
            row = {k.strip(): v for k, v in row.items()}
            category = row.pop("Category", None)
            if not category:
                continue

            cleaned_row = {k: v for k, v in row.items() if v and v.strip()}
            materials_by_category[category].append(cleaned_row)

    # Top-level index
    top_index = {
        "type": "categories",
        "items": []
    }

    for category, materials in materials_by_category.items():
        safe_category = normalize_folder_name(category)
        category_dir = os.path.join(output_base_dir, safe_category)
        os.makedirs(category_dir, exist_ok=True)

        category_index_path = os.path.join(category_dir, index_filename)
        with open(category_index_path, 'w', encoding='utf-8') as jsonfile:
            json.dump({
                "type": "materials",
                "items": materials
            }, jsonfile, indent=2, ensure_ascii=False)

        top_index["items"].append({
            "name": category,
            "path": f"{safe_category}/{index_filename}"
        })

    os.makedirs(output_base_dir, exist_ok=True)
    top_index_path = os.path.join(output_base_dir, index_filename)
    with open(top_index_path, 'w', encoding='utf-8') as topfile:
        json.dump(top_index, topfile, indent=2, ensure_ascii=False)

    print(f" Created {len(materials_by_category)} category folders.")

if __name__ == "__main__":
    kbob_transformer()

