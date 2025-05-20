# HYDRA Integration with ServiceNow

## Overview

This guide demonstrates how to integrate HYDRA with ServiceNow, enabling organizations to:

1. **Automate vulnerability management workflows** based on HYDRA findings
2. **Create and track remediation tickets** for identified security issues
3. **Integrate security validation** into IT service management processes
4. **Provide visibility** into security posture through ServiceNow dashboards
5. **Measure and report** on security improvement metrics

## Benefits of Integration

Integrating HYDRA with ServiceNow provides several key benefits:

- **Streamlined Remediation**: Automatically create tickets for vulnerabilities identified by HYDRA
- **Closed-Loop Validation**: Verify that remediated issues are actually fixed
- **Enhanced Visibility**: Provide security posture visibility to IT and business stakeholders
- **Improved Accountability**: Track remediation progress and SLA compliance
- **Unified Workflow**: Integrate security validation into existing IT service management processes

## Prerequisites

- HYDRA Enterprise Platform (v2.0+)
- ServiceNow Instance (Tokyo, San Diego, or Rome release)
- ServiceNow Security Operations or Vulnerability Response module (recommended)
- ServiceNow admin account with API access
- Network connectivity between HYDRA and ServiceNow

## Integration Architecture

![HYDRA-ServiceNow Integration Architecture](../images/hydra_servicenow_integration.png)

The integration uses the following components:

1. **HYDRA Simulation Engine**: Generates attack simulations and identifies vulnerabilities
2. **HYDRA Integration Module**: Formats and forwards findings to ServiceNow
3. **ServiceNow REST API**: Receives vulnerability data from HYDRA
4. **ServiceNow Workflow Engine**: Processes vulnerabilities according to defined workflows
5. **ServiceNow Security Operations/Vulnerability Response**: Manages the vulnerability lifecycle

## Configuration Steps

### 1. Configure ServiceNow REST API Access

1. Log in to ServiceNow as an administrator
2. Create a dedicated service account for HYDRA integration:
   - Navigate to User Administration > Users
   - Create a new user (e.g., "hydra-integration")
   - Assign appropriate roles (e.g., "vulnerability_response_admin", "security_admin")
3. Create an OAuth API endpoint for secure communication:
   - Navigate to System OAuth > Application Registry
   - Click "New" and select "Create an OAuth API endpoint for external clients"
   - Name: "HYDRA Integration"
   - Client ID: Generate or specify a client ID
   - Client Secret: Generate and securely store the client secret
   - Redirect URL: Leave blank for machine-to-machine integration
   - Active: Check this box
4. Configure access control:
   - Navigate to System OAuth > Application Registry
   - Open the newly created application
   - Click "Add OAuth Scope" and add required scopes (e.g., "vulnerability_response.write", "security_incident.write")

### 2. Configure HYDRA Integration Module

1. Log in to HYDRA Administration Console
2. Navigate to Settings > Integrations > ITSM
3. Select "ServiceNow" from the integration options
4. Configure the following settings:
   - ServiceNow Instance URL: `https://your-instance.service-now.com`
   - Authentication Method: "OAuth"
   - Client ID: Enter the client ID from ServiceNow
   - Client Secret: Enter the client secret from ServiceNow
   - Integration Mode: Select "Security Operations" or "Vulnerability Response" based on your ServiceNow modules
5. Click "Test Connection" to verify connectivity
6. Save the configuration

### 3. Configure Vulnerability Mapping

Map HYDRA vulnerability findings to ServiceNow fields:

1. In the HYDRA Administration Console, navigate to Settings > Integrations > ServiceNow > Field Mapping
2. Configure field mappings:
   - HYDRA Vulnerability Type → vulnerability.type
   - HYDRA Severity → vulnerability.risk_score
   - HYDRA Target Node → vulnerability.affected_system
   - HYDRA Attack Vector → vulnerability.attack_vector
   - HYDRA Simulation ID → vulnerability.source_id
3. Save the mapping configuration

### 4. Configure ServiceNow Workflows

Configure ServiceNow workflows to process HYDRA vulnerabilities:

1. Navigate to Security Operations > Administration > Vulnerability Response > Rules
2. Create a new rule for HYDRA vulnerabilities:
   - Name: "HYDRA Vulnerability Processing"
   - Condition: Source = "HYDRA"
   - Actions:
     - Set Assignment Group based on vulnerability type
     - Set Priority based on risk score
     - Set SLA based on severity
3. Activate the rule

## Data Types and Examples

HYDRA sends the following data to ServiceNow:

### Vulnerability Records

```json
{
  "source": "HYDRA",
  "type": "sql_injection",
  "risk_score": 85,
  "affected_system": "db-server-01",
  "attack_vector": "web_application",
  "description": "SQL Injection vulnerability in customer portal allows unauthorized database access",
  "remediation_steps": "Update web application framework to latest version and implement prepared statements",
  "simulation_details": {
    "simulation_id": "sim-20250520-134522",
    "attack_strategy": "Targeted",
    "success": true,
    "timestamp": "2025-05-20T13:45:22.123Z"
  }
}
```

### Security Incidents

```json
{
  "source": "HYDRA",
  "category": "attack_simulation",
  "subcategory": "data_breach",
  "short_description": "Simulated data breach via SQL Injection",
  "description": "HYDRA simulation detected successful data exfiltration through SQL Injection vulnerability in customer portal",
  "priority": 1,
  "affected_systems": ["db-server-01", "web-server-03"],
  "simulation_details": {
    "simulation_id": "sim-20250520-134522",
    "attack_path": "web-server-03 -> app-server-02 -> db-server-01",
    "data_compromised": "customer_records",
    "timestamp": "2025-05-20T13:45:22.123Z"
  }
}
```

## ServiceNow Dashboards and Reporting

### Import HYDRA Dashboards

HYDRA provides pre-built ServiceNow dashboards that can be imported:

1. In the HYDRA Administration Console, navigate to Integrations > ServiceNow > Dashboards
2. Click "Export Dashboards" to download the ServiceNow dashboard XML
3. In ServiceNow, navigate to Performance Analytics > Dashboards
4. Click "Import" and select the downloaded XML file

### Example Reports

The HYDRA ServiceNow integration enables several valuable reports:

#### Vulnerability Remediation Performance

- Average time to remediate HYDRA-identified vulnerabilities
- Remediation SLA compliance rate
- Vulnerability backlog trend
- Remediation by team/assignment group

#### Security Posture Improvement

- Reduction in critical vulnerabilities over time
- Improvement in attack simulation success rate
- Security control effectiveness trends
- Risk score reduction by system/application

## Advanced Integration: Closed-Loop Validation

HYDRA can perform closed-loop validation of remediated vulnerabilities:

1. When a vulnerability ticket is closed in ServiceNow, a webhook triggers a notification to HYDRA
2. HYDRA automatically schedules a targeted simulation to verify the vulnerability is fixed
3. Results are sent back to ServiceNow:
   - If fixed: The ticket remains closed with validation evidence attached
   - If not fixed: The ticket is reopened with new evidence

To configure closed-loop validation:

1. In ServiceNow, create a webhook that triggers when vulnerability tickets are closed:
   - Navigate to System Web Services > Outbound > REST Message
   - Create a new REST Message pointing to HYDRA's validation API
   - Configure the message to include ticket details

2. In HYDRA, configure the validation response:
   - Navigate to Settings > Integrations > ServiceNow > Closed-Loop Validation
   - Enable the feature
   - Configure validation parameters (retry attempts, validation criteria, etc.)

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Verify OAuth client ID and secret
   - Check service account permissions
   - Ensure OAuth scopes are properly configured

2. **Missing Tickets**
   - Verify field mappings
   - Check ServiceNow inbound email filters
   - Ensure the integration user has ticket creation permissions

3. **Workflow Issues**
   - Review ServiceNow workflow rules
   - Check for required fields that may be missing
   - Verify assignment group configurations

### Support Resources

- HYDRA Integration Documentation: [docs.hydra-security.ai/integrations/servicenow](https://docs.hydra-security.ai/integrations/servicenow)
- ServiceNow API Documentation: [developer.servicenow.com/dev.do](https://developer.servicenow.com/dev.do)
- HYDRA Support Portal: [support.hydra-security.ai](https://support.hydra-security.ai)

## Conclusion

Integrating HYDRA with ServiceNow creates a powerful platform for security validation and remediation management. By combining HYDRA's advanced attack simulation capabilities with ServiceNow's workflow and ticketing features, organizations can streamline vulnerability management, improve remediation effectiveness, and drive measurable security improvements.
