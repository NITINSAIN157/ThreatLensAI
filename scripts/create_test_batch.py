"""
Generates a small test batch CSV (250 rows) for live UI demonstration.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.generate_sample_data import generate_cicids2017_dataset

def main():
    dest = Path("data/raw/cicids2017_test_batch.csv")
    df = generate_cicids2017_dataset(n_samples=250, random_state=999)
    df.to_csv(dest, index=False)
    print(f"Generated test batch at {dest.resolve()} ({len(df)} rows)")

if __name__ == "__main__":
    main()
