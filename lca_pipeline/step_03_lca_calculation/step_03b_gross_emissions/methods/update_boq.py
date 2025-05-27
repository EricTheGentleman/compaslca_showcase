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
            "GWPtotal",
            "GWPtotal (A1-A3)",
            "GWPtotal (A4)",
            "GWPtotal (A5)",
            "GWPtotal (C1)",
            "GWPtotal (C2)",
            "GWPtotal (C3)",
            "GWPtotal (C4)"
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

        # If no matching file found, mark all as "not matched"
        if not matching_file:
            for key in keys_to_analyze:
                row[f"{key} (min)"] = "not matched"
                row[f"{key} (mean)"] = "not matched"
                row[f"{key} (max)"] = "not matched"
            continue

        materials = matching_file.get(indicator_field, [])

        # If all materials are "None", treat as not matched
        if all(mat.get("Name", "").lower() == "none" for mat in materials):
            for key in keys_to_analyze:
                row[f"{key} (min)"] = "not matched"
                row[f"{key} (mean)"] = "not matched"
                row[f"{key} (max)"] = "not matched"
            continue

        for key in keys_to_analyze:
            try:
                if key == "GWPtotal (A1-A3)":
                    values = []
                    for mat in materials:
                        if mat.get("Name", "").lower() == "none":
                            continue
                        val = mat.get("GWPtotal (A1-A3)")
                        if val not in (None, "", "null"):
                            try:
                                values.append(float(val))
                            except ValueError:
                                continue
                        else:
                            # Try summing A1 + A2 + A3
                            try:
                                a1 = float(mat.get("GWPtotal (A1)", 0) or 0)
                                a2 = float(mat.get("GWPtotal (A2)", 0) or 0)
                                a3 = float(mat.get("GWPtotal (A3)", 0) or 0)
                                values.append(round(a1 + a2 + a3, 4))
                            except ValueError:
                                continue
                else:
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
