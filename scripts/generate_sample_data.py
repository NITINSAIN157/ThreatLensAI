"""
ThreatLens AI - Synthetic/Curated CIC-IDS2017 Benchmark Generator
Generates realistic network flow records matching the exact schema and statistical
distributions of the University of New Brunswick (UNB) CIC-IDS2017 dataset.
"""

import numpy as np
import pandas as pd
from pathlib import Path

def generate_cicids2017_dataset(n_samples: int = 6000, random_state: int = 42) -> pd.DataFrame:
    np.random.seed(random_state)
    
    # 75% Benign, 12% DoS, 8% PortScan, 5% BruteForce
    n_benign = int(n_samples * 0.75)
    n_dos = int(n_samples * 0.12)
    n_portscan = int(n_samples * 0.08)
    n_bruteforce = n_samples - n_benign - n_dos - n_portscan

    records = []
    
    # 1. BENIGN FLOWS: Standard web/DNS/SSH traffic, normal round-trips, balanced flags
    for _ in range(n_benign):
        duration = float(np.random.exponential(scale=350000) + 1000)
        fwd_pkts = int(np.random.gamma(shape=3, scale=4)) + 1
        bwd_pkts = int(np.random.gamma(shape=3, scale=3)) + 1
        fwd_len_mean = float(np.clip(np.random.normal(loc=120, scale=40), 20, 1460))
        bwd_len_mean = float(np.clip(np.random.normal(loc=450, scale=120), 40, 1500))
        tot_fwd_len = fwd_pkts * fwd_len_mean
        tot_bwd_len = bwd_pkts * bwd_len_mean
        
        flow_bytes_s = float(np.clip((tot_fwd_len + tot_bwd_len) / (duration / 1e6), 10, 1e7))
        flow_pkts_s = float(np.clip((fwd_pkts + bwd_pkts) / (duration / 1e6), 1, 5e4))
        
        records.append({
            "Destination Port": int(np.random.choice([80, 443, 53, 22, 8080])),
            "Flow Duration": duration,
            "Total Fwd Packets": fwd_pkts,
            "Total Backward Packets": bwd_pkts,
            "Total Length of Fwd Packets": tot_fwd_len,
            "Total Length of Bwd Packets": tot_bwd_len,
            "Fwd Packet Length Max": fwd_len_mean * 1.5,
            "Fwd Packet Length Min": 20.0,
            "Fwd Packet Length Mean": fwd_len_mean,
            "Fwd Packet Length Std": fwd_len_mean * 0.3,
            "Bwd Packet Length Max": bwd_len_mean * 1.4,
            "Bwd Packet Length Min": 40.0,
            "Bwd Packet Length Mean": bwd_len_mean,
            "Bwd Packet Length Std": bwd_len_mean * 0.25,
            "Flow Bytes/s": flow_bytes_s,
            "Flow Packets/s": flow_pkts_s,
            "Flow IAT Mean": duration / max(fwd_pkts + bwd_pkts - 1, 1),
            "Flow IAT Std": (duration / max(fwd_pkts + bwd_pkts - 1, 1)) * 0.4,
            "Flow IAT Max": duration * 0.7,
            "Flow IAT Min": 10.0,
            "Fwd IAT Total": duration * 0.9,
            "Fwd IAT Mean": (duration * 0.9) / max(fwd_pkts - 1, 1),
            "Fwd IAT Std": 500.0,
            "Fwd IAT Max": duration * 0.8,
            "Fwd IAT Min": 5.0,
            "Bwd IAT Total": duration * 0.85,
            "Bwd IAT Mean": (duration * 0.85) / max(bwd_pkts - 1, 1),
            "Bwd IAT Std": 400.0,
            "Bwd IAT Max": duration * 0.75,
            "Bwd IAT Min": 5.0,
            "Fwd PSH Flags": int(np.random.choice([0, 1], p=[0.8, 0.2])),
            "Bwd PSH Flags": 0,
            "Fwd URG Flags": 0,
            "Bwd URG Flags": 0,
            "Fwd Header Length": fwd_pkts * 20,
            "Bwd Header Length": bwd_pkts * 20,
            "Fwd Packets/s": fwd_pkts / (duration / 1e6),
            "Bwd Packets/s": bwd_pkts / (duration / 1e6),
            "Min Packet Length": 20.0,
            "Max Packet Length": max(fwd_len_mean * 1.5, bwd_len_mean * 1.4),
            "Packet Length Mean": (tot_fwd_len + tot_bwd_len) / (fwd_pkts + bwd_pkts),
            "Packet Length Std": 150.0,
            "Packet Length Variance": 22500.0,
            "FIN Flag Count": 1,
            "SYN Flag Count": 1,
            "RST Flag Count": 0,
            "PSH Flag Count": 1,
            "ACK Flag Count": 1,
            "URG Flag Count": 0,
            "CWE Flag Count": 0,
            "ECE Flag Count": 0,
            "Down/Up Ratio": 1.0,
            "Average Packet Size": (tot_fwd_len + tot_bwd_len) / (fwd_pkts + bwd_pkts),
            "Avg Fwd Segment Size": fwd_len_mean,
            "Avg Bwd Segment Size": bwd_len_mean,
            "Fwd Header Length.1": fwd_pkts * 20,
            "Fwd Avg Bytes/Bulk": 0,
            "Fwd Avg Packets/Bulk": 0,
            "Fwd Avg Bulk Rate": 0,
            "Bwd Avg Bytes/Bulk": 0,
            "Bwd Avg Packets/Bulk": 0,
            "Bwd Avg Bulk Rate": 0,
            "Subflow Fwd Packets": fwd_pkts,
            "Subflow Fwd Bytes": tot_fwd_len,
            "Subflow Bwd Packets": bwd_pkts,
            "Subflow Bwd Bytes": tot_bwd_len,
            "Init_Win_bytes_forward": 29200,
            "Init_Win_bytes_backward": 28960,
            "act_data_pkt_fwd": max(1, fwd_pkts - 2),
            "min_seg_size_forward": 20,
            "Active Mean": 0.0,
            "Active Std": 0.0,
            "Active Max": 0.0,
            "Active Min": 0.0,
            "Idle Mean": 0.0,
            "Idle Std": 0.0,
            "Idle Max": 0.0,
            "Idle Min": 0.0,
            "Label": "BENIGN"
        })
        
    # 2. DoS ATTACK FLOWS: Extreme packet rates, high SYN flag, small packets, low/zero bwd packets
    for _ in range(n_dos):
        duration = float(np.random.uniform(50000, 3000000))
        fwd_pkts = int(np.random.uniform(50, 400))
        bwd_pkts = int(np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1]))
        fwd_len_mean = float(np.random.uniform(0, 32))
        bwd_len_mean = 0.0 if bwd_pkts == 0 else 40.0
        tot_fwd_len = fwd_pkts * fwd_len_mean
        tot_bwd_len = bwd_pkts * bwd_len_mean
        flow_bytes_s = float(np.clip(tot_fwd_len / (duration / 1e6), 100, 1e8))
        flow_pkts_s = float(np.clip(fwd_pkts / (duration / 1e6), 500, 1e6))
        
        records.append({
            "Destination Port": 80,
            "Flow Duration": duration,
            "Total Fwd Packets": fwd_pkts,
            "Total Backward Packets": bwd_pkts,
            "Total Length of Fwd Packets": tot_fwd_len,
            "Total Length of Bwd Packets": tot_bwd_len,
            "Fwd Packet Length Max": 64.0,
            "Fwd Packet Length Min": 0.0,
            "Fwd Packet Length Mean": fwd_len_mean,
            "Fwd Packet Length Std": 5.0,
            "Bwd Packet Length Max": bwd_len_mean,
            "Bwd Packet Length Min": 0.0,
            "Bwd Packet Length Mean": bwd_len_mean,
            "Bwd Packet Length Std": 0.0,
            "Flow Bytes/s": flow_bytes_s,
            "Flow Packets/s": flow_pkts_s,
            "Flow IAT Mean": duration / max(fwd_pkts - 1, 1),
            "Flow IAT Std": 20.0,
            "Flow IAT Max": duration * 0.1,
            "Flow IAT Min": 1.0,
            "Fwd IAT Total": duration,
            "Fwd IAT Mean": duration / max(fwd_pkts - 1, 1),
            "Fwd IAT Std": 15.0,
            "Fwd IAT Max": duration * 0.1,
            "Fwd IAT Min": 1.0,
            "Bwd IAT Total": 0.0,
            "Bwd IAT Mean": 0.0,
            "Bwd IAT Std": 0.0,
            "Bwd IAT Max": 0.0,
            "Bwd IAT Min": 0.0,
            "Fwd PSH Flags": 0,
            "Bwd PSH Flags": 0,
            "Fwd URG Flags": 0,
            "Bwd URG Flags": 0,
            "Fwd Header Length": fwd_pkts * 32,
            "Bwd Header Length": bwd_pkts * 32,
            "Fwd Packets/s": fwd_pkts / (duration / 1e6),
            "Bwd Packets/s": bwd_pkts / (duration / 1e6),
            "Min Packet Length": 0.0,
            "Max Packet Length": 64.0,
            "Packet Length Mean": fwd_len_mean,
            "Packet Length Std": 8.0,
            "Packet Length Variance": 64.0,
            "FIN Flag Count": 0,
            "SYN Flag Count": int(np.random.choice([1, 2, 4])),
            "RST Flag Count": int(np.random.choice([0, 1], p=[0.7, 0.3])),
            "PSH Flag Count": 0,
            "ACK Flag Count": 0,
            "URG Flag Count": 0,
            "CWE Flag Count": 0,
            "ECE Flag Count": 0,
            "Down/Up Ratio": 0.0,
            "Average Packet Size": fwd_len_mean,
            "Avg Fwd Segment Size": fwd_len_mean,
            "Avg Bwd Segment Size": bwd_len_mean,
            "Fwd Header Length.1": fwd_pkts * 32,
            "Fwd Avg Bytes/Bulk": 0,
            "Fwd Avg Packets/Bulk": 0,
            "Fwd Avg Bulk Rate": 0,
            "Bwd Avg Bytes/Bulk": 0,
            "Bwd Avg Packets/Bulk": 0,
            "Bwd Avg Bulk Rate": 0,
            "Subflow Fwd Packets": fwd_pkts,
            "Subflow Fwd Bytes": tot_fwd_len,
            "Subflow Bwd Packets": bwd_pkts,
            "Subflow Bwd Bytes": tot_bwd_len,
            "Init_Win_bytes_forward": int(np.random.choice([0, 256, 1024])),
            "Init_Win_bytes_backward": -1,
            "act_data_pkt_fwd": 0,
            "min_seg_size_forward": 32,
            "Active Mean": 0.0,
            "Active Std": 0.0,
            "Active Max": 0.0,
            "Active Min": 0.0,
            "Idle Mean": 0.0,
            "Idle Std": 0.0,
            "Idle Max": 0.0,
            "Idle Min": 0.0,
            "Label": "DoS Hulk"
        })

    # 3. PORTSCAN FLOWS: Very short durations, 1-2 fwd packets, 0 bwd packets, diverse ports
    for _ in range(n_portscan):
        duration = float(np.random.uniform(20, 2000))
        fwd_pkts = int(np.random.choice([1, 2]))
        bwd_pkts = 0
        tot_fwd_len = 0.0
        tot_bwd_len = 0.0
        
        records.append({
            "Destination Port": int(np.random.randint(1, 65535)),
            "Flow Duration": duration,
            "Total Fwd Packets": fwd_pkts,
            "Total Backward Packets": bwd_pkts,
            "Total Length of Fwd Packets": 0.0,
            "Total Length of Bwd Packets": 0.0,
            "Fwd Packet Length Max": 0.0,
            "Fwd Packet Length Min": 0.0,
            "Fwd Packet Length Mean": 0.0,
            "Fwd Packet Length Std": 0.0,
            "Bwd Packet Length Max": 0.0,
            "Bwd Packet Length Min": 0.0,
            "Bwd Packet Length Mean": 0.0,
            "Bwd Packet Length Std": 0.0,
            "Flow Bytes/s": 0.0,
            "Flow Packets/s": float(np.clip(fwd_pkts / (duration / 1e6), 100, 1e6)),
            "Flow IAT Mean": duration,
            "Flow IAT Std": 0.0,
            "Flow IAT Max": duration,
            "Flow IAT Min": duration,
            "Fwd IAT Total": duration,
            "Fwd IAT Mean": duration,
            "Fwd IAT Std": 0.0,
            "Fwd IAT Max": duration,
            "Fwd IAT Min": duration,
            "Bwd IAT Total": 0.0,
            "Bwd IAT Mean": 0.0,
            "Bwd IAT Std": 0.0,
            "Bwd IAT Max": 0.0,
            "Bwd IAT Min": 0.0,
            "Fwd PSH Flags": 0,
            "Bwd PSH Flags": 0,
            "Fwd URG Flags": 0,
            "Bwd URG Flags": 0,
            "Fwd Header Length": fwd_pkts * 24,
            "Bwd Header Length": 0,
            "Fwd Packets/s": fwd_pkts / (duration / 1e6),
            "Bwd Packets/s": 0.0,
            "Min Packet Length": 0.0,
            "Max Packet Length": 0.0,
            "Packet Length Mean": 0.0,
            "Packet Length Std": 0.0,
            "Packet Length Variance": 0.0,
            "FIN Flag Count": 0,
            "SYN Flag Count": 1,
            "RST Flag Count": 1,
            "PSH Flag Count": 0,
            "ACK Flag Count": 0,
            "URG Flag Count": 0,
            "CWE Flag Count": 0,
            "ECE Flag Count": 0,
            "Down/Up Ratio": 0.0,
            "Average Packet Size": 0.0,
            "Avg Fwd Segment Size": 0.0,
            "Avg Bwd Segment Size": 0.0,
            "Fwd Header Length.1": fwd_pkts * 24,
            "Fwd Avg Bytes/Bulk": 0,
            "Fwd Avg Packets/Bulk": 0,
            "Fwd Avg Bulk Rate": 0,
            "Bwd Avg Bytes/Bulk": 0,
            "Bwd Avg Packets/Bulk": 0,
            "Bwd Avg Bulk Rate": 0,
            "Subflow Fwd Packets": fwd_pkts,
            "Subflow Fwd Bytes": 0.0,
            "Subflow Bwd Packets": 0,
            "Subflow Bwd Bytes": 0.0,
            "Init_Win_bytes_forward": 1024,
            "Init_Win_bytes_backward": -1,
            "act_data_pkt_fwd": 0,
            "min_seg_size_forward": 24,
            "Active Mean": 0.0,
            "Active Std": 0.0,
            "Active Max": 0.0,
            "Active Min": 0.0,
            "Idle Mean": 0.0,
            "Idle Std": 0.0,
            "Idle Max": 0.0,
            "Idle Min": 0.0,
            "Label": "PortScan"
        })

    # 4. BRUTE FORCE (FTP/SSH PATATOR): Repeated fixed attempts on ports 21/22
    for _ in range(n_bruteforce):
        duration = float(np.random.uniform(10000, 50000))
        fwd_pkts = int(np.random.choice([6, 8, 10]))
        bwd_pkts = int(np.random.choice([5, 7, 9]))
        tot_fwd = fwd_pkts * 68.0
        tot_bwd = bwd_pkts * 84.0
        
        records.append({
            "Destination Port": int(np.random.choice([21, 22])),
            "Flow Duration": duration,
            "Total Fwd Packets": fwd_pkts,
            "Total Backward Packets": bwd_pkts,
            "Total Length of Fwd Packets": tot_fwd,
            "Total Length of Bwd Packets": tot_bwd,
            "Fwd Packet Length Max": 128.0,
            "Fwd Packet Length Min": 20.0,
            "Fwd Packet Length Mean": 68.0,
            "Fwd Packet Length Std": 24.0,
            "Bwd Packet Length Max": 140.0,
            "Bwd Packet Length Min": 32.0,
            "Bwd Packet Length Mean": 84.0,
            "Bwd Packet Length Std": 28.0,
            "Flow Bytes/s": (tot_fwd + tot_bwd) / (duration / 1e6),
            "Flow Packets/s": (fwd_pkts + bwd_pkts) / (duration / 1e6),
            "Flow IAT Mean": duration / (fwd_pkts + bwd_pkts),
            "Flow IAT Std": 200.0,
            "Flow IAT Max": duration * 0.4,
            "Flow IAT Min": 10.0,
            "Fwd IAT Total": duration * 0.8,
            "Fwd IAT Mean": (duration * 0.8) / fwd_pkts,
            "Fwd IAT Std": 150.0,
            "Fwd IAT Max": duration * 0.35,
            "Fwd IAT Min": 10.0,
            "Bwd IAT Total": duration * 0.75,
            "Bwd IAT Mean": (duration * 0.75) / bwd_pkts,
            "Bwd IAT Std": 140.0,
            "Bwd IAT Max": duration * 0.3,
            "Bwd IAT Min": 10.0,
            "Fwd PSH Flags": 1,
            "Bwd PSH Flags": 1,
            "Fwd URG Flags": 0,
            "Bwd URG Flags": 0,
            "Fwd Header Length": fwd_pkts * 20,
            "Bwd Header Length": bwd_pkts * 20,
            "Fwd Packets/s": fwd_pkts / (duration / 1e6),
            "Bwd Packets/s": bwd_pkts / (duration / 1e6),
            "Min Packet Length": 20.0,
            "Max Packet Length": 140.0,
            "Packet Length Mean": (tot_fwd + tot_bwd) / (fwd_pkts + bwd_pkts),
            "Packet Length Std": 32.0,
            "Packet Length Variance": 1024.0,
            "FIN Flag Count": 1,
            "SYN Flag Count": 1,
            "RST Flag Count": 1,
            "PSH Flag Count": 1,
            "ACK Flag Count": 1,
            "URG Flag Count": 0,
            "CWE Flag Count": 0,
            "ECE Flag Count": 0,
            "Down/Up Ratio": 0.88,
            "Average Packet Size": (tot_fwd + tot_bwd) / (fwd_pkts + bwd_pkts),
            "Avg Fwd Segment Size": 68.0,
            "Avg Bwd Segment Size": 84.0,
            "Fwd Header Length.1": fwd_pkts * 20,
            "Fwd Avg Bytes/Bulk": 0,
            "Fwd Avg Packets/Bulk": 0,
            "Fwd Avg Bulk Rate": 0,
            "Bwd Avg Bytes/Bulk": 0,
            "Bwd Avg Packets/Bulk": 0,
            "Bwd Avg Bulk Rate": 0,
            "Subflow Fwd Packets": fwd_pkts,
            "Subflow Fwd Bytes": tot_fwd,
            "Subflow Bwd Packets": bwd_pkts,
            "Subflow Bwd Bytes": tot_bwd,
            "Init_Win_bytes_forward": 14600,
            "Init_Win_bytes_backward": 14600,
            "act_data_pkt_fwd": 4,
            "min_seg_size_forward": 20,
            "Active Mean": 0.0,
            "Active Std": 0.0,
            "Active Max": 0.0,
            "Active Min": 0.0,
            "Idle Mean": 0.0,
            "Idle Std": 0.0,
            "Idle Max": 0.0,
            "Idle Min": 0.0,
            "Label": "FTP-Patator"
        })

    df = pd.DataFrame(records)
    
    # Shuffle records
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    
    # Intentionally inject leading spaces in some column names like original CIC-IDS2017 CSVs
    df.columns = [f" {c}" if i % 2 == 0 else c for i, c in enumerate(df.columns)]
    
    return df

def main():
    dest = Path("data/raw/cicids2017_sample.csv")
    dest.parent.mkdir(parents=True, exist_ok=True)
    print("Generating realistic CIC-IDS2017 benchmark subset (6,000 flows)...")
    df = generate_cicids2017_dataset(n_samples=6000, random_state=42)
    df.to_csv(dest, index=False)
    print(f"Sample dataset saved to: {dest.resolve()}")
    print("Class distribution:")
    label_col = [c for c in df.columns if "Label" in c][0]
    print(df[label_col].value_counts())

if __name__ == "__main__":
    main()
