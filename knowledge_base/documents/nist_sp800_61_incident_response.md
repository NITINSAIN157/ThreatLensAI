# NIST SP 800-61 Rev. 2: Incident Handling Guide for Network Security

## 1. Preparation Phase
Preparation establishes the operational baseline and defensive toolsets needed to quickly respond to network anomalies.
- Baseline Network Traffic: Document standard utilization patterns, peak hours, expected packet transfer rates, and authorized protocols per network subnet.
- Security Sensor Coverage: Deploy network flow collectors (NetFlow, IPFIX, CICFlowMeter) and intrusion detection sensors at key ingress/egress points.

## 2. Detection and Analysis Phase (Triage)
When an anomaly detection system flags suspicious network flows, analysts must perform systematic verification:
- Validate Anomaly Context: A high anomaly score flags statistical deviations from normal traffic; it does NOT constitute conclusive proof of an actual compromise.
- Correlate Network Signals:
  - Check source and destination IP addresses, destination port numbers, and connection duration.
  - Evaluate flow directionality: Unidirectional flows with high SYN flags indicate reconnaissance or DoS.
  - Cross-examine with host telemetry: Check authentication audit logs, process creation trees, and DNS query logs for the involved internal endpoints.
- Prioritization: Determine severity based on critical asset exposure (e.g., database tier vs. test environment) and attack scale.

## 3. Containment, Eradication, and Recovery
Containment prevents an incident from spreading before resolution.
- Short-Term Containment:
  - Apply dynamic firewall drop rules or ACLs for verified malicious external IPs.
  - Implement network segmentation or VLAN quarantine for compromised internal hosts.
  - Apply rate limiting or traffic shaping at upstream perimeter routers to mitigate volumetric flood impacts.
- Eradication:
  - Terminate unauthorized active sessions and purge malicious backdoors/scripts.
  - Close unused destination ports and terminate unencrypted legacy services (e.g., standard Telnet or cleartext FTP).
- Recovery:
  - Restore affected systems from clean, verified backups.
  - Validate baseline operation before returning host interfaces to general production networks.

## 4. Post-Incident Activity
- Documentation: Record the incident timeline, root cause, flow metrics, containment efficacy, and total downtime.
- Model & Rule Tuning: If an alert was a false positive (e.g., authorized automated vulnerability scanner or backup job), update detection exclusion lists and retune model decision thresholds.
