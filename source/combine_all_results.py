import pandas as pd
import os
import glob # Import the glob module to find files based on a pattern

def combine_csv_files():
    """
    Combines all CSV files starting with 'results_' located in the parent directory
    (relative to where this script resides) into a single output file named
    'all_results_combined.csv'. This combined file will be saved within a 'results'
    subfolder, which is created inside the parent directory.

    The first row of the first processed file is used as the single header row.

    This script is designed to be run from the *parent directory* of this script's location.
    """
    # Get the directory where this script file is located (the subfolder)
    script_directory = os.path.abspath(os.path.dirname(__file__))

    # Calculate the path to the parent directory.
    # This is where your 'results_*.csv' files are and where the 'results' output folder will be created.
    parent_directory = os.path.abspath(os.path.join(script_directory, os.pardir))

    # Automatically find all CSV files that start with "results_" in the parent directory.
    file_pattern = os.path.join(parent_directory, 'results_*.csv')
    file_names = glob.glob(file_pattern)
    file_names.sort() # Sort the files to ensure consistent processing order

    # Define the path to the 'results' subfolder within the parent directory.
    # This is where the combined CSV will be saved.
    results_output_subfolder = os.path.join(parent_directory, 'results')

    # Create the 'results' output subfolder if it doesn't already exist.
    # os.makedirs creates all necessary intermediate directories.
    if not os.path.exists(results_output_subfolder):
        os.makedirs(results_output_subfolder)
        print(f"Created results output subfolder: '{results_output_subfolder}'")

    # Define the full path for the combined output CSV file.
    output_file_path = os.path.join(results_output_subfolder, 'all_results_combined.csv')

    if not file_names:
        print("No input CSV files found starting with 'results_' in the parent directory. Please ensure there are files to combine.")
        return

    print(f"Found {len(file_names)} CSV files to combine in the parent directory: {', '.join(os.path.basename(f) for f in file_names)}")

    # Process the first file: read it and write to the output file with its header
    try:
        first_df = pd.read_csv(file_names[0])
        first_df.to_csv(output_file_path, index=False, header=True)
        print(f"Successfully started combining files. The header from '{os.path.basename(file_names[0])}' has been used, and its data saved to '{os.path.basename(output_file_path)}' in the '{os.path.basename(results_output_subfolder)}' subfolder.")
    except pd.errors.EmptyDataError:
        print(f"Warning: The first file '{os.path.basename(file_names[0])}' is empty. Creating an empty output file with headers from the first file in the '{os.path.basename(results_output_subfolder)}' subfolder.")
        # If the first file is empty but has a header, capture just the header
        first_df = pd.read_csv(file_names[0], header=0, nrows=0)
        first_df.to_csv(output_file_path, index=False, header=True)
    except Exception as e:
        print(f"An error occurred while processing the first file '{os.path.basename(file_names[0])}': {e}")
        return

    # Loop through the remaining files (from the second one onwards) and append their data
    for file in file_names[1:]:
        try:
            df_to_append = pd.read_csv(file)
            # Append data to the output file. 'mode="a"' ensures append mode,
            # and 'header=False' prevents writing headers for subsequent files.
            df_to_append.to_csv(output_file_path, mode='a', index=False, header=False)
            print(f"Successfully appended data from '{os.path.basename(file)}' to '{os.path.basename(output_file_path)}'.")
        except pd.errors.EmptyDataError:
            print(f"Warning: Skipping empty file '{os.path.basename(file)}'. No data appended from it.")
        except Exception as e:
            print(f"An error occurred while appending data from '{os.path.basename(file)}': {e}")

    print(f"\nAll specified CSV files starting with 'results_' have been processed and combined into '{os.path.basename(output_file_path)}'.")
    print(f"You can find the combined data in the '{os.path.basename(results_output_subfolder)}' subfolder of the parent directory.")


# --- Example Usage ---
# Call the function to combine the found files. No arguments are needed now.
#combine_csv_files()

# Optional: Read and print the content of the combined file to verify
# try:
#     # Note: when reading back, specify the path to the combined file in the new 'results' subfolder
#     # We need to re-calculate parent_directory and results_output_subfolder
#     script_dir_for_read = os.path.abspath(os.path.dirname(__file__))
#     parent_dir_for_read = os.path.abspath(os.path.join(script_dir_for_read, os.pardir))
#     combined_file_path_for_read = os.path.join(parent_dir_for_read, 'results', 'all_results_combined.csv')
#     final_df = pd.read_csv(combined_file_path_for_read)
#     print("\n--- Content of the Combined CSV File ---")
#     print(final_df.to_string())
# except FileNotFoundError:
#     print(f"Error: The output file 'all_results_combined.csv' was not created in the 'results' subfolder.")
# except Exception as e:
#     print(f"Error reading the final combined file: {e}")
