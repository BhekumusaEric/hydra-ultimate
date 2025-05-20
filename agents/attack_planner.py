"""
Attack Planner Module for HYDRA

This module implements sophisticated planning algorithms for creating multi-stage attack campaigns.
It uses AI-driven techniques to plan and execute complex attack sequences based on the MITRE ATT&CK framework.
"""

import random
import numpy as np
import networkx as nx
from collections import deque, defaultdict
import json
import os
from enum import Enum

# Import MITRE ATT&CK tactics and techniques
from agents.attack_framework import ATTCKTactic, ATTCKTechnique

class AttackPhase(Enum):
    """Phases of an attack campaign"""
    RECONNAISSANCE = "reconnaissance"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    COMMAND_AND_CONTROL = "command_and_control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"

class AttackGoal(Enum):
    """Goals for attack campaigns"""
    DATA_THEFT = "data_theft"
    PERSISTENCE = "persistence"
    DISRUPTION = "disruption"
    RANSOMWARE = "ransomware"
    ESPIONAGE = "espionage"

class AttackPlanner:
    """
    Advanced attack planner that creates sophisticated multi-stage attack campaigns
    using AI-driven planning algorithms.
    """
    def __init__(self, env, skill_level=0.7, threat_intel_file=None):
        self.env = env
        self.skill_level = skill_level
        self.current_phase = None
        self.campaign_goal = None
        self.attack_path = []
        self.target_nodes = []
        self.high_value_targets = []
        self.threat_intel = self._load_threat_intel(threat_intel_file)

    def _load_threat_intel(self, threat_intel_file):
        """Load threat intelligence data from file"""
        if not threat_intel_file or not os.path.exists(threat_intel_file):
            # Use default threat intel
            return {
                "techniques": {
                    "initial_access": ["phishing", "exploit_public_facing_application"],
                    "execution": ["command_line_interface", "scripting"],
                    "persistence": ["registry_run_keys", "scheduled_task"],
                    "privilege_escalation": ["access_token_manipulation", "bypass_user_account_control"],
                    "defense_evasion": ["obfuscated_files", "indicator_removal"],
                    "credential_access": ["brute_force", "credential_dumping"],
                    "discovery": ["file_and_directory_discovery", "network_service_scanning"],
                    "lateral_movement": ["remote_services", "internal_spearphishing"],
                    "collection": ["data_from_local_system", "data_staged"],
                    "command_and_control": ["encrypted_channel", "multi_stage_channels"],
                    "exfiltration": ["exfiltration_over_c2_channel", "scheduled_transfer"],
                    "impact": ["data_encrypted_for_impact", "service_stop"]
                }
            }

        try:
            with open(threat_intel_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading threat intel file: {e}")
            return {}

    def set_campaign_goal(self, goal=None):
        """Set the goal for the attack campaign"""
        if goal is None:
            # Randomly select a goal if none provided
            self.campaign_goal = random.choice(list(AttackGoal))
        elif isinstance(goal, AttackGoal):
            self.campaign_goal = goal
        else:
            try:
                self.campaign_goal = AttackGoal(goal)
            except ValueError:
                self.campaign_goal = random.choice(list(AttackGoal))

        # Reset the attack path
        self.attack_path = []
        self.current_phase = AttackPhase.RECONNAISSANCE

        # Identify high-value targets based on the goal
        self._identify_high_value_targets()

        return self.campaign_goal

    def _identify_high_value_targets(self):
        """Identify high-value targets based on the campaign goal"""
        self.high_value_targets = []

        # Get all nodes
        all_nodes = list(self.env.graph.nodes())

        if not all_nodes:
            return

        # Different goals prioritize different types of targets
        if self.campaign_goal == AttackGoal.DATA_THEFT or self.campaign_goal == AttackGoal.ESPIONAGE:
            # Prioritize databases and servers with sensitive data
            for node in all_nodes:
                node_data = self.env.graph.nodes[node]
                if node_data.get('type') in ['database', 'file_server', 'server']:
                    self.high_value_targets.append(node)

        elif self.campaign_goal == AttackGoal.DISRUPTION or self.campaign_goal == AttackGoal.RANSOMWARE:
            # Prioritize critical infrastructure and high-centrality nodes
            critical_nodes = self.env.get_critical_nodes()
            self.high_value_targets.extend(critical_nodes)

            # Add domain controllers and critical servers
            for node in all_nodes:
                node_data = self.env.graph.nodes[node]
                if node_data.get('type') in ['domain_controller', 'critical_server']:
                    self.high_value_targets.append(node)

        elif self.campaign_goal == AttackGoal.PERSISTENCE:
            # Prioritize nodes with high connectivity
            centrality = nx.degree_centrality(self.env.graph)
            sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
            top_nodes = [node for node, _ in sorted_nodes[:max(1, len(sorted_nodes) // 3)]]
            self.high_value_targets.extend(top_nodes)

        # Ensure we have at least some targets
        if not self.high_value_targets and all_nodes:
            self.high_value_targets = random.sample(all_nodes, min(3, len(all_nodes)))

    def plan_attack_path(self):
        """
        Plan a multi-stage attack path based on the campaign goal
        and current network state.
        """
        if not self.campaign_goal:
            self.set_campaign_goal()

        # Reset attack path
        self.attack_path = []

        # Start with entry points
        entry_points = self.env.entry_points
        if not entry_points:
            # If no entry points defined, use nodes with external connections
            entry_points = [n for n in self.env.graph.nodes() if self.env.graph.in_degree(n) == 0]
            if not entry_points:
                # If still no entry points, use any node
                entry_points = list(self.env.graph.nodes())[:1]

        if not entry_points or not self.high_value_targets:
            return []

        # Create a plan based on the goal
        if self.campaign_goal in [AttackGoal.DATA_THEFT, AttackGoal.ESPIONAGE]:
            self.attack_path = self._plan_data_theft_attack(entry_points)
        elif self.campaign_goal == AttackGoal.PERSISTENCE:
            self.attack_path = self._plan_persistence_attack(entry_points)
        elif self.campaign_goal == AttackGoal.DISRUPTION:
            self.attack_path = self._plan_disruption_attack(entry_points)
        elif self.campaign_goal == AttackGoal.RANSOMWARE:
            self.attack_path = self._plan_ransomware_attack(entry_points)

        return self.attack_path

    def _plan_data_theft_attack(self, entry_points):
        """Plan an attack path focused on data theft"""
        attack_path = []

        # Find shortest paths to high-value targets
        for target in self.high_value_targets:
            for entry in entry_points:
                try:
                    # Find shortest path from entry to target
                    path = nx.shortest_path(self.env.graph, entry, target)

                    # Add phases to the attack path
                    attack_path.append({
                        "phase": AttackPhase.INITIAL_ACCESS.value,
                        "node": entry,
                        "techniques": self._get_techniques_for_phase(AttackPhase.INITIAL_ACCESS)
                    })

                    # Add lateral movement for intermediate nodes
                    for i in range(1, len(path) - 1):
                        attack_path.append({
                            "phase": AttackPhase.LATERAL_MOVEMENT.value,
                            "node": path[i],
                            "techniques": self._get_techniques_for_phase(AttackPhase.LATERAL_MOVEMENT)
                        })

                    # Add collection and exfiltration for the target
                    attack_path.append({
                        "phase": AttackPhase.COLLECTION.value,
                        "node": target,
                        "techniques": self._get_techniques_for_phase(AttackPhase.COLLECTION)
                    })

                    attack_path.append({
                        "phase": AttackPhase.EXFILTRATION.value,
                        "node": target,
                        "techniques": self._get_techniques_for_phase(AttackPhase.EXFILTRATION)
                    })

                    # We found a path, no need to check other entries
                    break
                except nx.NetworkXNoPath:
                    # No path from this entry to target, try another entry
                    continue

        return attack_path

    def _plan_persistence_attack(self, entry_points):
        """Plan an attack path focused on establishing persistence"""
        # Similar implementation to _plan_data_theft_attack but with focus on persistence
        # Implementation details would go here
        return []

    def _plan_disruption_attack(self, entry_points):
        """Plan an attack path focused on disruption"""
        # Implementation details would go here
        return []

    def _plan_ransomware_attack(self, entry_points):
        """Plan an attack path focused on ransomware deployment"""
        # Implementation details would go here
        return []

    def _get_techniques_for_phase(self, phase):
        """Get appropriate techniques for a given attack phase"""
        if isinstance(phase, AttackPhase):
            phase_value = phase.value
        else:
            phase_value = phase

        # Get techniques from threat intel if available
        techniques = self.threat_intel.get("techniques", {}).get(phase_value, [])

        if not techniques:
            # Fallback to default techniques
            if phase_value == AttackPhase.INITIAL_ACCESS.value:
                techniques = ["phishing", "exploit_public_facing_application"]
            elif phase_value == AttackPhase.LATERAL_MOVEMENT.value:
                techniques = ["remote_services", "pass_the_hash"]
            elif phase_value == AttackPhase.COLLECTION.value:
                techniques = ["data_from_local_system", "data_staged"]
            elif phase_value == AttackPhase.EXFILTRATION.value:
                techniques = ["exfiltration_over_c2_channel", "scheduled_transfer"]
            else:
                techniques = ["default_technique"]

        # Return a subset of techniques based on skill level
        num_techniques = max(1, int(len(techniques) * self.skill_level))
        return random.sample(techniques, min(num_techniques, len(techniques)))

    def get_next_action(self, current_position):
        """
        Get the next action in the attack path based on current position
        and campaign progress.
        """
        # If no attack path or all actions completed, generate a new plan
        if not self.attack_path:
            self.plan_attack_path()

        # Find the next action that hasn't been completed
        for action in self.attack_path:
            # Skip actions for nodes we can't reach
            if current_position is not None:
                try:
                    # Check if we can reach this node from current position
                    path = nx.shortest_path(self.env.graph, current_position, action["node"])
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    # Can't reach this node, skip it
                    continue

            # Return the action
            return action

        # If we've completed all actions or can't reach any remaining actions,
        # return None to indicate we need a new plan
        return None
