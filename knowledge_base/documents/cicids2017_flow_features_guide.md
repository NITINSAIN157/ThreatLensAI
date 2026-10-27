# CIC-IDS2017 Network Flow Feature Guide & Diagnostic Interpretations

## Overview of Network Flow Records
In the CIC-IDS2017 benchmark dataset, network traffic is represented as bidirectional flow records aggregated across connection intervals. Key features and their diagnostic significance include:

### 1. Connection Duration & Rates
- Flow Duration: Total time (in microseconds) that a connection remained active.
  - Port scans typically exhibit extremely short flow durations (< 1,000 microseconds).
  - Normal web browsing and file transfers exhibit multi-second durations with varied inter-arrival times.
- Flow Packets/s: Number of packets transmitted per second of connection time.
  - Normal traffic rarely exceeds 1,000 - 5,000 packets/sec for individual flows.
  - Floods, DoS, and DDoS attacks drive packet rates above 50,000 - 500,000 packets/sec.
- Flow Bytes/s: Transfer rate in bytes per second. Discrepancies between high packet rates and low byte rates strongly signify tiny packet flooding.

### 2. Directionality & Packet Length Statistics
- Total Fwd Packets & Total Backward Packets:
  - Legitimate TCP connections maintain a balanced ratio between forward requests and backward responses.
  - Asymmetric flows where Total Backward Packets = 0 while Total Fwd Packets >= 1 indicates unanswered requests (SYN floods, port scanning, or unresponsive servers).
- Fwd Packet Length Mean vs Bwd Packet Length Mean:
  - HTTP requests are usually compact (100 - 500 bytes), while HTTP responses are larger (500 - 1,500 bytes).
  - DoS Hulk and Slowloris often use minimal forward packet lengths (0 - 64 bytes) to consume connection state tables without transmitting payload.

### 3. TCP Flags & Connection State
- SYN Flag Count: Number of packets with the Synchronize control flag enabled.
  - Normal flows contain 1-2 SYN packets during the initial 3-way handshake.
  - Spikes in SYN flags without subsequent ACK flags indicate SYN flood attacks or half-open TCP port scans.
- RST Flag Count: Number of Reset flags sent to forcibly terminate a socket.
  - High RST counts in short flows indicate closed ports responding to port scanning probes.
- ACK & PSH Flags: Push and Acknowledge flags. Normal interactive protocols (SSH, HTTP) frequently set PSH and ACK for immediate data processing.

### 4. Inter-Arrival Time (IAT)
- Flow IAT Mean & Flow IAT Std: Average and standard deviation of time between consecutive packets in a flow.
  - Automated attacks (bots, scripts, flood tools) exhibit low IAT variance and uniform intervals.
  - Human traffic exhibits high IAT variance due to unpredictable pauses and read times.
