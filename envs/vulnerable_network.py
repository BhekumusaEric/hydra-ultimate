"""
Vulnerable Enterprise Network Module for HYDRA

This module implements a more vulnerable version of the enterprise network
to demonstrate the effectiveness of the Super Red Agent.
"""

import os
import random
import json
import networkx as nx
from enum import Enum
from envs.enterprise_network import EnterpriseNetwork, NodeType, VulnerabilityType

class VulnerableNetwork(EnterpriseNetwork):
    """
    A more vulnerable version of the enterprise network with higher vulnerability density,
    weaker security controls, and more realistic network topology.
    """
    
    def __init__(self, size="medium", complexity="medium", load_from_file=None):
        """
        Initialize a vulnerable enterprise network simulation.

        Args:
            size: small (10-20 nodes), medium (30-50 nodes), large (100-200 nodes)
            complexity: low, medium, high (affects connectivity and vulnerability density)
            load_from_file: Path to a JSON file to load a pre-configured network
        """
        # Call parent constructor but we'll override the network generation
        super().__init__(size, complexity, load_from_file)
        
        # If not loading from file, generate a more vulnerable network
        if not load_from_file or not os.path.exists(load_from_file):
            self._generate_vulnerable_network()
            
        # Log initialization
        self.logs.append(f"Vulnerable enterprise network created with {len(self.graph.nodes())} nodes and {self.graph.number_of_edges()} connections")
    
    def _generate_vulnerable_network(self):
        """Generate a more vulnerable enterprise network."""
        # Clear existing graph
        self.graph.clear()
        
        # Determine number of nodes based on size
        if self.size == "small":
            num_nodes = random.randint(10, 20)
        elif self.size == "medium":
            num_nodes = random.randint(30, 50)
        else:  # large
            num_nodes = random.randint(100, 200)
            
        # Create nodes with properties
        for i in range(num_nodes):
            # Assign node types with realistic distribution
            if i == 0:
                node_type = NodeType.FIREWALL  # Entry point is always a firewall
            elif i < num_nodes * 0.1:
                node_type = NodeType.ROUTER
            elif i < num_nodes * 0.2:
                node_type = NodeType.SERVER
            elif i < num_nodes * 0.3:
                node_type = NodeType.DATABASE
            elif i < num_nodes * 0.4:
                node_type = NodeType.CLOUD_INSTANCE
            else:
                node_type = NodeType.WORKSTATION
                
            # Assign vulnerabilities - more vulnerabilities than standard network
            vulnerabilities = []
            
            # Higher vulnerability chance
            vuln_chance = 0.7  # 70% chance of each vulnerability type
            
            # Assign random vulnerabilities
            for vuln_type in VulnerabilityType:
                if random.random() < vuln_chance:
                    # Assign severity and exploitability - higher than standard
                    severity = random.uniform(5.0, 10.0)  # Higher severity
                    exploitability = random.uniform(0.5, 1.0)  # Higher exploitability
                    vulnerabilities.append({
                        "type": vuln_type.value,
                        "severity": severity,
                        "exploitability": exploitability,
                        "patched": False
                    })
            
            # Add node to graph with properties
            self.graph.add_node(i,
                type=node_type.value,
                vulnerabilities=vulnerabilities,
                services=self._generate_services(node_type),
                os=self._generate_os(),
                patch_level=random.uniform(0.1, 0.7),  # Lower patch levels
                security_controls=self._generate_weak_security_controls(node_type)
            )
        
        # Create edges (connections) between nodes
        self._generate_vulnerable_connections()
        
        # Set entry points
        self.entry_points = [0]  # Firewall is the main entry point
        
        # Add some additional entry points (more than standard)
        for i in range(1, min(5, num_nodes)):
            if random.random() < 0.3:  # 30% chance for each node to be an entry point
                self.entry_points.append(i)
    
    def _generate_weak_security_controls(self, node_type):
        """Generate weaker security controls based on node type."""
        controls = []
        
        # Common controls with lower probabilities
        if random.random() < 0.5:  # 50% chance (down from 70%)
            controls.append("Antivirus")
            
        if random.random() < 0.3:  # 30% chance (down from 50%)
            controls.append("Host Firewall")
            
        if random.random() < 0.1:  # 10% chance (down from 30%)
            controls.append("EDR")
            
        # Type-specific controls
        if node_type == NodeType.SERVER or node_type == NodeType.DATABASE:
            if random.random() < 0.3:  # 30% chance (down from 60%)
                controls.append("Intrusion Detection")
                
            if random.random() < 0.2:  # 20% chance (down from 40%)
                controls.append("File Integrity Monitoring")
                
        elif node_type == NodeType.FIREWALL:
            if random.random() < 0.7:  # 70% chance
                controls.append("Packet Inspection")
                
            if random.random() < 0.4:  # 40% chance (down from 70%)
                controls.append("IPS")
                
        return controls
    
    def _generate_vulnerable_connections(self):
        """Generate more permissive network connections."""
        nodes = list(self.graph.nodes())
        
        # Connect all nodes to at least one router
        routers = [n for n in nodes if self.graph.nodes[n]['type'] == NodeType.ROUTER.value]
        firewalls = [n for n in nodes if self.graph.nodes[n]['type'] == NodeType.FIREWALL.value]
        
        # Connect firewall to routers
        for router in routers:
            for firewall in firewalls:
                self.graph.add_edge(firewall, router, weight=1.0)
                
        # Connect nodes with more permissive rules
        for node in nodes:
            # Higher chance of connections between all node types
            for other_node in nodes:
                if node != other_node and random.random() < 0.2:  # 20% chance of connection
                    self.graph.add_edge(node, other_node, weight=random.uniform(0.5, 1.0))
                    
                    # Add bidirectional connection with high probability
                    if random.random() < 0.8:  # 80% chance of bidirectional connection
                        self.graph.add_edge(other_node, node, weight=random.uniform(0.5, 1.0))
    
    def attack_node(self, node_id, attack_type, skill_level=0.5):
        """
        Attempt to attack a node with a specific attack type.
        This version has higher success probabilities than the standard network.

        Args:
            node_id: ID of the node to attack
            attack_type: Type of attack (e.g., "sql_injection")
            skill_level: Attacker skill level (0.0 to 1.0)

        Returns:
            success: Whether the attack was successful
            info: Additional information about the attack
        """
        if node_id not in self.graph:
            return False, "Node does not exist"
            
        node_data = self.graph.nodes[node_id]
        node_type = node_data['type']
        
        # Check if node is already compromised
        if node_id in self.compromised_nodes:
            return True, "Node already compromised"
            
        # Check for zero-day exploits (always succeed)
        if attack_type.startswith("zero_day_"):
            self.compromised_nodes.add(node_id)
            self.logs.append(f"Node {node_id} ({node_type}) compromised via {attack_type} zero-day exploit")
            
            # Generate alert with low probability (stealthy zero-day)
            if random.random() < 0.2:
                self.alerts.append({
                    "type": "compromise",
                    "node_id": node_id,
                    "attack_type": attack_type,
                    "timestamp": "now"
                })
                
            return True, "Zero-day attack successful"
            
        # Check if the node has vulnerabilities
        vulnerabilities = node_data['vulnerabilities']
        matching_vulns = [v for v in vulnerabilities if v['type'] == attack_type]
        
        if not matching_vulns:
            self.logs.append(f"Attack failed: No {attack_type} vulnerability on node {node_id}")
            return False, f"No {attack_type} vulnerability found"
            
        # Calculate attack success probability - higher than standard
        vuln = matching_vulns[0]  # Use the first matching vulnerability
        base_probability = vuln['exploitability'] * 1.5  # 50% higher base probability
        
        # Adjust based on security controls - less impact than standard
        security_controls = node_data['security_controls']
        control_factor = 1.0 - (len(security_controls) * 0.05)  # Each control reduces success by only 5% (down from 10%)
        
        # Adjust based on patch level (default to 0 if not present) - less impact
        patch_factor = 1.0 - (node_data.get('patch_level', 0.0) * 0.7)  # Patch level has 30% less effect
        
        # Final probability calculation
        success_probability = min(0.95, base_probability * control_factor * patch_factor * skill_level)
        
        # Determine if attack succeeds
        success = random.random() < success_probability
        
        if success:
            self.compromised_nodes.add(node_id)
            self.logs.append(f"Node {node_id} ({node_type}) compromised via {attack_type}")
            
            # Generate alert with lower probability (more stealthy)
            if random.random() < 0.3:  # 30% chance (down from standard)
                self.alerts.append({
                    "type": "compromise",
                    "node_id": node_id,
                    "attack_type": attack_type,
                    "timestamp": "now"
                })
                
            return True, "Attack successful"
        else:
            self.logs.append(f"Attack failed: {attack_type} on node {node_id}")
            
            # Determine if the attack was detected - lower chance than standard
            detection_chance = sum(0.1 for control in security_controls if control in ["Intrusion Detection", "EDR"])
            if random.random() < detection_chance:
                self.alerts.append({
                    "type": "attempt",
                    "node_id": node_id,
                    "attack_type": attack_type,
                    "timestamp": "now"
                })
                
            return False, "Attack failed"
