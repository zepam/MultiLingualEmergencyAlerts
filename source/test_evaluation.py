import subprocess
import json
import os

def test_evaluation_script():
    # Run the evaluation script with the test files
    result = subprocess.run(
        [
            "python", "evaluation.py",
            "test_generated.json",
            "test_reference.json",
            "--output_csv", "test_results.csv"
        ],
        capture_output=True,
        text=True
    )
    # Check that the script ran successfully
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    # Check that the output CSV was created and is not empty
    assert os.path.exists("test_results.csv")
    with open("test_results.csv", "r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) > 1  # header + at least one result

if __name__ == "__main__":
    test_evaluation_script()
    print("Test passed!")
