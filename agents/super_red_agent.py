"""
Super Red Agent Module for HYDRA

This module implements a highly effective red agent with guaranteed success rates
for demonstration and blue team testing purposes.
"""

import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import json
import os
import time
from datetime import datetime
import networkx as nx

# Import attack framework
from agents.attack_framework import ATTCKTactic, ATTCKTechnique, TECHNIQUE_TO_VULNERABILITY

# Import components from enhanced red agent
from agents.enhanced_red_agent_new import EnhancedRedAgent, APT29Strategy, APT41Strategy, RansomwareStrategy
from agents.attack_planner import AttackPlanner, AttackGoal, AttackPhase
from agents.data_exfiltration import DataExfiltration, DataType, ExfiltrationType

class SuperRedAgent(EnhancedRedAgent):
    """
    Super Red Agent with guaranteed success rates for demonstration purposes.
    This agent is designed to effectively compromise networks and exfiltrate data
    to provide a challenging test for blue teams.
    """
    def __init__(self, env, skill_level=0.95, learning_rate=0.001, threat_intel_file=None):
        """Initialize the Super Red Agent with high skill level"""
        # Initialize with very high skill level
        super().__init__(env, skill_level, learning_rate, threat_intel_file)

        # Override with even higher skill level for guaranteed success
        self.skill_level = 0.99

        # Track all nodes in the network for comprehensive compromise
        self.all_nodes = list(self.env.graph.nodes())
        self.target_sequence = self._plan_optimal_attack_sequence()

        # Track data exfiltration progress
        self.exfiltrated_data_by_type = {}
        self.total_data_in_network = self._estimate_total_data()

        # Enhanced capabilities
        self.has_domain_admin = False
        self.backdoors_installed = set()
        self.network_mapped = False

        # Set campaign goal to data theft by default
        self.campaign_goal = "data_theft"
        self.attack_planner.set_campaign_goal(AttackGoal.DATA_THEFT)

        # Initialize zero-day exploits
        self.zero_day_exploits = {
            "zero_day_buffer_overflow": 0.99,
            "zero_day_remote_code_execution": 0.99,
            "zero_day_privilege_escalation": 0.99,
            "zero_day_authentication_bypass": 0.99
        }

        # Log initialization
        print(f"Super Red Agent initialized with skill level {self.skill_level}")
        print(f"Campaign goal: {self.campaign_goal}")
        print(f"Network size: {len(self.all_nodes)} nodes")

    def _plan_optimal_attack_sequence(self):
        """Plan the optimal sequence of nodes to attack for maximum impact"""
        # Get all nodes
        nodes = list(self.env.graph.nodes())

        # Identify high-value targets
        high_value_targets = []
        for node in nodes:
            node_data = self.env.graph.nodes[node]
            node_type = node_data.get('type', '')

            # Prioritize databases and servers
            if node_type in ['database', 'server', 'domain_controller']:
                high_value_targets.append((node, 3))  # Higher weight
            elif node_type in ['workstation', 'cloud_instance']:
                high_value_targets.append((node, 2))  # Medium weight
            else:
                high_value_targets.append((node, 1))  # Lower weight

        # Sort by priority (weight)
        high_value_targets.sort(key=lambda x: x[1], reverse=True)

        # Extract just the node IDs
        target_sequence = [node for node, _ in high_value_targets]

        # Ensure entry points are attacked first
        for entry in self.env.entry_points:
            if entry in target_sequence:
                target_sequence.remove(entry)
            target_sequence.insert(0, entry)

        return target_sequence

    def _estimate_total_data(self):
        """Estimate the total amount of data in the network by node type"""
        total_data = {}

        for node in self.all_nodes:
            node_data = self.env.graph.nodes[node]
            node_type = node_data.get('type', '')

            # Assign data amounts by node type
            if node_type == 'database':
                data_types = [DataType.PERSONAL_IDENTIFIABLE_INFO.value,
                             DataType.FINANCIAL.value,
                             DataType.CUSTOMER_DATA.value]
                for data_type in data_types:
                    if data_type not in total_data:
                        total_data[data_type] = 0
                    total_data[data_type] += random.randint(5000, 20000)  # KB

            elif node_type == 'server':
                data_types = [DataType.CONFIGURATION.value,
                             DataType.SOURCE_CODE.value,
                             DataType.AUTHENTICATION.value]
                for data_type in data_types:
                    if data_type not in total_data:
                        total_data[data_type] = 0
                    total_data[data_type] += random.randint(2000, 10000)  # KB

            elif node_type == 'workstation':
                data_types = [DataType.PERSONAL_IDENTIFIABLE_INFO.value,
                             DataType.INTELLECTUAL_PROPERTY.value]
                for data_type in data_types:
                    if data_type not in total_data:
                        total_data[data_type] = 0
                    total_data[data_type] += random.randint(500, 5000)  # KB

        return total_data

    def act(self):
        """
        Execute an attack action with guaranteed success.
        This method overrides the standard act method to ensure successful attacks.
        """
        # If we haven't compromised any nodes yet, start with an entry point
        if not self.compromised_nodes:
            target_node = self.env.entry_points[0]
            attack_type = self._select_guaranteed_attack_type(target_node)
            success, info = self._guaranteed_attack(target_node, attack_type)

            if success:
                self.current_position = target_node
                self.compromised_nodes.add(target_node)
                self.campaign_progress += 0.1

                # Record the attack
                attack_record = {
                    "strategy": "SuperRedAgent",
                    "target": target_node,
                    "attack_type": attack_type,
                    "success": success,
                    "detected": False,
                    "zero_day": True,
                    "info": info,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.attack_history.append(attack_record)

                return success, attack_record

        # If we have a current position, choose the next target strategically
        next_target = self._select_next_target()
        attack_type = self._select_guaranteed_attack_type(next_target)

        # Execute the attack with guaranteed success
        success, info = self._guaranteed_attack(next_target, attack_type)

        if success:
            previous_position = self.current_position
            self.current_position = next_target
            self.compromised_nodes.add(next_target)

            # Update campaign progress
            self.campaign_progress = min(1.0, self.campaign_progress + 0.05)

            # Perform data operations if appropriate
            if self.env.graph.nodes[next_target].get('type') in ['database', 'server', 'workstation']:
                self._perform_guaranteed_data_operations(next_target)

            # Track lateral movement
            if previous_position is not None and previous_position != next_target:
                self.lateral_movement_paths.append((previous_position, next_target))

            # Install backdoor for persistence
            self._install_backdoor(next_target)

        # Record the attack
        attack_record = {
            "strategy": "SuperRedAgent",
            "target": next_target,
            "attack_type": attack_type,
            "success": success,
            "detected": False,
            "zero_day": True,
            "info": info,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.attack_history.append(attack_record)

        return success, attack_record

    def _select_next_target(self):
        """Select the next target to attack based on strategic priorities"""
        # If we have a target sequence, use it
        for target in self.target_sequence:
            if target not in self.compromised_nodes:
                # Check if we can reach this target from current position
                if self._can_reach_target(target):
                    return target

        # If we've compromised all targets in our sequence or can't reach any,
        # find any uncompromised node we can reach
        for node in self.all_nodes:
            if node not in self.compromised_nodes and self._can_reach_target(node):
                return node

        # If all nodes are compromised or unreachable, return to an entry point
        return self.env.entry_points[0]

    def _can_reach_target(self, target):
        """Check if we can reach a target from current position"""
        if self.current_position is None:
            return target in self.env.entry_points

        try:
            path = nx.shortest_path(self.env.graph, self.current_position, target)
            # Check if all nodes in the path are compromised or the target itself
            for node in path[1:-1]:  # Skip current position and target
                if node not in self.compromised_nodes:
                    return False
            return True
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return False

    def _select_guaranteed_attack_type(self, target_node):
        """Select an attack type that is guaranteed to succeed"""
        if target_node not in self.env.graph:
            return "zero_day_remote_code_execution"

        # Check if the node has any vulnerabilities
        vulnerabilities = self.env.graph.nodes[target_node].get('vulnerabilities', [])

        if vulnerabilities:
            # Use an existing vulnerability if available
            return vulnerabilities[0]['type']
        else:
            # Use a zero-day exploit if no vulnerabilities are available
            return random.choice(list(self.zero_day_exploits.keys()))

    def _guaranteed_attack(self, target_node, attack_type):
        """Execute an attack with guaranteed success"""
        # If it's a zero-day, bypass the normal attack mechanism
        if attack_type in self.zero_day_exploits:
            # Add the node to compromised nodes
            self.env.compromised_nodes.add(target_node)

            # Log the attack
            node_type = self.env.graph.nodes[target_node].get('type', 'unknown') if target_node in self.env.graph else 'unknown'
            self.env.logs.append(f"Node {target_node} ({node_type}) compromised via {attack_type} zero-day exploit")

            # Create an alert with low probability (stealthy zero-day)
            if random.random() < 0.2:
                self.env.alerts.append({
                    "type": "compromise",
                    "node_id": target_node,
                    "attack_type": attack_type,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            return True, "Zero-day attack successful"

        # Otherwise use the environment's attack method but ensure success
        success, info = self.env.attack_node(target_node, attack_type, self.skill_level)

        # If the attack failed, force success
        if not success:
            # Add the node to compromised nodes
            self.env.compromised_nodes.add(target_node)

            # Log the forced success
            node_type = self.env.graph.nodes[target_node].get('type', 'unknown') if target_node in self.env.graph else 'unknown'
            self.env.logs.append(f"Node {target_node} ({node_type}) compromised via {attack_type} (forced success)")

            return True, "Attack successful (forced)"

        return success, info

    def _perform_guaranteed_data_operations(self, node_id):
        """Perform data collection and exfiltration with guaranteed success"""
        node_data = self.env.graph.nodes[node_id]
        node_type = node_data.get('type', '')

        # Determine what types of data might be available on this node
        available_data_types = []

        if node_type == 'database':
            available_data_types = [
                DataType.PERSONAL_IDENTIFIABLE_INFO.value,
                DataType.FINANCIAL.value,
                DataType.CUSTOMER_DATA.value,
                DataType.EMPLOYEE_DATA.value,
                DataType.AUTHENTICATION.value
            ]
        elif node_type == 'server':
            available_data_types = [
                DataType.CONFIGURATION.value,
                DataType.SYSTEM_LOGS.value,
                DataType.AUTHENTICATION.value,
                DataType.SOURCE_CODE.value
            ]
        elif node_type == 'workstation':
            available_data_types = [
                DataType.PERSONAL_IDENTIFIABLE_INFO.value,
                DataType.BUSINESS_PLANS.value,
                DataType.INTELLECTUAL_PROPERTY.value,
                DataType.SOURCE_CODE.value
            ]
        elif node_type == 'cloud_instance':
            available_data_types = [
                DataType.CONFIGURATION.value,
                DataType.SOURCE_CODE.value,
                DataType.CUSTOMER_DATA.value,
                DataType.SYSTEM_LOGS.value
            ]
        else:
            available_data_types = [
                DataType.CONFIGURATION.value,
                DataType.SYSTEM_LOGS.value
            ]

        # Collect all available data types
        collected_data_details = []
        total_size = 0

        for data_type in available_data_types:
            # Generate a realistic size for this data type
            min_size, max_size = 1000, 10000  # Default range in KB

            if data_type == DataType.PERSONAL_IDENTIFIABLE_INFO.value:
                min_size, max_size = 5000, 50000
            elif data_type == DataType.FINANCIAL.value:
                min_size, max_size = 2000, 20000
            elif data_type == DataType.CUSTOMER_DATA.value:
                min_size, max_size = 10000, 100000
            elif data_type == DataType.SOURCE_CODE.value:
                min_size, max_size = 5000, 30000

            size = random.randint(min_size, max_size)
            total_size += size

            collected_data_details.append({
                "type": data_type,
                "size": size,
                "sensitivity": self._get_data_sensitivity(data_type)
            })

            # Track in our data collection
            if node_id not in self.data_collected:
                self.data_collected[node_id] = []
            self.data_collected[node_id].append(data_type)

            # Update exfiltrated data tracking
            if data_type not in self.exfiltrated_data_by_type:
                self.exfiltrated_data_by_type[data_type] = 0
            self.exfiltrated_data_by_type[data_type] += size

        # Log the collection activity
        self.env.logs.append(f"Data collection detected on node {node_id} ({node_type}): {len(collected_data_details)} data types, {total_size} KB")

        # Exfiltrate the data with guaranteed success
        self._guaranteed_exfiltration(node_id, collected_data_details, total_size)

        return True

    def _guaranteed_exfiltration(self, source_node, data_details, total_size):
        """Exfiltrate data with guaranteed success"""
        # Select an exfiltration method based on node type
        node_type = self.env.graph.nodes[source_node].get('type', '')

        if node_type in ['server', 'cloud_instance']:
            method = ExfiltrationType.HTTPS_EXFILTRATION
        elif node_type == 'database':
            method = ExfiltrationType.ENCRYPTED_CHANNEL
        else:
            method = ExfiltrationType.DNS_TUNNELING

        # Create exfiltration record
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        exfil_record = {
            "timestamp": timestamp,
            "node_id": source_node,
            "method": method.value,
            "data": data_details,
            "total_size": total_size,
            "success": True,
            "detected": False
        }

        # Log the exfiltration
        self.env.logs.append(f"Data exfiltrated from node {source_node} using {method.value}: {total_size} KB")

        # Generate network traffic for the exfiltration (stealthy)
        self._generate_stealthy_exfil_traffic(source_node, method, total_size)

        # Update campaign progress
        self.campaign_progress = min(1.0, self.campaign_progress + 0.1)

        return exfil_record

    def _generate_stealthy_exfil_traffic(self, source_node, method, data_size):
        """Generate stealthy exfiltration traffic that evades detection"""
        # Select a destination (usually an entry point)
        if not self.env.entry_points:
            return

        destination = random.choice(self.env.entry_points)

        # Break into multiple small transfers to avoid detection
        max_packet_size = 50000  # 50KB max packet size for stealth
        num_packets = max(1, data_size // max_packet_size)

        for i in range(num_packets):
            packet_size = min(max_packet_size, data_size - (i * max_packet_size))
            if packet_size <= 0:
                break

            # Determine traffic type based on exfiltration method
            if method == ExfiltrationType.HTTPS_EXFILTRATION:
                traffic_type = "HTTPS"
                details = {
                    "method": "POST",
                    "path": f"/api/analytics/{random.randint(1000, 9999)}",
                    "host": f"analytics-{random.randint(100, 999)}.cloudfront.net",
                    "encrypted": True
                }
            elif method == ExfiltrationType.DNS_TUNNELING:
                traffic_type = "DNS"
                details = {
                    "query": f"data{random.randint(1000, 9999)}.{random.randint(1000, 9999)}.cloudns.com",
                    "record_type": "TXT"
                }
            elif method == ExfiltrationType.ENCRYPTED_CHANNEL:
                traffic_type = "TCP"
                details = {
                    "port": random.randint(10000, 65000),
                    "protocol": "Custom",
                    "encrypted": True
                }
            else:
                traffic_type = "HTTPS"
                details = {
                    "method": "GET",
                    "path": f"/images/{random.randint(1000, 9999)}.png",
                    "host": f"cdn-{random.randint(100, 999)}.cloudfront.net"
                }

            # Add packet-specific details
            details["part"] = f"{i+1}/{num_packets}"

            # Create traffic event (marked as malicious but very low detection chance)
            event = {
                "source": source_node,
                "destination": destination,
                "type": traffic_type,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "size": packet_size,
                "malicious": True,
                "details": details
            }

            self.env.traffic_logs.append(event)

            # Add delay between packets to avoid detection
            time.sleep(0.01)

    def _install_backdoor(self, node_id):
        """Install a backdoor on the compromised node for persistence"""
        if node_id in self.backdoors_installed:
            return False

        # Add to backdoors set
        self.backdoors_installed.add(node_id)

        # Log the backdoor installation (stealthily)
        if random.random() < 0.1:  # Only 10% chance of logging to avoid detection
            self.env.logs.append(f"Persistence mechanism deployed on node {node_id}")

        return True

    def _get_data_sensitivity(self, data_type):
        """Determine the sensitivity level of a data type (1-10)."""
        sensitivity_map = {
            DataType.PERSONAL_IDENTIFIABLE_INFO.value: 8,
            DataType.FINANCIAL.value: 9,
            DataType.INTELLECTUAL_PROPERTY.value: 10,
            DataType.AUTHENTICATION.value: 7,
            DataType.BUSINESS_PLANS.value: 8,
            DataType.CUSTOMER_DATA.value: 7,
            DataType.EMPLOYEE_DATA.value: 6,
            DataType.SOURCE_CODE.value: 9,
            DataType.CONFIGURATION.value: 5,
            DataType.SYSTEM_LOGS.value: 4
        }

        return sensitivity_map.get(data_type, 5)

    def get_campaign_status(self):
        """Get detailed status of the attack campaign with data exfiltration metrics"""
        # Calculate data exfiltration percentage
        total_exfiltrated = sum(self.exfiltrated_data_by_type.values())
        total_available = sum(self.total_data_in_network.values())
        exfil_percentage = total_exfiltrated / max(1, total_available)

        # Calculate network compromise percentage
        network_compromise = len(self.compromised_nodes) / max(1, len(self.all_nodes))

        return {
            "goal": self.campaign_goal,
            "progress": self.campaign_progress,
            "compromised_nodes": len(self.compromised_nodes),
            "total_nodes": len(self.all_nodes),
            "network_compromise_percentage": network_compromise * 100,
            "data_collected": len(self.data_collected),
            "data_exfiltrated_kb": total_exfiltrated,
            "data_exfiltration_percentage": exfil_percentage * 100,
            "lateral_movements": len(self.lateral_movement_paths),
            "backdoors_installed": len(self.backdoors_installed),
            "has_domain_admin": self.has_domain_admin,
            "exfiltrated_data_by_type": self.exfiltrated_data_by_type
        }
