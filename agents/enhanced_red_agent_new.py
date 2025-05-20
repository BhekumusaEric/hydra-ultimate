"""
Enhanced Red Agent Module for HYDRA

This module implements an advanced red agent with real-world attack patterns,
threat intelligence, and sophisticated attack planning capabilities.
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

# Import basic strategies from advanced_red_agent.py
from agents.advanced_red_agent import RandomAttackStrategy, TargetedAttackStrategy, StealthyAttackStrategy

# Import attack framework
from agents.attack_framework import ATTCKTactic, ATTCKTechnique, TECHNIQUE_TO_VULNERABILITY

# Import new components
from agents.attack_planner import AttackPlanner, AttackGoal, AttackPhase
from agents.data_exfiltration import DataExfiltration, DataType, ExfiltrationType
from agents.credential_theft import CredentialTheft, CredentialTheftTechnique
from agents.living_off_the_land import LivingOffTheLand, LOLBinTechnique

# Advanced attack strategies based on real-world threat actors
class APTStrategy:
    """Base class for APT-style attack strategies"""
    def __init__(self, name, skill_level=0.7):
        self.name = name
        self.skill_level = skill_level
        self.tactics = []
        self.techniques = {}
        self.target_types = []
        self.detection_history = {}

    def select_target(self, env, current_position):
        """Select a target based on APT preferences"""
        raise NotImplementedError

    def select_attack_type(self, env, target_node):
        """Select an attack type based on APT TTPs"""
        raise NotImplementedError

    def update_detection_history(self, node_id, detected):
        """Update detection history for a node"""
        current_rate = self.detection_history.get(node_id, 0.5)
        # Exponential moving average
        self.detection_history[node_id] = 0.7 * current_rate + 0.3 * (1.0 if detected else 0.0)

class APT29Strategy(APTStrategy):
    """Cozy Bear / APT29 strategy - sophisticated, stealthy state actor"""
    def __init__(self, skill_level=0.9):
        super().__init__("APT29", skill_level)
        self.tactics = [
            ATTCKTactic.INITIAL_ACCESS,
            ATTCKTactic.EXECUTION,
            ATTCKTactic.PERSISTENCE,
            ATTCKTactic.PRIVILEGE_ESCALATION,
            ATTCKTactic.DEFENSE_EVASION,
            ATTCKTactic.CREDENTIAL_ACCESS,
            ATTCKTactic.DISCOVERY,
            ATTCKTactic.LATERAL_MOVEMENT,
            ATTCKTactic.COLLECTION,
            ATTCKTactic.EXFILTRATION
        ]
        self.target_types = ["workstation", "server", "database"]

    def select_target(self, env, current_position):
        """Select targets with high value and low security visibility"""
        if current_position is None:
            # Start from an entry point if not positioned
            return random.choice(env.entry_points)

        # Get neighbors
        neighbors = list(env.graph.successors(current_position))
        if not neighbors:
            return random.choice(list(env.graph.nodes()))

        # Score neighbors by value and security controls
        scored_neighbors = []
        for node in neighbors:
            node_data = env.graph.nodes[node]
            node_type = node_data['type']

            # Skip nodes that don't match target types
            if node_type not in self.target_types:
                continue

            # Calculate value score (higher for databases and servers)
            value_score = 0
            if node_type == "database":
                value_score = 10
            elif node_type == "server":
                value_score = 8
            elif node_type == "workstation":
                value_score = 5

            # Calculate security score (lower is better for attacker)
            security_controls = node_data['security_controls']
            security_score = len(security_controls) * 2

            # Check for specific high-value controls
            if "Intrusion Detection" in security_controls:
                security_score += 3
            if "EDR" in security_controls:
                security_score += 4

            # Check detection history
            detection_rate = self.detection_history.get(node, 0.5)
            detection_score = detection_rate * 5

            # Final score (higher is better for attacker)
            final_score = value_score - security_score - detection_score
            scored_neighbors.append((node, final_score))

        if not scored_neighbors:
            return random.choice(neighbors)

        # Sort by score (descending)
        scored_neighbors.sort(key=lambda x: x[1], reverse=True)

        # Select from top 3 or all if fewer
        top_n = min(3, len(scored_neighbors))
        return random.choice(scored_neighbors[:top_n])[0]

    def select_attack_type(self, env, target_node):
        """Select sophisticated attack types with low detection profile"""
        # Preferred stealthy techniques
        preferred_techniques = [
            ATTCKTechnique.VALID_ACCOUNTS,
            ATTCKTechnique.ACCESS_TOKEN_MANIPULATION,
            ATTCKTechnique.MASQUERADING,
            ATTCKTechnique.EXPLOIT_VULNERABILITY
        ]

        # Map techniques to vulnerabilities
        preferred_vulns = []
        for technique in preferred_techniques:
            if technique in TECHNIQUE_TO_VULNERABILITY:
                preferred_vulns.extend(TECHNIQUE_TO_VULNERABILITY[technique])

        if target_node in env.graph:
            # Check target's vulnerabilities
            vulnerabilities = env.graph.nodes[target_node]['vulnerabilities']

            # Filter for preferred vulnerabilities
            matching_vulns = [v for v in vulnerabilities if v['type'] in preferred_vulns]

            if matching_vulns:
                # Sort by exploitability (higher is better)
                sorted_vulns = sorted(matching_vulns, key=lambda v: v['exploitability'], reverse=True)
                return sorted_vulns[0]['type']

            # If no preferred vulnerabilities, use any available
            if vulnerabilities:
                return random.choice(vulnerabilities)['type']

        # Fallback to a default vulnerability type
        return random.choice(preferred_vulns)

class APT41Strategy(APTStrategy):
    """APT41 strategy - financially motivated and espionage actor"""
    def __init__(self, skill_level=0.85):
        super().__init__("APT41", skill_level)
        self.tactics = [
            ATTCKTactic.INITIAL_ACCESS,
            ATTCKTactic.EXECUTION,
            ATTCKTactic.PERSISTENCE,
            ATTCKTactic.PRIVILEGE_ESCALATION,
            ATTCKTactic.DEFENSE_EVASION,
            ATTCKTactic.CREDENTIAL_ACCESS,
            ATTCKTactic.DISCOVERY,
            ATTCKTactic.LATERAL_MOVEMENT,
            ATTCKTactic.COLLECTION,
            ATTCKTactic.EXFILTRATION,
            ATTCKTactic.IMPACT
        ]
        self.target_types = ["server", "database", "cloud_instance"]

    def select_target(self, env, current_position):
        """Select high-value financial targets"""
        if current_position is None:
            # Start from an entry point if not positioned
            return random.choice(env.entry_points)

        # Prioritize databases and servers
        all_nodes = list(env.graph.nodes())
        databases = [n for n in all_nodes if env.graph.nodes[n]['type'] == "database"]
        servers = [n for n in all_nodes if env.graph.nodes[n]['type'] == "server"]
        cloud = [n for n in all_nodes if env.graph.nodes[n]['type'] == "cloud_instance"]

        # If we can reach a database directly, prioritize it
        neighbors = list(env.graph.successors(current_position))
        neighbor_databases = [n for n in neighbors if n in databases]
        if neighbor_databases:
            return random.choice(neighbor_databases)

        # If we can reach a server directly, go there
        neighbor_servers = [n for n in neighbors if n in servers]
        if neighbor_servers:
            return random.choice(neighbor_servers)

        # If we can reach cloud instances directly, go there
        neighbor_cloud = [n for n in neighbors if n in cloud]
        if neighbor_cloud:
            return random.choice(neighbor_cloud)

        # Otherwise, move to any neighbor
        if neighbors:
            return random.choice(neighbors)

        # Fallback to random node
        return random.choice(all_nodes)

    def select_attack_type(self, env, target_node):
        """Select attack type based on target and available vulnerabilities"""
        # Preferred techniques for different target types
        target_type = env.graph.nodes[target_node]['type'] if target_node in env.graph else None

        preferred_vulns = []
        if target_type == "database":
            preferred_vulns = ["sql_injection", "default_credentials"]
        elif target_type == "server":
            preferred_vulns = ["unpatched_cve", "buffer_overflow"]
        elif target_type == "cloud_instance":
            preferred_vulns = ["misconfiguration", "default_credentials"]
        else:
            # Default preferences
            preferred_vulns = ["sql_injection", "unpatched_cve", "default_credentials"]

        if target_node in env.graph:
            # Check target's vulnerabilities
            vulnerabilities = env.graph.nodes[target_node]['vulnerabilities']

            # Filter for preferred vulnerabilities
            matching_vulns = [v for v in vulnerabilities if v['type'] in preferred_vulns]

            if matching_vulns:
                # Sort by severity (higher is better)
                sorted_vulns = sorted(matching_vulns, key=lambda v: v['severity'], reverse=True)
                return sorted_vulns[0]['type']

            # If no preferred vulnerabilities, use any available
            if vulnerabilities:
                return random.choice(vulnerabilities)['type']

        # Fallback to a default vulnerability type
        return random.choice(preferred_vulns)

class RansomwareStrategy(APTStrategy):
    """Modern ransomware strategy with double extortion"""
    def __init__(self, skill_level=0.75):
        super().__init__("Ransomware", skill_level)
        self.tactics = [
            ATTCKTactic.INITIAL_ACCESS,
            ATTCKTactic.EXECUTION,
            ATTCKTactic.PRIVILEGE_ESCALATION,
            ATTCKTactic.DISCOVERY,
            ATTCKTactic.LATERAL_MOVEMENT,
            ATTCKTactic.COLLECTION,
            ATTCKTactic.EXFILTRATION,
            ATTCKTactic.IMPACT
        ]
        self.target_types = ["server", "database", "workstation"]

    def select_target(self, env, current_position):
        """Aggressively target data storage systems"""
        if current_position is None:
            # Start from an entry point if not positioned
            return random.choice(env.entry_points)

        # Try to find as many targets as possible for maximum impact
        all_nodes = list(env.graph.nodes())

        # Prioritize by type
        databases = [n for n in all_nodes if env.graph.nodes[n]['type'] == "database"]
        servers = [n for n in all_nodes if env.graph.nodes[n]['type'] == "server"]
        workstations = [n for n in all_nodes if env.graph.nodes[n]['type'] == "workstation"]

        # Get neighbors
        neighbors = list(env.graph.successors(current_position))
        if not neighbors:
            # If no neighbors, try to find a high-value target
            if databases:
                return random.choice(databases)
            elif servers:
                return random.choice(servers)
            else:
                return random.choice(all_nodes)

        # Prioritize neighbors by type
        neighbor_databases = [n for n in neighbors if n in databases]
        if neighbor_databases:
            return random.choice(neighbor_databases)

        neighbor_servers = [n for n in neighbors if n in servers]
        if neighbor_servers:
            return random.choice(neighbor_servers)

        neighbor_workstations = [n for n in neighbors if n in workstations]
        if neighbor_workstations:
            return random.choice(neighbor_workstations)

        # If no preferred neighbors, choose any neighbor
        return random.choice(neighbors)

    def select_attack_type(self, env, target_node):
        """Select attack types that enable rapid compromise"""
        # Ransomware prefers fast, effective attacks
        preferred_vulns = ["buffer_overflow", "unpatched_cve", "default_credentials", "privilege_escalation"]

        if target_node in env.graph:
            # Check target's vulnerabilities
            vulnerabilities = env.graph.nodes[target_node]['vulnerabilities']

            # Filter for preferred vulnerabilities
            matching_vulns = [v for v in vulnerabilities if v['type'] in preferred_vulns]

            if matching_vulns:
                # Sort by severity and exploitability
                sorted_vulns = sorted(matching_vulns,
                                     key=lambda v: v['severity'] * v['exploitability'],
                                     reverse=True)
                return sorted_vulns[0]['type']

            # If no preferred vulnerabilities, use any available
            if vulnerabilities:
                return random.choice(vulnerabilities)['type']

        # Fallback to a default vulnerability type
        return random.choice(preferred_vulns)

class EnhancedRedAgent:
    """Enhanced Red Agent with real-world attack patterns and threat intelligence"""
    def __init__(self, env, skill_level=0.7, learning_rate=0.001, threat_intel_file=None):
        self.env = env
        self.skill_level = skill_level
        self.current_position = None
        self.compromised_nodes = set()
        self.attack_history = []
        self.data_collected = {}  # Track data collected from nodes
        self.lateral_movement_paths = []  # Track successful lateral movement

        # Initialize advanced attack strategies
        self.strategies = {
            "APT29": APT29Strategy(skill_level * 1.2),
            "APT41": APT41Strategy(skill_level * 1.1),
            "Ransomware": RansomwareStrategy(skill_level),
            "Random": RandomAttackStrategy(skill_level * 0.8),
            "Targeted": TargetedAttackStrategy(skill_level=skill_level),
            "Stealthy": StealthyAttackStrategy(skill_level=skill_level * 1.2)
        }

        # Strategy selection probabilities
        self.strategy_probs = {
            "APT29": 0.25,
            "APT41": 0.25,
            "Ransomware": 0.15,
            "Random": 0.05,
            "Targeted": 0.15,
            "Stealthy": 0.15
        }

        # Initialize learning components
        self.learning_rate = learning_rate
        self.memory = deque(maxlen=1000)
        self.gamma = 0.95  # Discount factor

        # Initialize neural network for strategy selection
        self.initialize_network()

        # Load threat intelligence if provided
        self.threat_intelligence = {}
        if threat_intel_file and os.path.exists(threat_intel_file):
            self.load_threat_intelligence(threat_intel_file)

        # Initialize new components
        self.attack_planner = AttackPlanner(env, skill_level)
        self.data_exfiltration = DataExfiltration(env, skill_level)
        self.credential_theft = CredentialTheft(env, skill_level)
        self.living_off_the_land = LivingOffTheLand(env, skill_level)

        # Attack campaign tracking
        self.campaign_goal = self._select_campaign_goal()
        self.campaign_progress = 0.0
        self.campaign_start_time = time.time()

        # Set the campaign goal in the attack planner
        attack_goal = AttackGoal(self.campaign_goal) if self.campaign_goal in [g.value for g in AttackGoal] else None
        self.attack_planner.set_campaign_goal(attack_goal)

    def _select_campaign_goal(self):
        """Select a goal for the attack campaign"""
        goals = [
            "data_theft",  # Steal sensitive data
            "persistence",  # Establish long-term access
            "disruption",   # Disrupt operations
            "ransomware"    # Deploy ransomware
        ]
        return random.choice(goals)

    def initialize_network(self):
        """Initialize neural network for strategy selection"""
        # More sophisticated network with additional layers
        self.model = nn.Sequential(
            nn.Linear(15, 64),  # Input: expanded network state features
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, len(self.strategies)),
            nn.Softmax(dim=1)
        )

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

    def load_threat_intelligence(self, file_path):
        """Load threat intelligence data from file"""
        try:
            with open(file_path, 'r') as f:
                self.threat_intelligence = json.load(f)
        except Exception as e:
            print(f"Error loading threat intelligence: {e}")

    def get_state_features(self):
        """Get the current state as a feature vector for decision making"""
        # Basic features
        num_nodes = len(self.env.graph.nodes())
        num_compromised = len(self.compromised_nodes)
        compromise_ratio = num_compromised / max(1, num_nodes)

        # Network structure features
        try:
            import networkx as nx
            # Calculate centrality of current position
            if self.current_position is not None:
                centrality = nx.degree_centrality(self.env.graph).get(self.current_position, 0)
                closeness = nx.closeness_centrality(self.env.graph).get(self.current_position, 0)
            else:
                centrality = 0
                closeness = 0
        except:
            centrality = 0
            closeness = 0

        # Campaign progress features
        campaign_duration = (time.time() - self.campaign_start_time) / 3600  # Hours
        campaign_progress = self.campaign_progress

        # Goal-specific features
        goal_data_theft = 1 if self.campaign_goal == "data_theft" else 0
        goal_persistence = 1 if self.campaign_goal == "persistence" else 0
        goal_disruption = 1 if self.campaign_goal == "disruption" else 0
        goal_ransomware = 1 if self.campaign_goal == "ransomware" else 0

        # Detection features
        alerts_count = len(self.env.alerts)
        detection_ratio = alerts_count / max(1, len(self.attack_history))

        # Combine all features
        features = [
            compromise_ratio,
            centrality,
            closeness,
            campaign_duration,
            campaign_progress,
            goal_data_theft,
            goal_persistence,
            goal_disruption,
            goal_ransomware,
            detection_ratio,
            num_compromised,
            len(self.data_collected),
            len(self.lateral_movement_paths),
            self.skill_level,
            alerts_count / max(1, num_nodes)
        ]

        return features

    def select_strategy(self, state_features=None):
        """Select an attack strategy based on current state and campaign goal"""
        # Adjust strategy probabilities based on campaign goal
        if self.campaign_goal == "data_theft":
            self.strategy_probs["APT29"] = 0.35
            self.strategy_probs["APT41"] = 0.30
            self.strategy_probs["Ransomware"] = 0.05
        elif self.campaign_goal == "persistence":
            self.strategy_probs["APT29"] = 0.40
            self.strategy_probs["Stealthy"] = 0.30
        elif self.campaign_goal == "disruption":
            self.strategy_probs["APT41"] = 0.30
            self.strategy_probs["Ransomware"] = 0.30
        elif self.campaign_goal == "ransomware":
            self.strategy_probs["Ransomware"] = 0.50
            self.strategy_probs["APT41"] = 0.20

        # Use neural network if state features provided and not in exploration mode
        if state_features is not None and random.random() > 0.2:  # Reduced exploration rate
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state_features).unsqueeze(0)
                strategy_probs = self.model(state_tensor).squeeze().numpy()
                strategy_names = list(self.strategies.keys())
                return self.strategies[strategy_names[np.argmax(strategy_probs)]]

        # Use probability-based selection
        strategy_names = list(self.strategy_probs.keys())
        strategy_p = [self.strategy_probs[s] for s in strategy_names]
        selected_strategy = random.choices(strategy_names, weights=strategy_p, k=1)[0]

        return self.strategies[selected_strategy]

    def act(self):
        """Execute an attack action based on the selected strategy and campaign goal"""
        # Get state features for strategy selection
        state_features = self.get_state_features()

        # Check if we should use the attack planner for a more sophisticated attack
        use_planner = random.random() < 0.7  # 70% chance to use the planner

        if use_planner:
            # Get the next action from the attack planner
            next_action = self.attack_planner.get_next_action(self.current_position)

            if next_action:
                # Use the planned action
                target_node = next_action["node"]
                attack_phase = next_action["phase"]
                techniques = next_action["techniques"]

                # Select a technique from the planned ones
                if techniques:
                    technique = random.choice(techniques)
                    # Map technique to an attack type
                    attack_type = self._map_technique_to_attack_type(technique)
                else:
                    # Fallback to strategy-based selection
                    strategy = self.select_strategy(state_features)
                    attack_type = strategy.select_attack_type(self.env, target_node)
            else:
                # If no planned action, fall back to strategy-based selection
                strategy = self.select_strategy(state_features)
                target_node = strategy.select_target(self.env, self.current_position)
                attack_type = strategy.select_attack_type(self.env, target_node)
        else:
            # Use strategy-based selection
            strategy = self.select_strategy(state_features)
            target_node = strategy.select_target(self.env, self.current_position)
            attack_type = strategy.select_attack_type(self.env, target_node)

        # Check if we should use a zero-day exploit
        use_zero_day = self._should_use_zero_day(target_node,
                                               self.strategies["APT29"] if use_planner else strategy)
        if use_zero_day:
            attack_type = self._select_zero_day_attack()
            # Zero-day attacks have higher skill level
            skill_level = min(1.0, self.skill_level * 1.5)
        else:
            skill_level = self.skill_level

        # Apply advanced evasion techniques if needed
        evasion_applied = False
        if self._should_use_evasion(target_node):
            evasion_applied = self._apply_evasion_techniques(target_node)
            # Evasion techniques reduce detection chance
            if evasion_applied:
                skill_level = min(1.0, skill_level * 1.2)

        # Execute attack
        success, info = self.env.attack_node(target_node, attack_type, skill_level)

        # Update agent state
        if success:
            previous_position = self.current_position
            self.current_position = target_node
            self.compromised_nodes.add(target_node)

            # Update campaign progress based on goal
            self._update_campaign_progress(target_node)

            # Perform data collection and exfiltration if that's the campaign goal
            if self.campaign_goal == "data_theft" or self.campaign_goal == "ransomware":
                self._perform_data_operations(target_node)

            # Attempt credential theft
            self._attempt_credential_theft(target_node)

            # Deploy persistence mechanisms
            if self.campaign_goal == "persistence" or random.random() < 0.3:
                self._deploy_persistence_mechanism(target_node)

            # Use living-off-the-land techniques
            self._use_living_off_the_land_techniques(target_node)

            # Track lateral movement
            if previous_position is not None and previous_position != target_node:
                self.lateral_movement_paths.append((previous_position, target_node))

            # If this is a high-value target, establish additional access paths
            if self._is_high_value_target(target_node) and random.random() < 0.7:
                self._establish_backup_access(target_node)

        # Determine if attack was detected
        detected = "attempt" in info

        # If evasion was applied, reduce detection chance
        if evasion_applied and detected and random.random() < 0.6:
            detected = False
            info = "Attack successful with evasion"

        # Record attack in history
        attack_record = {
            "strategy": "Planned" if use_planner else strategy.name,
            "target": target_node,
            "attack_type": attack_type,
            "success": success,
            "detected": detected,
            "zero_day": use_zero_day,
            "evasion": evasion_applied,
            "info": info,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.attack_history.append(attack_record)

        # Update detection history for APT strategies
        if not use_planner and hasattr(strategy, 'update_detection_history'):
            strategy.update_detection_history(target_node, detected)

        # Store experience for learning
        reward = self._calculate_reward(success, detected, target_node)
        next_state_features = self.get_state_features()

        self.memory.append((state_features,
                           "Planned" if use_planner else strategy.name,
                           reward,
                           next_state_features))

        # Learn from experience
        if len(self.memory) > 32:
            self.learn(batch_size=32)

        return success, attack_record

    def _map_technique_to_attack_type(self, technique):
        """Map a MITRE ATT&CK technique to an attack type"""
        # Mapping of common techniques to attack types
        technique_mapping = {
            "phishing": "cross_site_scripting",
            "exploit_public_facing_application": "unpatched_cve",
            "valid_accounts": "default_credentials",
            "supply_chain_compromise": "unpatched_cve",
            "external_remote_services": "default_credentials",
            "drive_by_compromise": "cross_site_scripting",
            "command_line_interface": "privilege_escalation",
            "scripting": "privilege_escalation",
            "powershell": "privilege_escalation",
            "scheduled_task": "privilege_escalation",
            "registry_run_keys": "privilege_escalation",
            "access_token_manipulation": "privilege_escalation",
            "bypass_user_account_control": "privilege_escalation",
            "obfuscated_files": "buffer_overflow",
            "indicator_removal": "misconfiguration",
            "brute_force": "default_credentials",
            "credential_dumping": "privilege_escalation",
            "network_service_scanning": "misconfiguration",
            "remote_services": "default_credentials",
            "internal_spearphishing": "cross_site_scripting",
            "data_from_local_system": "privilege_escalation",
            "data_staged": "privilege_escalation",
            "exfiltration_over_c2_channel": "privilege_escalation",
            "scheduled_transfer": "privilege_escalation",
            "data_encrypted_for_impact": "privilege_escalation",
            "service_stop": "privilege_escalation"
        }

        return technique_mapping.get(technique, "misconfiguration")  # Default fallback

    def _perform_data_operations(self, node_id):
        """Perform data collection and exfiltration operations"""
        # First, try to collect data from the node
        success, data_types, total_size = self.data_exfiltration.collect_data(node_id)

        if success and data_types:
            # Record the data collection in our own tracking
            if node_id not in self.data_collected:
                self.data_collected[node_id] = []
            self.data_collected[node_id].extend([d["type"] for d in data_types])

            # If we have enough data, try to stage it for exfiltration
            if len(self.data_collected) >= 3 or random.random() < 0.3:
                # Find a good staging node (preferably one with external access)
                staging_candidates = []

                # Prefer nodes that can reach entry points
                for node in self.compromised_nodes:
                    if node == node_id:
                        continue

                    # Check if this node can reach an entry point
                    can_reach_entry = False
                    for entry in self.env.entry_points:
                        try:
                            import networkx as nx
                            path = nx.shortest_path(self.env.graph, node, entry)
                            can_reach_entry = True
                            break
                        except (nx.NetworkXNoPath, nx.NodeNotFound):
                            continue

                    if can_reach_entry:
                        staging_candidates.append((node, 2))  # Higher weight
                    else:
                        staging_candidates.append((node, 1))

                if staging_candidates:
                    # Select a staging node with weighted probability
                    nodes, weights = zip(*staging_candidates)
                    staging_node = random.choices(nodes, weights=weights, k=1)[0]

                    # Stage the data
                    stage_success, staged_size = self.data_exfiltration.stage_data(node_id, staging_node)

                    # If staging was successful and we have enough data, try to exfiltrate
                    if stage_success and (staged_size > 5000 or random.random() < 0.4):
                        # Exfiltrate the data
                        exfil_success, exfil_record, detected = self.data_exfiltration.exfiltrate_data(staging_node)

                        if exfil_success:
                            # Update campaign progress significantly for successful exfiltration
                            self.campaign_progress += 0.2

                            # Log the exfiltration
                            self.env.logs.append(f"Data exfiltration detected from node {staging_node}: {staged_size} KB")

                            # If this is a ransomware campaign, encrypt the data
                            if self.campaign_goal == "ransomware":
                                self._encrypt_data_for_ransom(staging_node)

    def _encrypt_data_for_ransom(self, node_id):
        """Simulate encrypting data on a node for ransomware"""
        if node_id not in self.env.graph:
            return False

        node_data = self.env.graph.nodes[node_id]
        node_type = node_data.get('type', '')

        # Log the encryption activity
        self.env.logs.append(f"Ransomware encryption detected on node {node_id} ({node_type})")

        # Generate an alert
        self.env.alerts.append({
            "type": "ransomware",
            "node_id": node_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "details": {
                "encryption_algorithm": "AES-256",
                "ransom_note": "Your files have been encrypted. Pay 10 BTC to recover them."
            }
        })

        # Update campaign progress
        self.campaign_progress += 0.15

        # Generate network traffic for command and control
        self._generate_c2_traffic(node_id)

        return True

    def _generate_c2_traffic(self, source_node):
        """Generate command and control traffic"""
        # Select a destination (usually an entry point)
        if not self.env.entry_points:
            return

        destination = random.choice(self.env.entry_points)

        # Create C2 traffic event
        event = {
            "source": source_node,
            "destination": destination,
            "type": "HTTPS",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "size": random.randint(1000, 5000),
            "malicious": True,
            "details": {
                "method": "POST",
                "path": f"/api/report/{random.randint(1000, 9999)}",
                "host": f"c2-{random.randint(100, 999)}.example.com",
                "encrypted": True
            }
        }

        self.env.traffic_logs.append(event)

    def _should_use_zero_day(self, target_node, strategy):
        """Determine if a zero-day exploit should be used"""
        # Zero-days are rare and should be used strategically
        if not hasattr(self, 'zero_day_usage_count'):
            self.zero_day_usage_count = 0

        # Limit zero-day usage
        if self.zero_day_usage_count >= 3:
            return False

        # Only certain APTs have zero-days
        if strategy.name not in ["APT29", "APT41"]:
            return False

        # Only use on high-value targets
        if not self._is_high_value_target(target_node):
            return False

        # Use zero-days when other methods have failed
        target_attempts = [a for a in self.attack_history if a['target'] == target_node]
        if len(target_attempts) < 2:
            return False

        # 10% chance of using a zero-day if all conditions are met
        if random.random() < 0.1:
            self.zero_day_usage_count += 1
            return True

        return False

    def _select_zero_day_attack(self):
        """Select a zero-day attack type"""
        zero_days = [
            "zero_day_buffer_overflow",
            "zero_day_remote_code_execution",
            "zero_day_privilege_escalation"
        ]
        return random.choice(zero_days)

    def _should_use_evasion(self, target_node):
        """Determine if evasion techniques should be used"""
        if target_node not in self.env.graph:
            return False

        # Check if target has strong security controls
        security_controls = self.env.graph.nodes[target_node]['security_controls']
        has_strong_security = any(c in security_controls for c in ["Intrusion Detection", "EDR", "Packet Inspection"])

        # More likely to use evasion on well-protected targets
        evasion_chance = 0.2
        if has_strong_security:
            evasion_chance = 0.6

        # Adjust based on skill level
        evasion_chance *= self.skill_level

        return random.random() < evasion_chance

    def _apply_evasion_techniques(self, target_node):
        """Apply evasion techniques to avoid detection"""
        # Simulate applying evasion techniques
        self.env.logs.append(f"Evasion techniques applied against node {target_node}")
        return True

    def _update_campaign_progress(self, target_node):
        """Update campaign progress based on goal and target"""
        if target_node not in self.env.graph:
            return

        node_data = self.env.graph.nodes[target_node]
        node_type = node_data.get('type', '')

        # Base progress increment
        progress_increment = 0.05

        # Adjust based on node type and campaign goal
        if self.campaign_goal == "data_theft" and node_type in ["database", "server"]:
            progress_increment = 0.1
        elif self.campaign_goal == "persistence" and node_type in ["server", "domain_controller"]:
            progress_increment = 0.1
        elif self.campaign_goal == "disruption" and node_type in ["router", "firewall", "server"]:
            progress_increment = 0.1
        elif self.campaign_goal == "ransomware" and node_type in ["database", "file_server"]:
            progress_increment = 0.1

        # Update progress
        self.campaign_progress = min(1.0, self.campaign_progress + progress_increment)

    def _attempt_credential_theft(self, node_id):
        """Attempt to steal credentials from a compromised node"""
        # Determine if we should attempt credential theft
        if random.random() < 0.7:  # 70% chance to attempt credential theft
            # Get node information
            if node_id not in self.env.graph:
                return False

            node_info = self.env.graph.nodes[node_id]
            os_type = node_info.get('os', {}).get('type', 'Unknown')

            # Select an appropriate technique based on OS
            technique = None
            if os_type == "Windows":
                techniques = [
                    CredentialTheftTechnique.MIMIKATZ.value,
                    CredentialTheftTechnique.LSASS_MEMORY_DUMP.value,
                    CredentialTheftTechnique.REGISTRY_EXTRACTION.value,
                    CredentialTheftTechnique.NTLM_HASH_EXTRACTION.value
                ]
                technique = random.choice(techniques)
            elif os_type == "Linux":
                techniques = [
                    CredentialTheftTechnique.KEYLOGGING.value,
                    CredentialTheftTechnique.CREDENTIAL_PROMPT_SPOOFING.value,
                    CredentialTheftTechnique.BROWSER_CREDENTIAL_THEFT.value
                ]
                technique = random.choice(techniques)
            elif os_type == "macOS":
                techniques = [
                    CredentialTheftTechnique.KEYLOGGING.value,
                    CredentialTheftTechnique.BROWSER_CREDENTIAL_THEFT.value,
                    CredentialTheftTechnique.CREDENTIAL_PROMPT_SPOOFING.value
                ]
                technique = random.choice(techniques)

            # Attempt credential theft
            success, credentials, detected = self.credential_theft.steal_credentials(node_id, technique)

            # If successful, update campaign progress
            if success:
                self.campaign_progress = min(1.0, self.campaign_progress + 0.05)

                # If this is a lateral movement campaign, use the credentials for lateral movement
                if self.campaign_goal in ["data_theft", "persistence", "ransomware"]:
                    self._use_stolen_credentials(credentials)

            return success

        return False

    def _use_stolen_credentials(self, credentials):
        """Use stolen credentials for lateral movement or privilege escalation"""
        if not credentials:
            return False

        # Log the use of stolen credentials
        self.env.logs.append(f"Using stolen credentials: {credentials['username']} ({credentials['type']})")

        # Simulate using the credentials for lateral movement
        # This would be implemented in a real system by attempting to authenticate to other systems
        return True

    def _use_living_off_the_land_techniques(self, node_id):
        """Use living-off-the-land techniques on a compromised node"""
        # Determine if we should use living-off-the-land techniques
        if random.random() < 0.6:  # 60% chance to use living-off-the-land
            # Get node information
            if node_id not in self.env.graph:
                return False

            node_info = self.env.graph.nodes[node_id]
            os_type = node_info.get('os', {}).get('type', 'Unknown')

            # Select purpose based on campaign goal
            if self.campaign_goal == "persistence":
                purpose = "persistence"
            elif self.campaign_goal == "data_theft":
                purpose = "data_collection"
            elif self.campaign_goal == "ransomware":
                purpose = "execution"
            else:
                purpose = random.choice(["execution", "lateral_movement", "data_collection", "persistence"])

            # Execute living-off-the-land technique
            success, details, detected = self.living_off_the_land.execute_lolbin(node_id, purpose=purpose)

            # If successful, update campaign progress
            if success:
                self.campaign_progress = min(1.0, self.campaign_progress + 0.03)

                # Log the technique used
                if details:
                    self.env.logs.append(f"Living-off-the-land technique used on node {node_id}: {details['technique']} for {purpose}")

            return success

        return False

    def _deploy_persistence_mechanism(self, node_id):
        """Deploy a persistence mechanism on a compromised node"""
        # Use living-off-the-land for persistence
        return self._use_living_off_the_land_techniques(node_id)

    def _is_high_value_target(self, target_node):
        """Determine if a target is high-value"""
        if target_node not in self.env.graph:
            return False

        node_data = self.env.graph.nodes[target_node]
        node_type = node_data.get('type', '')

        # High-value node types
        high_value_types = ["database", "domain_controller", "server", "cloud_instance"]

        return node_type in high_value_types

    def _deploy_persistence_mechanism(self, node_id):
        """Deploy persistence mechanisms on a compromised node"""
        if node_id not in self.env.graph:
            return False

        # Log the persistence activity
        self.env.logs.append(f"Persistence mechanism deployed on node {node_id}")

        # Update campaign progress if persistence is the goal
        if self.campaign_goal == "persistence":
            self.campaign_progress += 0.1

        return True

    def _establish_backup_access(self, node_id):
        """Establish additional access paths to important nodes"""
        if node_id not in self.env.graph:
            return False

        # Log the activity
        self.env.logs.append(f"Backup access established to node {node_id}")

        return True

    def _calculate_reward(self, success, detected, target_node):
        """Calculate reward for reinforcement learning"""
        # Base reward
        base_reward = -0.1  # Small negative reward for any action

        if success:
            # Reward for successful compromise
            base_reward += 1.0

            # Bonus for high-value targets
            if self._is_high_value_target(target_node):
                base_reward += 0.5

            # Penalty for detection
            if detected:
                base_reward -= 0.7
        else:
            # Penalty for failed attack
            base_reward -= 0.2

            # Larger penalty if detected
            if detected:
                base_reward -= 0.3

        # Bonus for stealth over time
        if success and not detected:
            # Higher reward for maintaining stealth as campaign progresses
            stealth_bonus = 0.3 * (len(self.compromised_nodes) / max(1, len(self.env.graph.nodes())))
            base_reward += stealth_bonus

        # Bonus for achieving campaign milestones
        if self.campaign_goal == "data_theft" and len(self.data_collected) > 5:
            base_reward += 0.7
        elif self.campaign_goal == "persistence" and len(self.compromised_nodes) > 10:
            base_reward += 0.7
        elif self.campaign_goal == "ransomware" and self.campaign_progress > 0.7:
            base_reward += 1.0

        return base_reward

    def learn(self, batch_size=32):
        """Learn from past experiences with enhanced learning algorithm"""
        if len(self.memory) < batch_size:
            return

        # Sample a batch of experiences
        batch = random.sample(self.memory, batch_size)

        for state, strategy_name, reward, next_state in batch:
            # Convert to tensors
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0)

            # Get current Q values
            current_q = self.model(state_tensor)

            # Get next Q values
            next_q = self.model(next_state_tensor).detach()

            # Get strategy index
            strategy_idx = list(self.strategies.keys()).index(strategy_name)

            # Update Q value for the selected strategy
            target_q = current_q.clone()
            target_q[0, strategy_idx] = reward + self.gamma * torch.max(next_q)

            # Calculate loss
            loss = self.criterion(current_q, target_q)

            # Backpropagate
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        # Update strategy probabilities based on recent performance
        if self.attack_history:
            recent_history = self.attack_history[-50:]
            strategy_success = {}

            for strategy_name in self.strategies:
                strategy_attacks = [a for a in recent_history if a['strategy'] == strategy_name]
                if strategy_attacks:
                    # Consider both success and stealth
                    success_rate = sum(1 for a in strategy_attacks if a['success']) / len(strategy_attacks)
                    stealth_rate = 1.0 - sum(1 for a in strategy_attacks if a.get('detected', False)) / len(strategy_attacks)
                    strategy_success[strategy_name] = 0.7 * success_rate + 0.3 * stealth_rate
                else:
                    strategy_success[strategy_name] = 0.33  # Default

            # Normalize and update probabilities
            total = sum(strategy_success.values())
            if total > 0:
                for strategy_name in strategy_success:
                    # Update with some inertia to avoid rapid changes
                    old_prob = self.strategy_probs[strategy_name]
                    new_prob = strategy_success[strategy_name] / total
                    self.strategy_probs[strategy_name] = 0.8 * old_prob + 0.2 * new_prob

    def get_compromised_nodes(self):
        """Return the set of compromised nodes"""
        return self.compromised_nodes

    def get_campaign_status(self):
        """Get the current status of the attack campaign"""
        return {
            "goal": self.campaign_goal,
            "progress": self.campaign_progress,
            "compromised_nodes": len(self.compromised_nodes),
            "data_collected": len(self.data_collected),
            "lateral_movements": len(self.lateral_movement_paths)
        }