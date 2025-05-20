# HYDRA Integration with ELK Stack

## Overview

This guide demonstrates how to integrate HYDRA with the ELK Stack (Elasticsearch, Logstash, Kibana), enabling organizations to:

1. **Send HYDRA simulation data to Elasticsearch** for storage and analysis
2. **Process and enrich HYDRA events with Logstash**
3. **Visualize security posture with Kibana dashboards**
4. **Evaluate detection rules** against simulated attacks
5. **Correlate simulation data** with production security events

## Benefits of Integration

Integrating HYDRA with ELK Stack provides several key benefits:

- **Enhanced Detection Validation**: Test Elasticsearch detection rules against HYDRA's simulated attacks
- **Advanced Analytics**: Apply Elasticsearch's powerful analytics to simulation data
- **Custom Visualizations**: Create tailored Kibana dashboards for security posture assessment
- **Unified Security Visibility**: Correlate simulated attacks with real-world security events
- **Open-Source Flexibility**: Leverage the extensibility of the ELK Stack

## Prerequisites

- HYDRA Enterprise Platform (v2.0+)
- Elasticsearch (v7.10+)
- Logstash (v7.10+)
- Kibana (v7.10+)
- Network connectivity between HYDRA and ELK environments

## Integration Architecture

![HYDRA-ELK Integration Architecture](../images/hydra_elk_integration.png)

The integration uses the following components:

1. **HYDRA Simulation Engine**: Generates attack simulations and defense responses
2. **HYDRA Integration Module**: Formats and forwards events to Logstash
3. **Logstash**: Processes, enriches, and forwards HYDRA events
4. **Elasticsearch**: Stores and indexes HYDRA simulation data
5. **Kibana**: Provides visualization and dashboard capabilities

## Configuration Steps

### 1. Configure Elasticsearch Index Template

Create an index template for HYDRA data to ensure proper field mapping:

```bash
PUT _index_template/hydra_simulations
{
  "index_patterns": ["hydra-simulations-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "simulation_id": { "type": "keyword" },
        "event_type": { "type": "keyword" },
        "attack_strategy": { "type": "keyword" },
        "attack_type": { "type": "keyword" },
        "source_node": { "type": "integer" },
        "target_node": { "type": "integer" },
        "target_type": { "type": "keyword" },
        "success": { "type": "boolean" },
        "details": {
          "properties": {
            "vulnerability": { "type": "keyword" },
            "severity": { "type": "float" },
            "exploitability": { "type": "float" },
            "detection_time": { "type": "float" },
            "response_time": { "type": "float" }
          }
        }
      }
    }
  }
}
```

### 2. Configure Logstash Pipeline

Create a Logstash pipeline configuration file (`hydra.conf`):

```
input {
  http {
    port => 8080
    codec => "json"
  }
}

filter {
  if [event_type] == "attack" {
    mutate {
      add_field => { "event_category" => "attack_simulation" }
    }
  }
  else if [event_type] == "defense" {
    mutate {
      add_field => { "event_category" => "defense_simulation" }
    }
  }
  else if [event_type] == "alert" {
    mutate {
      add_field => { "event_category" => "alert_simulation" }
    }
  }
  
  date {
    match => [ "timestamp", "ISO8601" ]
    target => "@timestamp"
    remove_field => [ "timestamp" ]
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "hydra-simulations-%{+YYYY.MM.dd}"
  }
}
```

### 3. Configure HYDRA Integration Module

1. Log in to HYDRA Administration Console
2. Navigate to Settings > Integrations > SIEM
3. Select "ELK Stack" from the integration options
4. Configure the following settings:
   - Logstash URL: `http://your-logstash-server:8080`
   - Authentication: Configure if required (Basic Auth, API Key, etc.)
   - Event Types: Select the event types to forward (attacks, defenses, alerts, etc.)
5. Click "Test Connection" to verify connectivity
6. Save the configuration

## Data Types and Examples

HYDRA sends the following event types to ELK Stack:

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

## Kibana Dashboards and Visualizations

### Import HYDRA Dashboards

HYDRA provides pre-built Kibana dashboards that can be imported:

1. In the HYDRA Administration Console, navigate to Integrations > ELK Stack > Dashboards
2. Click "Export Dashboards" to download the Kibana dashboard export file
3. In Kibana, navigate to Stack Management > Saved Objects
4. Click "Import" and select the downloaded file
5. Resolve any conflicts if prompted

### Example Visualizations

The HYDRA Kibana dashboards include:

#### Attack Success Rate

A pie chart showing the proportion of successful vs. failed attacks:

```
GET hydra-simulations-*/_search
{
  "size": 0,
  "query": {
    "term": {
      "event_type": "attack"
    }
  },
  "aggs": {
    "success_rate": {
      "terms": {
        "field": "success"
      }
    }
  }
}
```

#### Top Vulnerable Node Types

A bar chart showing which node types are most successfully attacked:

```
GET hydra-simulations-*/_search
{
  "size": 0,
  "query": {
    "bool": {
      "must": [
        { "term": { "event_type": "attack" } },
        { "term": { "success": true } }
      ]
    }
  },
  "aggs": {
    "vulnerable_nodes": {
      "terms": {
        "field": "target_type",
        "size": 10
      }
    }
  }
}
```

#### Defense Effectiveness Timeline

A line chart showing defense effectiveness over time:

```
GET hydra-simulations-*/_search
{
  "size": 0,
  "aggs": {
    "timeline": {
      "date_histogram": {
        "field": "@timestamp",
        "calendar_interval": "day"
      },
      "aggs": {
        "attacks": {
          "filter": {
            "term": {
              "event_type": "attack"
            }
          }
        },
        "successful_defenses": {
          "filter": {
            "bool": {
              "must": [
                { "term": { "event_type": "defense" } },
                { "term": { "success": true } }
              ]
            }
          }
        }
      }
    }
  }
}
```

## Advanced Integration: Detection Rule Testing

HYDRA can be used to test Elasticsearch detection rules:

1. Create detection rules in Elasticsearch Security:
   ```
   POST /_security/rule
   {
     "rule_id": "hydra-sql-injection-test",
     "risk_score": 75,
     "description": "Detects SQL injection attacks",
     "index": ["hydra-simulations-*", "logs-*"],
     "query": "event_type:attack AND attack_type:sql_injection"
   }
   ```

2. Run HYDRA simulations that include SQL injection attacks

3. Evaluate rule effectiveness in Kibana Security

4. Refine rules based on detection performance

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Verify network connectivity between HYDRA and Logstash
   - Check authentication configuration
   - Ensure Logstash HTTP input is properly configured

2. **Missing Events**
   - Verify Logstash pipeline configuration
   - Check Elasticsearch index patterns
   - Ensure events are within the time range

3. **Mapping Issues**
   - Review index template configuration
   - Check for field type conflicts
   - Verify field names match between systems

### Support Resources

- HYDRA Integration Documentation: [docs.hydra-security.ai/integrations/elk](https://docs.hydra-security.ai/integrations/elk)
- Elasticsearch Documentation: [www.elastic.co/guide/en/elasticsearch/reference/current/index.html](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- HYDRA Support Portal: [support.hydra-security.ai](https://support.hydra-security.ai)

## Conclusion

Integrating HYDRA with the ELK Stack creates a powerful platform for security validation, detection testing, and continuous improvement. By combining HYDRA's advanced attack simulation capabilities with ELK's analytics and visualization features, organizations can gain unprecedented visibility into their security posture and drive measurable security improvements.
