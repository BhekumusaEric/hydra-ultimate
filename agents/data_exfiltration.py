"""
Data Exfiltration Module for HYDRA

This module implements detailed simulation of data theft and exfiltration techniques
used by advanced threat actors. It models various exfiltration methods, data types,
and detection mechanisms.
"""

import random
import time
from datetime import datetime
from enum import Enum
import json
import math

class DataType(Enum):
    """Types of data that can be exfiltrated"""
    PERSONAL_IDENTIFIABLE_INFO = "pii"
    FINANCIAL = "financial"
    INTELLECTUAL_PROPERTY = "ip"
    AUTHENTICATION = "authentication"
    BUSINESS_PLANS = "business_plans"
    CUSTOMER_DATA = "customer_data"
    EMPLOYEE_DATA = "employee_data"
    SOURCE_CODE = "source_code"
    CONFIGURATION = "configuration"
    SYSTEM_LOGS = "system_logs"

class ExfiltrationType(Enum):
    """Methods of data exfiltration"""
    HTTP_EXFILTRATION = "http_exfiltration"
    HTTPS_EXFILTRATION = "https_exfiltration"
    DNS_TUNNELING = "dns_tunneling"
    SMTP_EXFILTRATION = "smtp_exfiltration"
    FTP_EXFILTRATION = "ftp_exfiltration"
    CUSTOM_PROTOCOL = "custom_protocol"
    STEGANOGRAPHY = "steganography"
    PHYSICAL_EXFILTRATION = "physical_exfiltration"
    CLOUD_STORAGE = "cloud_storage"
    ENCRYPTED_CHANNEL = "encrypted_channel"

class DataExfiltration:
    """
    Simulates data exfiltration techniques used by advanced threat actors.
    Models the collection, staging, and exfiltration of data from compromised systems.
    """
    def __init__(self, env, skill_level=0.7):
        self.env = env
        self.skill_level = skill_level
        self.collected_data = {}  # Map of node_id -> list of DataType
        self.staged_data = {}     # Map of node_id -> {data_type: size}
        self.exfiltrated_data = []  # List of successful exfiltration events
        self.detection_history = {}  # Track detection rates for different methods

        # Initialize detection probabilities for different exfiltration methods
        self.detection_probs = {
            ExfiltrationType.HTTP_EXFILTRATION: 0.6,
            ExfiltrationType.HTTPS_EXFILTRATION: 0.4,
            ExfiltrationType.DNS_TUNNELING: 0.5,
            ExfiltrationType.SMTP_EXFILTRATION: 0.7,
            ExfiltrationType.FTP_EXFILTRATION: 0.8,
            ExfiltrationType.CUSTOM_PROTOCOL: 0.3,
            ExfiltrationType.STEGANOGRAPHY: 0.2,
            ExfiltrationType.PHYSICAL_EXFILTRATION: 0.1,
            ExfiltrationType.CLOUD_STORAGE: 0.5,
            ExfiltrationType.ENCRYPTED_CHANNEL: 0.3
        }

        # Data sizes for different data types (in KB)
        self.data_sizes = {
            DataType.PERSONAL_IDENTIFIABLE_INFO: (100, 5000),
            DataType.FINANCIAL: (500, 10000),
            DataType.INTELLECTUAL_PROPERTY: (1000, 50000),
            DataType.AUTHENTICATION: (10, 1000),
            DataType.BUSINESS_PLANS: (500, 5000),
            DataType.CUSTOMER_DATA: (1000, 100000),
            DataType.EMPLOYEE_DATA: (500, 10000),
            DataType.SOURCE_CODE: (5000, 100000),
            DataType.CONFIGURATION: (100, 2000),
            DataType.SYSTEM_LOGS: (1000, 20000)
        }

    def collect_data(self, node_id):
        """
        Collect data from a compromised node based on node type.
        Returns a tuple of (success, data_types, total_size)
        """
        if node_id not in self.env.graph:
            return False, [], 0

        if node_id not in self.env.compromised_nodes:
            return False, [], 0

        node_data = self.env.graph.nodes[node_id]
        node_type = node_data.get('type', '')

        # Determine what types of data might be available on this node
        available_data_types = self._get_available_data_types(node_type)

        if not available_data_types:
            return False, [], 0

        # Collect a subset of available data based on skill level
        num_types_to_collect = max(1, int(len(available_data_types) * self.skill_level))
        collected_types = random.sample(available_data_types, min(num_types_to_collect, len(available_data_types)))

        # Calculate total size of collected data
        total_size = 0
        collected_data_details = []

        for data_type in collected_types:
            min_size, max_size = self.data_sizes[data_type]
            size = random.randint(min_size, max_size)
            total_size += size

            collected_data_details.append({
                "type": data_type.value,
                "size": size,
                "sensitivity": self._get_data_sensitivity(data_type)
            })

        # Store collected data
        if node_id not in self.collected_data:
            self.collected_data[node_id] = []

        self.collected_data[node_id].extend(collected_data_details)

        # Log the collection activity
        self.env.logs.append(f"Data collection detected on node {node_id} ({node_type}): {len(collected_types)} data types, {total_size} KB")

        # Generate an alert with some probability based on security controls
        security_controls = node_data.get('security_controls', [])
        detection_chance = 0.1  # Base chance

        if "Data Loss Prevention" in security_controls:
            detection_chance += 0.4
        if "File Integrity Monitoring" in security_controls:
            detection_chance += 0.3
        if "EDR" in security_controls:
            detection_chance += 0.2

        # Adjust based on skill level (higher skill = lower detection)
        detection_chance *= (1 - (self.skill_level * 0.5))

        if random.random() < detection_chance:
            self.env.alerts.append({
                "type": "data_collection",
                "node_id": node_id,
                "data_types": [d["type"] for d in collected_data_details],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            })

        return True, collected_data_details, total_size

    def stage_data(self, source_node_id, staging_node_id):
        """
        Stage collected data on a node in preparation for exfiltration.
        Returns a tuple of (success, staged_data_size)
        """
        if source_node_id not in self.collected_data:
            return False, 0

        if staging_node_id not in self.env.graph:
            return False, 0

        if staging_node_id not in self.env.compromised_nodes:
            return False, 0

        # Check if there's a path from source to staging node
        try:
            import networkx as nx
            path = nx.shortest_path(self.env.graph, source_node_id, staging_node_id)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return False, 0

        # Transfer the data
        if staging_node_id not in self.staged_data:
            self.staged_data[staging_node_id] = []

        # Move data from collected to staged
        staged_size = 0
        for data_item in self.collected_data[source_node_id]:
            # Create a copy with source information
            staged_item = data_item.copy()
            staged_item["source_node"] = source_node_id
            self.staged_data[staging_node_id].append(staged_item)
            staged_size += data_item["size"]

        # Clear collected data from source
        self.collected_data[source_node_id] = []

        # Log the staging activity
        self.env.logs.append(f"Data staged on node {staging_node_id} from node {source_node_id}: {staged_size} KB")

        # Generate traffic for the staging activity
        self._generate_staging_traffic(source_node_id, staging_node_id, staged_size)

        return True, staged_size

    def exfiltrate_data(self, node_id, method=None):
        """
        Exfiltrate staged data from a node using the specified method.
        If no method is specified, one will be selected based on the node's capabilities.
        Returns a tuple of (success, exfiltrated_data, detected)
        """
        if node_id not in self.staged_data or not self.staged_data[node_id]:
            return False, None, False

        if node_id not in self.env.compromised_nodes:
            return False, None, False

        # Select exfiltration method if not specified
        if method is None:
            method = self._select_exfiltration_method(node_id)

        # Calculate total size of staged data
        total_size = sum(item["size"] for item in self.staged_data[node_id])

        # Determine success probability based on method, skill level, and node security
        success_prob = self._calculate_exfiltration_success_prob(node_id, method)

        # Determine if exfiltration is successful
        success = random.random() < success_prob

        # Determine if exfiltration is detected
        detection_prob = self.detection_probs[method] * (1 - (self.skill_level * 0.5))
        detected = random.random() < detection_prob

        # Create exfiltration record
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        exfil_record = {
            "timestamp": timestamp,
            "node_id": node_id,
            "method": method.value,
            "data": self.staged_data[node_id],
            "total_size": total_size,
            "success": success,
            "detected": detected
        }

        if success:
            # Add to exfiltrated data history
            self.exfiltrated_data.append(exfil_record)

            # Clear staged data
            self.staged_data[node_id] = []

            # Log the exfiltration
            self.env.logs.append(f"Data exfiltrated from node {node_id} using {method.value}: {total_size} KB")

            # Generate network traffic for the exfiltration
            self._generate_exfiltration_traffic(node_id, method, total_size)
        else:
            # Log the failed attempt
            self.env.logs.append(f"Data exfiltration attempt failed from node {node_id} using {method.value}")

        # Generate an alert if detected
        if detected:
            self.env.alerts.append({
                "type": "data_exfiltration",
                "node_id": node_id,
                "method": method.value,
                "size": total_size,
                "timestamp": timestamp
            })

        # Update detection history for this method
        if method not in self.detection_history:
            self.detection_history[method] = []

        self.detection_history[method].append(detected)

        return success, exfil_record, detected

    def _get_available_data_types(self, node_type):
        """Determine what types of data might be available on a node based on its type."""
        available_types = []

        if node_type == 'database':
            available_types = [
                DataType.PERSONAL_IDENTIFIABLE_INFO,
                DataType.FINANCIAL,
                DataType.CUSTOMER_DATA,
                DataType.EMPLOYEE_DATA,
                DataType.AUTHENTICATION
            ]
        elif node_type == 'server':
            available_types = [
                DataType.CONFIGURATION,
                DataType.SYSTEM_LOGS,
                DataType.AUTHENTICATION,
                DataType.SOURCE_CODE
            ]
        elif node_type == 'workstation':
            available_types = [
                DataType.PERSONAL_IDENTIFIABLE_INFO,
                DataType.BUSINESS_PLANS,
                DataType.INTELLECTUAL_PROPERTY,
                DataType.SOURCE_CODE
            ]
        elif node_type == 'cloud_instance':
            available_types = [
                DataType.CONFIGURATION,
                DataType.SOURCE_CODE,
                DataType.CUSTOMER_DATA,
                DataType.SYSTEM_LOGS
            ]
        else:
            # Default for other node types
            available_types = [
                DataType.CONFIGURATION,
                DataType.SYSTEM_LOGS
            ]

        return available_types

    def _get_data_sensitivity(self, data_type):
        """Determine the sensitivity level of a data type (1-10)."""
        sensitivity_map = {
            DataType.PERSONAL_IDENTIFIABLE_INFO: 8,
            DataType.FINANCIAL: 9,
            DataType.INTELLECTUAL_PROPERTY: 10,
            DataType.AUTHENTICATION: 7,
            DataType.BUSINESS_PLANS: 8,
            DataType.CUSTOMER_DATA: 7,
            DataType.EMPLOYEE_DATA: 6,
            DataType.SOURCE_CODE: 9,
            DataType.CONFIGURATION: 5,
            DataType.SYSTEM_LOGS: 4
        }

        return sensitivity_map.get(data_type, 5)

    def _select_exfiltration_method(self, node_id):
        """Select an appropriate exfiltration method based on node capabilities."""
        node_data = self.env.graph.nodes[node_id]
        node_type = node_data.get('type', '')
        services = node_data.get('services', [])

        # Get available methods based on node services
        available_methods = []

        # Check for specific services
        service_names = [s.get('name', '').lower() for s in services]

        if any(s in ['http', 'https', 'web'] for s in service_names):
            available_methods.extend([ExfiltrationType.HTTP_EXFILTRATION, ExfiltrationType.HTTPS_EXFILTRATION])

        if any(s in ['dns'] for s in service_names):
            available_methods.append(ExfiltrationType.DNS_TUNNELING)

        if any(s in ['smtp', 'email'] for s in service_names):
            available_methods.append(ExfiltrationType.SMTP_EXFILTRATION)

        if any(s in ['ftp'] for s in service_names):
            available_methods.append(ExfiltrationType.FTP_EXFILTRATION)

        # Add general methods that don't depend on specific services
        available_methods.extend([
            ExfiltrationType.CUSTOM_PROTOCOL,
            ExfiltrationType.ENCRYPTED_CHANNEL
        ])

        # Add cloud storage for cloud instances
        if node_type == 'cloud_instance':
            available_methods.append(ExfiltrationType.CLOUD_STORAGE)

        # Add steganography as a rare option
        if random.random() < 0.2:
            available_methods.append(ExfiltrationType.STEGANOGRAPHY)

        # Add physical exfiltration as a very rare option
        if random.random() < 0.05:
            available_methods.append(ExfiltrationType.PHYSICAL_EXFILTRATION)

        # If we have detection history, prefer methods with lower detection rates
        if self.detection_history:
            methods_with_rates = []
            for method in available_methods:
                if method in self.detection_history and self.detection_history[method]:
                    # Calculate detection rate for this method
                    detection_rate = sum(self.detection_history[method]) / len(self.detection_history[method])
                    methods_with_rates.append((method, detection_rate))
                else:
                    # No history, use default rate
                    methods_with_rates.append((method, self.detection_probs[method]))

            # Sort by detection rate (lower is better)
            methods_with_rates.sort(key=lambda x: x[1])

            # Select method with preference for lower detection rates
            # but with some randomness to avoid being too predictable
            if random.random() < self.skill_level:
                # High skill attackers choose more optimally
                return methods_with_rates[0][0]
            else:
                # Lower skill attackers might not choose the best method
                top_n = max(1, int(len(methods_with_rates) * 0.5))
                return random.choice(methods_with_rates[:top_n])[0]

        # If no history or not using it, just pick randomly from available methods
        if not available_methods:
            # Default fallback
            return random.choice([
                ExfiltrationType.HTTP_EXFILTRATION,
                ExfiltrationType.HTTPS_EXFILTRATION,
                ExfiltrationType.DNS_TUNNELING
            ])

        return random.choice(available_methods)

    def _calculate_exfiltration_success_prob(self, node_id, method):
        """Calculate the probability of successful exfiltration."""
        node_data = self.env.graph.nodes[node_id]
        security_controls = node_data.get('security_controls', [])

        # Base success probability
        base_prob = 0.7

        # Adjust based on method
        method_factors = {
            ExfiltrationType.HTTP_EXFILTRATION: 0.8,  # Fairly reliable but easily detected
            ExfiltrationType.HTTPS_EXFILTRATION: 0.9,  # More reliable and harder to detect
            ExfiltrationType.DNS_TUNNELING: 0.7,  # Less reliable but often overlooked
            ExfiltrationType.SMTP_EXFILTRATION: 0.6,  # Often monitored
            ExfiltrationType.FTP_EXFILTRATION: 0.5,  # Very obvious
            ExfiltrationType.CUSTOM_PROTOCOL: 0.8,  # Custom protocols can be effective
            ExfiltrationType.STEGANOGRAPHY: 0.9,  # Very hard to detect
            ExfiltrationType.PHYSICAL_EXFILTRATION: 0.95,  # Almost guaranteed if possible
            ExfiltrationType.CLOUD_STORAGE: 0.8,  # Reliable but might be monitored
            ExfiltrationType.ENCRYPTED_CHANNEL: 0.85  # Reliable and hard to inspect
        }

        base_prob *= method_factors.get(method, 1.0)

        # Adjust based on security controls
        control_penalty = 0.0

        if "Data Loss Prevention" in security_controls:
            control_penalty += 0.3
        if "Network Monitoring" in security_controls:
            control_penalty += 0.2
        if "Intrusion Detection" in security_controls:
            control_penalty += 0.15
        if "Packet Inspection" in security_controls:
            control_penalty += 0.25

        # Some methods are less affected by certain controls
        if method == ExfiltrationType.ENCRYPTED_CHANNEL and "Packet Inspection" in security_controls:
            control_penalty -= 0.15  # Encryption helps bypass inspection

        if method == ExfiltrationType.STEGANOGRAPHY and "Data Loss Prevention" in security_controls:
            control_penalty -= 0.2  # Steganography can bypass DLP

        if method == ExfiltrationType.DNS_TUNNELING and "Network Monitoring" in security_controls:
            control_penalty -= 0.1  # DNS tunneling can be subtle

        # Apply control penalty
        base_prob *= (1.0 - min(control_penalty, 0.9))

        # Adjust based on skill level
        base_prob *= (0.5 + (self.skill_level * 0.5))

        # Ensure probability is in valid range
        return max(0.1, min(base_prob, 0.95))

    def _generate_staging_traffic(self, source_node, target_node, data_size):
        """Generate network traffic events for data staging."""
        # Convert KB to bytes for traffic size
        traffic_size = data_size * 1024

        # Break into multiple transfers if large
        max_packet_size = 1000000  # 1MB max packet size
        num_packets = math.ceil(traffic_size / max_packet_size)

        for i in range(num_packets):
            packet_size = min(max_packet_size, traffic_size - (i * max_packet_size))

            # Create traffic event
            event = {
                "source": source_node,
                "destination": target_node,
                "type": "File Transfer",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "size": packet_size,
                "malicious": True,
                "details": {
                    "protocol": "SMB" if random.random() < 0.7 else "FTP",
                    "operation": "WRITE",
                    "part": f"{i+1}/{num_packets}"
                }
            }

            self.env.traffic_logs.append(event)

    def _generate_exfiltration_traffic(self, source_node, method, data_size):
        """Generate network traffic events for data exfiltration."""
        # Convert KB to bytes for traffic size
        traffic_size = data_size * 1024

        # Determine destination (usually external)
        # In a real network, this would be an external IP or domain
        destination = random.choice(self.env.entry_points)

        # Traffic type and details based on exfiltration method
        traffic_type = "HTTP"
        details = {}

        if method == ExfiltrationType.HTTP_EXFILTRATION:
            traffic_type = "HTTP"
            details = {
                "method": "POST",
                "path": f"/api/data/{random.randint(1000, 9999)}",
                "host": f"data-{random.randint(100, 999)}.example.com"
            }
        elif method == ExfiltrationType.HTTPS_EXFILTRATION:
            traffic_type = "HTTPS"
            details = {
                "method": "POST",
                "path": f"/upload/{random.randint(1000, 9999)}",
                "host": f"secure-{random.randint(100, 999)}.example.com"
            }
        elif method == ExfiltrationType.DNS_TUNNELING:
            traffic_type = "DNS"
            details = {
                "query": f"data{random.randint(1000, 9999)}.exfil.example.com",
                "record_type": "TXT"
            }
        elif method == ExfiltrationType.SMTP_EXFILTRATION:
            traffic_type = "SMTP"
            details = {
                "to": f"drop{random.randint(100, 999)}@example.com",
                "subject": f"Data Package {random.randint(1000, 9999)}",
                "attachments": random.randint(1, 5)
            }
        elif method == ExfiltrationType.FTP_EXFILTRATION:
            traffic_type = "FTP"
            details = {
                "operation": "STOR",
                "filename": f"data_{random.randint(1000, 9999)}.zip"
            }
        elif method == ExfiltrationType.CLOUD_STORAGE:
            traffic_type = "HTTPS"
            details = {
                "method": "PUT",
                "path": f"/storage/v1/b/bucket-{random.randint(100, 999)}/o",
                "host": "storage.googleapis.com"
            }
        else:
            # Generic for other methods
            traffic_type = "TCP"
            details = {
                "port": random.randint(10000, 65000),
                "protocol": "Custom"
            }

        # Break into multiple transfers if large
        max_packet_size = 500000  # 500KB max packet size for exfiltration (smaller to avoid detection)
        num_packets = math.ceil(traffic_size / max_packet_size)

        for i in range(num_packets):
            packet_size = min(max_packet_size, traffic_size - (i * max_packet_size))

            # Add packet-specific details
            packet_details = details.copy()
            packet_details["part"] = f"{i+1}/{num_packets}"

            # Create traffic event
            event = {
                "source": source_node,
                "destination": destination,
                "type": traffic_type,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "size": packet_size,
                "malicious": True,
                "details": packet_details
            }

            self.env.traffic_logs.append(event)

    def get_exfiltration_summary(self):
        """Get a summary of all exfiltration activities."""
        if not self.exfiltrated_data:
            return {
                "total_exfiltration_events": 0,
                "total_data_exfiltrated": 0,
                "detected_events": 0,
                "detection_rate": 0,
                "data_types": {}
            }

        # Calculate summary statistics
        total_events = len(self.exfiltrated_data)
        detected_events = sum(1 for e in self.exfiltrated_data if e["detected"])
        detection_rate = detected_events / total_events if total_events > 0 else 0

        # Calculate total data exfiltrated
        total_data = sum(e["total_size"] for e in self.exfiltrated_data)

        # Count data types
        data_types = {}
        for event in self.exfiltrated_data:
            for data_item in event["data"]:
                data_type = data_item["type"]
                if data_type not in data_types:
                    data_types[data_type] = 0
                data_types[data_type] += data_item["size"]

        return {
            "total_exfiltration_events": total_events,
            "total_data_exfiltrated": total_data,
            "detected_events": detected_events,
            "detection_rate": detection_rate,
            "data_types": data_types
        }
