# MITRE ATT&CK - Network Adversary Tactics & Techniques

## T1046: Network Service Scanning
Adversaries may attempt to get a listing of services running on remote hosts, including those that may be vulnerable to remote software exploitation. Methods include:
- Port Scanning: Sending TCP SYN, ACK, or FIN packets across sequential or random destination ports to detect listening sockets.
- Behavioral Network Indicators:
  - High frequency of outbound connections to varied destination ports with very low flow duration (< 1000 microseconds).
  - Unidirectional traffic: Total Forward Packets typically 1-2, Total Backward Packets equal to 0.
  - RST (Reset) or SYN flags prominently set without completing the full 3-way TCP handshake.
- Investigation & Containment:
  1. Determine the source IP initiating the scans (internal compromised host or external scanning appliance).
  2. Inspect whether any scanned ports responded with SYN-ACK (indicating open/vulnerable services).
  3. Temporarily isolate the source host or apply edge firewall drop rules for the scanning IP.

## T1498: Network Denial of Service (DoS)
Adversaries may perform Network Denial of Service (DoS) attacks to degrade or block the availability of targeted resources to legitimate users.
- Sub-techniques:
  - T1498.001 Direct Network Flood: Volumetric flooding of target network interfaces with spoofed or automated high-rate packets.
  - T1498.002 Reflection Amplification: Leveraging misconfigured third-party UDP services (e.g., DNS, NTP) to reflect oversized payloads to the victim.
- Behavioral Network Indicators:
  - Abnormal spike in Flow Packets/s (often exceeding 50,000 packets/sec).
  - Disproportionate SYN Flag Count relative to completed TCP ACK handshakes.
  - Forward packet sizes are small (often 0-64 bytes) with minimal or zero backward packet return.
- Investigation & Mitigation:
  1. Identify whether attack traffic is concentrated on specific destination ports (e.g., Port 80 HTTP, Port 443 HTTPS).
  2. Implement rate limiting and SYN cookies on boundary firewalls / reverse proxies.
  3. Deploy upstream ISP scrubbing or Cloud DDoS mitigation if link saturation occurs.

## T1110: Brute Force Authentication
Adversaries may use brute force techniques to attempt credential guessing against network management services.
- Sub-techniques:
  - T1110.001 Password Guessing: Systematic attempts against service interfaces (FTP, SSH, RDP).
- Behavioral Network Indicators:
  - Repeated connections targeting specific management ports: Port 21 (FTP-Patator), Port 22 (SSH-Patator).
  - Consistent flow durations (10,000 - 50,000 microseconds) and uniform forward/backward packet counts (e.g., 6 forward, 5 backward per attempt).
  - High frequency of connection resets following failed authentication exchanges.
- Investigation & Containment:
  1. Check authentication server logs (e.g., /var/log/auth.log or Windows Security Event ID 4625).
  2. Enforce account lockout thresholds, IP throttling, and multi-factor authentication (MFA).
  3. Restrict management port access strictly to internal management VPNs / bastion hosts.

## T1071: Application Layer Command & Control (C2)
Adversaries may communicate with compromised hosts using application layer protocols (HTTP, HTTPS, DNS) to blend in with legitimate network traffic.
- Behavioral Network Indicators:
  - Periodic beaconing patterns evidenced by consistent Flow Inter-Arrival Times (Flow IAT Mean/Std) and predictable Idle times.
  - High ratio of outbound payload bytes to inbound response bytes.
