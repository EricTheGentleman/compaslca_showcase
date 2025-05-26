import csv
import json
from pathlib import Path

import csv
import json
from pathlib import Path

def append_emissions_to_csv(csv_path, json_dir, output_csv_path, config_database):
    """
    Appends min, mean, and max values for emissions from JSON files
    into a new CSV file based on matching GlobalId or CompilationGroupID.
    """

    # === Select emission keys and JSON field based on config_database ===
    if config_database.lower() == "kbob":
        indicator_field = "Matched Materials with Gross Emissions (KBOB)"
        keys_to_analyze = [
            "Global Warming Potential Total [kgCO2-eqv]",
            "Biogenic Carbon [kg C]",
            "UBP (Total)",
            "Total Renewable Primary Energy [kWh oil-eq]",
            "Total Non-Renewable Primary Energy [kWh oil-eq]"
        ]
    else:  # Assume OEKOBAUDAT
        indicator_field = "Matched Materials with Gross Emissions (OEKOBAUDAT)"
        keys_to_analyze = [
            "GWPbiogenic",
            "GWPfossil",
            "GWPtotal"
        ]

    csv_path = Path(csv_path)
    json_dir = Path(json_dir)
    output_csv_path = Path(output_csv_path)

    # === Read CSV ===
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames.copy()

    # === Add new columns ===
    for key in keys_to_analyze:
        fieldnames.append(f"{key} (min)")
        fieldnames.append(f"{key} (mean)")
        fieldnames.append(f"{key} (max)")

    # === Process each row ===
    for row in rows:
        match_id = row["Id"]

        # Try to find matching JSON file
        matching_file = None
        for json_file in json_dir.rglob("*.json"):
            with open(json_file, encoding="utf-8-sig") as jf:
                try:
                    data = json.load(jf)
                except json.JSONDecodeError:
                    continue

            if data.get("GlobalId") == match_id or data.get("CompilationGroupID") == match_id:
                matching_file = data
                break

        # If no matching file found, leave new fields empty
        if not matching_file:
            for key in keys_to_analyze:
                row[f"{key} (min)"] = ""
                row[f"{key} (mean)"] = ""
                row[f"{key} (max)"] = ""
            continue

        materials = matching_file.get(indicator_field, [])

        for key in keys_to_analyze:
            try:
                values = [
                    float(mat[key]) for mat in materials
                    if key in mat and mat.get("Name", "").lower() != "none"
                ]
            except ValueError:
                values = []

            if values:
                min_val = round(min(values), 4)
                max_val = round(max(values), 4)
                mean_val = round((min_val + max_val) / 2, 4)
            else:
                min_val = max_val = mean_val = ""

            row[f"{key} (min)"] = min_val
            row[f"{key} (mean)"] = mean_val
            row[f"{key} (max)"] = max_val

    # === Write new CSV ===
    with open(output_csv_path, "w", newline='', encoding="utf-8-sig") as outf:
        writer = csv.DictWriter(outf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Final Bill of Quantities saved under: {output_csv_path}")
