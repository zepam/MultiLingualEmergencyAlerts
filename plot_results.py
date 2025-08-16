import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

def main():
    # Directory where your result files are stored
    directory = "./"   # change to your path if needed

    # Get all files that start with 'results'
    files = glob.glob(os.path.join(directory, "results*.csv"))

    if not files:
        print("No results files found.")
        return

    # Combine all CSVs into a single DataFrame (assume first row is header)
    all_dfs = []
    for file in files:
        print(f"Reading {file}...")
        df = pd.read_csv(file)
        # Extract service name from filename (e.g., results_deepseek.csv -> deepseek)
        base = os.path.basename(file)
        if base.startswith("results_") and base.endswith(".csv"):
            service = base[len("results_"):-len(".csv")]
        else:
            service = base
        df["SERVICE_FROM_FILENAME"] = service
        all_dfs.append(df)

    combined_df = pd.concat(all_dfs, ignore_index=True)
    print("Combined DataFrame shape:", combined_df.shape)
    print(combined_df.head())

    # Save the combined table as a CSV
    combined_df.to_csv("all_results_combined.csv", index=False)
    print("✅ Combined table written to all_results_combined.csv!")

    # Automatically determine metric columns: all columns except the first few (metadata)
    metadata_cols = {"SERVICE", "LANGUAGE", "DISASTER", "PROMPT"}
    metric_cols = [col for col in combined_df.columns if col not in metadata_cols]
    if not metric_cols:
        print("No metric columns found (all columns are metadata).")
        return
    
    # Ensure the plots directory exists
    plots_dir = "plots"
    os.makedirs(plots_dir, exist_ok=True)

    for metric_col in metric_cols:
        plt.figure(figsize=(12,7))
        # Dynamically use all non-metric columns as label parts
        label_cols = [col for col in combined_df.columns if col not in metric_cols]
        labels = combined_df[label_cols].astype(str).agg(" | ".join, axis=1)
        plt.bar(labels, combined_df[metric_col], color='skyblue')
        plt.xticks(rotation=45, ha="right")
        plt.ylabel(metric_col)
        plt.title(f"Comparison of {metric_col} by {' | '.join(label_cols)} (All Results)")
        plt.tight_layout()

        # Save plot instead of just showing it
        outname = os.path.join(plots_dir, f"all_results_{metric_col}_by_service.png")
        plt.savefig(outname, dpi=300)
        plt.close()
        print(f"✅ Plot saved to {outname}")

if __name__ == "__main__":
    main()