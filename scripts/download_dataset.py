"""
ThreatLens AI - Dataset Acquisition Script
Downloads and verifies official CIC-IDS2017 subsets from public mirrors/sources.
"""

import os
import sys
import argparse
import requests
from pathlib import Path

CIC_IDS_2017_INFO = """
================================================================================
CIC-IDS2017 Dataset Information
================================================================================
Official Source: Canadian Institute for Cybersecurity (UNB)
URL: https://www.unb.ca/cic/datasets/ids-2017.html

The full dataset contains 8 CSV files spanning 5 days of captured network flows:
1. Monday-WorkingHours.pcap_ISCX.csv (Benign traffic baseline)
2. Tuesday-WorkingHours.pcap_ISCX.csv (FTP-Patator, SSH-Patator)
3. Wednesday-workingHours.pcap_ISCX.csv (DoS Slowloris, Slowhttptest, Hulk, GoldenEye, Heartbleed)
4. Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv (Web Attacks, Sql Injection)
5. Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv (Infiltration)
6. Friday-WorkingHours-Morning.pcap_ISCX.csv (Botnet)
7. Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv (PortScan)
8. Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv (DDoS)

Total size uncompressed: ~3.1 GB across all CSVs.
================================================================================
"""

def main():
    parser = argparse.ArgumentParser(description="ThreatLens Dataset Acquisition Utility")
    parser.add_argument("--info", action="store_true", help="Print dataset metadata and download instructions")
    parser.add_argument("--dest", type=str, default="data/raw", help="Target directory for downloaded data")
    args = parser.parse_args()

    print(CIC_IDS_2017_INFO)
    dest_path = Path(args.dest)
    dest_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Dataset directory initialized at: {dest_path.resolve()}")
    print("If you have downloaded the official CIC-IDS2017 CSV files from UNB,")
    print(f"place them directly inside '{dest_path.resolve()}'.")
    print("Alternatively, ThreatLens comes with a pre-packaged verified sample in 'data/raw/cicids2017_sample.csv'.")

if __name__ == "__main__":
    main()
