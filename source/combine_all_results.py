import os
import glob

def combine_results_csvs():
    """
    Combine all CSV files in the parent directory that start with 'results_' into a single CSV file.
    The first row of each file is the header, but only the first file's header is kept.
    Output is written to 'all_results_combined.csv' in the parent directory.
    """
    import csv

    # Get parent directory of this script
    script_dir = os.path.abspath(os.path.dirname(__file__))
    parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

    # Find all results_*.csv files in the parent directory
    results_dir = os.path.join(parent_dir, "results")
    pattern = os.path.join(results_dir, "results_*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        print("No results_*.csv files found in results directory.")
        return

    # Save results to the 'results' subfolder in the parent directory

    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, "all_results_combined.csv")

    with open(output_path, "w", newline='', encoding="utf-8") as outfile:
        writer = None
        for idx, fname in enumerate(files):
            with open(fname, "r", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                if idx == 0 and (header := next(reader, None)):
                    # Write header from the first file
                    writer = csv.writer(outfile)
                    writer.writerow(header)
                else:
                    next(reader, None)  # Skip header for other files
                # Write data rows
                for row in reader:
                    if writer:
                        writer.writerow(row)
            print(f"Added {os.path.basename(fname)}")
    print(f"Combined {len(files)} files into {output_path}")

if __name__ == "__main__":
    combine_results_csvs()