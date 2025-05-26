# Transform ökobaudat CSV into JSON directory structure for recursive traversal of LLM inference
import csv
import os
import json

csv_file_path = "data/input/LCI_database/csv/oekobaudat.csv"
output_base_dir = "data/input/LCI_database/OEKOBAUDAT"
index_filename = 'index.json'

def normalize_folder_name(name):
    return name.strip().replace(" ", "_").replace(",", "").replace("/", "_")

# Build a nested dictionary structure
def insert_nested_material(tree, path_parts, material):
    if not path_parts:
        return
    head, *tail = path_parts
    if head not in tree:
        tree[head] = {"__materials__": [], "__children__": {}}
    if tail:
        insert_nested_material(tree[head]["__children__"], tail, material)
    else:
        tree[head]["__materials__"].append(material)


def write_tree_to_disk(tree, base_path, path_parts=None):
    if path_parts is None:
        path_parts = []

    os.makedirs(base_path, exist_ok=True)

    index_items = []
    has_subfolders = False
    has_materials_here = False

    for name, node in tree.items():
        folder_name = normalize_folder_name(name)
        folder_path = os.path.join(base_path, folder_name)
        sub_path_parts = path_parts + [name]

        os.makedirs(folder_path, exist_ok=True)

        # Write materials for the current child node (i.e., in its own folder)
        if node["__materials__"]:
            has_materials_in_child = True
            with open(os.path.join(folder_path, index_filename), 'w', encoding='utf-8') as f:
                json.dump({
                    "type": "materials",
                    "path": " / ".join(sub_path_parts),
                    "items": node["__materials__"]
                }, f, indent=2, ensure_ascii=False)

        # Recurse into children
        if node["__children__"]:
            write_tree_to_disk(node["__children__"], folder_path, sub_path_parts)
            has_subfolders = True

        # Regardless of what's inside, this child gets listed
        index_items.append({
            "name": name,
            "path": f"{folder_name}/{index_filename}"
        })

    # Detect if *this folder itself* has direct materials (rare in your structure)
    has_materials_here = "__materials__" in tree and bool(tree["__materials__"])

    # Determine type for this folder
    if has_subfolders and not has_materials_here:
        index_type = "categories"
    elif not has_subfolders and has_materials_here:
        index_type = "materials"
    elif has_subfolders and has_materials_here:
        index_type = "mixed"
    else:
        index_type = "categories"  # fallback: still needs an index

    # Write index.json for this folder
    with open(os.path.join(base_path, index_filename), 'w', encoding='utf-8') as f:
        json.dump({
            "type": index_type,
            "path": " / ".join(path_parts),
            "items": index_items
        }, f, indent=2, ensure_ascii=False)


def transform():
    tree = {}

    with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [field.strip() for field in reader.fieldnames]

        for row in reader:
            row = {k.strip(): v for k, v in row.items()}
            category_path = row.pop("Category", None)
            if not category_path:
                continue

            parts = [p.strip(" '") for p in category_path.split(" / ")]
            cleaned_row = {k: v for k, v in row.items() if v and v.strip()}
            insert_nested_material(tree, parts, cleaned_row)

    write_tree_to_disk(tree, output_base_dir)
    print("Hierarchy exported successfully.")

if __name__ == "__main__":
    transform()

