# HYDRA Integration with Splunk

## Overview

This guide demonstrates how to integrate HYDRA with Splunk, enabling organizations to:

1. **Send HYDRA simulation data to Splunk** for correlation with production security events
2. **Evaluate Splunk detection rules** against simulated attacks
3. **Create dashboards** that visualize security posture based on HYDRA findings
4. **Automate remediation workflows** based on HYDRA-identified vulnerabilities

## Benefits of Integration

Integrating HYDRA with Splunk provides several key benefits:

- **Enhanced Detection Validation**: Test Splunk detection rules against HYDRA's simulated attacks
- **Unified Security Visibility**: Correlate simulated attacks with real-world security events
- **Improved Incident Response**: Train SOC analysts using realistic attack scenarios
- **Automated Remediation**: Trigger automated workflows based on HYDRA findings
- **Comprehensive Reporting**: Generate executive-level reports on security posture

## Prerequisites

- HYDRA Enterprise Platform (v2.0+)
- Splunk Enterprise or Splunk Cloud (v8.0+)
- Splunk HTTP Event Collector (HEC) configured
- Network connectivity between HYDRA and Splunk environments

## Integration Architecture

![HYDRA-Splunk Integration Architecture](../images/hydra_splunk_integration.png)

The integration uses the following components:

1. **HYDRA Simulation Engine**: Generates attack simulations and defense responses
2. **HYDRA Integration Module**: Formats and forwards events to Splunk
3. **Splunk HTTP Event Collector**: Receives events from HYDRA
4. **Splunk Indexers**: Store and process HYDRA simulation data
5. **Splunk Search Head**: Provides search and visualization capabilities

## Configuration Steps

### 1. Configure Splunk HTTP Event Collector

1. Log in to Splunk as an administrator
2. Navigate to Settings > Data Inputs > HTTP Event Collector
3. Click "New Token"
4. Enter a name (e.g., "HYDRA Integration")
5. Select or create an index for HYDRA data (e.g., "hydra_simulations")
6. Complete the setup and note the generated token

### 2. Configure HYDRA Integration Module

1. Log in to HYDRA Administration Console
2. Navigate to Settings > Integrations > SIEM
3. Select "Splunk" from the integration options
4. Configure the following settings:
   - Splunk URL: `https://your-splunk-instance:8088/services/collector`
   - HEC Token: `your-hec-token`
   - Index: `hydra_simulations` (or your custom index)
   - Source Type: `hydra:simulation` (recommended)
   - Event Types: Select the event types to forward (attacks, defenses, alerts, etc.)
5. Click "Test Connection" to verify connectivity
6. Save the configuration

### 3. Configure Data Mapping

HYDRA events can be mapped to Splunk fields for better searchability:

1. In the HYDRA Administration Console, navigate to Settings > Integrations > Splunk > Data Mapping
2. Configure field mappings:
   - HYDRA Attack Type → attack_type
   - HYDRA Target Node → target_node
   - HYDRA Vulnerability → vulnerability
   - HYDRA Success Status → success
   - HYDRA Timestamp → time
3. Save the mapping configuration

## Data Types and Examples

HYDRA sends the following event types to Splunk:

### Attack Events

```json
{
  "event_type": "attack",
  "timestamp": "2025-05-20T13:45:22.123Z",
  "simulation_id": "sim-20250520-134522",
  "attack_strategy": "Targeted",
  "attack_type": "sql_injection",
  "source_node": 3,
  "target_node": 7,
  "target_type": "database",
  "success": true,
  "details": {
    "vulnerability": "unpatched_cve",
    "severity": 8.5,
    "exploitability": 0.7
  }
}
```

### Defense Events

```json
{
  "event_type": "defense",
  "timestamp": "2025-05-20T13:45:23.456Z",
  "simulation_id": "sim-20250520-134522",
  "defense_strategy": "Reactive",
  "action_type": "patch",
  "node_id": 7,
  "node_type": "database",
  "vulnerability_type": "sql_injection",
  "success": true,
  "details": {
    "detection_time": 1.2,
    "response_time": 3.5
  }
}
```

### Alert Events

```json
{
  "event_type": "alert",
  "timestamp": "2025-05-20T13:45:22.789Z",
  "simulation_id": "sim-20250520-134522",
  "alert_type": "compromise",
  "node_id": 7,
  "attack_type": "sql_injection",
  "severity": "high",
  "details": {
    "detection_source": "network_monitoring",
    "false_positive": false
  }
}
```

## Splunk Searches and Dashboards

### Example Searches

#### Find Successful Attacks

```
index=hydra_simulations sourcetype=hydra:simulation event_type=attack success=true 
| stats count by attack_type, target_type
| sort -count
```

#### Evaluate Defense Effectiveness

```
index=hydra_simulations sourcetype=hydra:simulation 
| stats count(eval(event_type="attack" AND success=true)) as successful_attacks, 
        count(eval(event_type="defense" AND success=true)) as successful_defenses 
        by simulation_id
| eval defense_effectiveness=round((successful_defenses/successful_attacks)*100,2)
| sort -defense_effectiveness
```

#### Detection Time Analysis

```
index=hydra_simulations sourcetype=hydra:simulation event_type=defense 
| stats avg(details.detection_time) as avg_detection_time, 
        max(details.detection_time) as max_detection_time, 
        min(details.detection_time) as min_detection_time 
        by defense_strategy
| sort avg_detection_time
```

### Example Dashboard

HYDRA provides a pre-built Splunk dashboard that can be imported:

1. In the HYDRA Administration Console, navigate to Integrations > Splunk > Dashboards
2. Click "Export Dashboard" to download the XML definition
3. In Splunk, navigate to Dashboards > Create New Dashboard
4. Click "Source" and paste the XML content
5. Save the dashboard

The dashboard includes:
- Attack success rate by type
- Defense effectiveness metrics
- Detection time analysis
- Critical vulnerability trends
- Attack path visualization

## Advanced Integration: Automated Remediation

HYDRA can trigger Splunk alerts that initiate automated remediation workflows:

1. In Splunk, create a saved search that identifies critical vulnerabilities:
   ```
   index=hydra_simulations sourcetype=hydra:simulation event_type=attack success=true 
   severity>7
   | dedup target_node, vulnerability
   ```

2. Configure an alert action to trigger a remediation workflow:
   - Use Splunk Phantom for orchestration
   - Use ServiceNow for ticket creation
   - Use custom scripts for specific remediation actions

3. Test the workflow with HYDRA simulations

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Verify network connectivity between HYDRA and Splunk
   - Check HEC token validity and permissions
   - Ensure HEC is enabled on the Splunk instance

2. **Missing Events**
   - Verify index and sourcetype configurations
   - Check event filtering settings in HYDRA
   - Ensure events are within Splunk's time range

3. **Field Mapping Issues**
   - Review data mapping configuration
   - Check for field extraction issues in Splunk
   - Verify field names match between systems

### Support Resources

- HYDRA Integration Documentation: [docs.hydra-security.ai/integrations/splunk](https://docs.hydra-security.ai/integrations/splunk)
- Splunk HTTP Event Collector Documentation: [docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)
- HYDRA Support Portal: [support.hydra-security.ai](https://support.hydra-security.ai)

## Conclusion

Integrating HYDRA with Splunk creates a powerful platform for security validation, detection testing, and continuous improvement. By combining HYDRA's advanced attack simulation capabilities with Splunk's analytics and visualization features, organizations can gain unprecedented visibility into their security posture and drive measurable security improvements.
