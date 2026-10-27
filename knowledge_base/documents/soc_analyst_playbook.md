# ThreatLens SOC Analyst Standard Operating Procedure (SOP)

## Operational Mission
ThreatLens AI assists Security Operations Center (SOC) analysts by detecting statistical anomalies in network flow records and providing grounded context. Analysts must apply this SOP when responding to alerts.

## Severity Levels & Triage SLAs
- CRITICAL (Model Score >= 0.70):
  - Action SLA: 15 minutes.
  - Characteristics: Multi-feature anomaly (extreme packet rates, SYN spikes, zero backward packets).
  - High probability of active DoS, heavy reconnaissance, or automated credential attack.
- SUSPICIOUS (Model Score 0.50 - 0.69):
  - Action SLA: 60 minutes.
  - Characteristics: Unbalanced flags, atypical ports, or elevated forward packet volume.
  - Requires correlation with host endpoint logs.
- ELEVATED (Model Score 0.30 - 0.49):
  - Action SLA: Routine monitoring / 24 hours.
  - Characteristics: Marginal statistical deviation from baseline; check for scheduled jobs or network backups.
- BENIGN (Model Score < 0.30):
  - Standard legitimate operational network traffic.

## Step-by-Step Analyst Workflow
1. Initial Validation:
   - Note the flagged Destination Port and the Top Contributing Features displayed by ThreatLens AI.
   - If Port = 80/443 and Flow Packets/s is abnormal, suspect HTTP DoS/DDoS.
   - If Destination Port spans ephemeral ranges (1024-65535) with zero backward packets, suspect PortScan (T1046).
   - If Port = 21/22 with repeated connections, suspect Patator Brute Force (T1110).
2. Host & Identity Correlation:
   - Query SIEM / EDR for the internal host associated with the connection.
   - Check if an authorized vulnerability assessment or penetration test is currently scheduled.
3. Containment Execution:
   - If external attack: Block source IP CIDR at perimeter firewall.
   - If internal compromised host: Quarantine endpoint via EDR agent and initiate host isolation.
4. Document & Escalate:
   - Log case details in ticketing system citing ThreatLens anomaly score, contributing flow features, and recommended playbook citations.
