import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.patches import Patch

legend_handles = [
    Patch(facecolor='skyblue', label='ObjectType'),
    Patch(facecolor='orchid', label='Unique Element')
]
plt.legend(handles=legend_handles, loc='upper right', fontsize=7, frameon=False)


def plot_indicators(csv_path, output_dir, database_config):

    # Set indicator list based on database
    if database_config.lower() == "kbob":
        indicators = [
            "Global Warming Potential Total [kgCO2-eqv]",
            "Biogenic Carbon [kg C]",
            "UBP (Total)",
            "Total Renewable Primary Energy [kWh oil-eq]",
            "Total Non-Renewable Primary Energy [kWh oil-eq]",
        ]
    else:
        indicators = [
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

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path, na_values=["not matched", "not available", ""])

    for indicator in indicators:
        min_col = f"{indicator} (min)"
        mean_col = f"{indicator} (mean)"
        max_col = f"{indicator} (max)"

        if not all(col in df.columns for col in [min_col, mean_col, max_col]):
            print(f"Skipping {indicator}: columns missing.")
            continue

        # Convert to numeric safely
        for col in [min_col, mean_col, max_col]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Filter rows where both min and max are missing or zero
        mask = ~((df[min_col].fillna(0) == 0) & (df[max_col].fillna(0) == 0))
        temp_df = df.loc[mask, ["Name", "Compiled", min_col, mean_col, max_col]].copy()

        if temp_df.empty:
            print(f"Skipping {indicator}: no valid data after filtering.")
            continue

        # Error
        temp_df["error"] = (temp_df[[max_col, min_col]].max(axis=1) - temp_df[[max_col, min_col]].min(axis=1)) / 2

        # Sort
        temp_df = temp_df.sort_values(by=mean_col, ascending=False).reset_index(drop=True)
        x = range(len(temp_df))

        # Colors
        bar_colors = ["skyblue" if compiled else "orchid" for compiled in temp_df["Compiled"]]

        # Plot
        plt.figure(figsize=(14, 6))
        for i in x:
            plt.bar(i, temp_df[mean_col].iloc[i], color=bar_colors[i], edgecolor="none")

        plt.xlim(-1.5, len(temp_df))

        err = plt.errorbar(
            x=x,
            y=temp_df[mean_col],
            yerr=temp_df["error"],
            fmt='none',
            ecolor='black',
            capsize=3.5,
            linewidth=0.7
        )
        for cap in err[1]:
            cap.set_linewidth(0.3)

        # X-ticks
        plt.xticks(ticks=x, labels=temp_df["Name"], rotation=90, ha='right', fontsize=5)
        plt.yticks(fontsize=6)
        plt.ylabel(indicator, fontsize=8)

        # Tick label colors
        ax = plt.gca()
        xtick_labels = ax.get_xticklabels()
        for i, label in enumerate(xtick_labels):
            label.set_color('skyblue' if temp_df["Compiled"].iloc[i] else 'orchid')

        # Legend
        legend_handles = [
            Patch(facecolor='skyblue', label='ObjectType'),
            Patch(facecolor='orchid', label='Unique Element')
        ]
        plt.legend(handles=legend_handles, loc='upper right', fontsize=7, frameon=False)

        plt.title(indicator, fontsize=10)
        plt.tight_layout()

        # Save
        safe_name = indicator.split("[")[0].strip().replace(" ", "_").replace("(", "").replace(")", "").lower()
        output_file = output_dir / f"{safe_name}_plot.png"
        plt.savefig(output_file, dpi=300)
        plt.close()



def plot_total_gwp_individual(csv_path, output_dir, database_config):

    # Load data
    df = pd.read_csv(csv_path, na_values=["not matched", "not available", ""])

    # Configuration
    if database_config.lower() == "kbob":
        indicators = [
            "Global Warming Potential Manufacturing [kgCO2-eqv]",
            "Global Warming Potential Disposal [kgCO2-eqv]",
            "Global Warming Potential Total [kgCO2-eqv]",
        ]
        base_color = "#f5c396"
        total_color = "#db8c2e"
        db_label = "KBOB"
    elif database_config.lower() == "oekobaudat":
        indicators = [
            "GWPtotal (A1-A3)",
            "GWPtotal (A4)",
            "GWPtotal (A5)",
            "GWPtotal (C1)",
            "GWPtotal (C2)",
            "GWPtotal (C3)",
            "GWPtotal (C4)",
            "GWPtotal"
        ]
        base_color = "#e1d3f9"
        total_color = "#c3a6f3"
        db_label = "Oekobaudat"
    else:
        raise ValueError("database_config must be either 'kbob' or 'oekobaudat'")

    # Prepare data
    indicators_present = []
    means = []
    errors = []
    colors = []

    for ind in indicators:
        min_col, mean_col, max_col = f"{ind} (min)", f"{ind} (mean)", f"{ind} (max)"
        if all(col in df.columns for col in [min_col, mean_col, max_col]):
            mean_val = df[mean_col].sum()
            diffs = df[[max_col, min_col]].dropna()
            error_val = ((diffs[max_col] - diffs[min_col]) / 2).clip(lower=0).sum()

            indicators_present.append(ind)
            means.append(mean_val)
            errors.append(error_val)
            colors.append(total_color if "Total" in ind or ind == "GWPtotal" else base_color)
        else:
            print(f"Missing columns for indicator: {ind}")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 5))

    x_pos = list(range(len(indicators_present)))
    ax.bar(x_pos, means, yerr=errors, capsize=4, color=colors, edgecolor='none')

    ax.set_xticks(x_pos)
    ax.set_xticklabels(indicators_present, rotation=45, ha='right', fontsize=8)

    ax.set_ylabel("Total GWP [kgCO2-eqv]", fontsize=10)
    ax.set_title(f"Total GWP – {db_label}", fontsize=12)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, linestyle='-', linewidth=0.5, alpha=0.4)

    plt.tight_layout()

    # Save
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename_base = f"GWP_total_{db_label}"
    png_path = output_dir / f"{filename_base}.png"

    plt.savefig(png_path, dpi=300)
    plt.close()