import glob
import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_results_from_csvs(results_pattern="results_*.csv", output_dir="plots"):
    """
    Reads all CSV files matching the given pattern and generates bar plots for each metric in each file.

    Args:
        results_pattern (str): Glob pattern for results CSV files.
        output_dir (str): Directory to save the generated plots.

    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)
    csv_files = glob.glob(results_pattern)
    print(f"Looking for files with pattern: {results_pattern}")
    print(f"Found files: {csv_files}")
    if not csv_files:
        print("No results CSV files found.")
        return

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        # Assume the first column is a label (e.g., system, language, etc.)
        label_col = df.columns[0]
        metrics = df.columns[1:]

        for metric in metrics:
            plt.figure(figsize=(10, 6))
            plt.bar(df[label_col], df[metric], color='skyblue')
            plt.xlabel(label_col)
            plt.ylabel(metric)
            plt.title(f"{metric} - {os.path.basename(csv_file)}")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plot_filename = os.path.join(
                output_dir,
                f"{os.path.splitext(os.path.basename(csv_file))[0]}_{metric}.png"
            )
            plt.savefig(plot_filename)
            plt.close()
            print(f"Saved plot: {plot_filename}")

if __name__ == "__main__":
    plot_results_from_csvs()
