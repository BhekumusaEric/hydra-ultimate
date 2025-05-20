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

# Import new components
from agents.attack_planner import AttackPlanner, AttackGoal, AttackPhase
from agents.data_exfiltration import DataExfiltration, DataType, ExfiltrationType

# MITRE ATT&CK Framework Tactics
class ATTCKTactic:
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    EXFILTRATION = "exfiltration"
    COMMAND_AND_CONTROL = "command_and_control"
    IMPACT = "impact"

# MITRE ATT&CK Framework Techniques
class ATTCKTechnique:
    # Initial Access
    PHISHING = "phishing"
    VALID_ACCOUNTS = "valid_accounts"
    EXPLOIT_PUBLIC_FACING_APPLICATION = "exploit_public_facing_application"
    SUPPLY_CHAIN_COMPROMISE = "supply_chain_compromise"
    TRUSTED_RELATIONSHIP = "trusted_relationship"
    SPEARPHISHING_ATTACHMENT = "spearphishing_attachment"
    SPEARPHISHING_LINK = "spearphishing_link"
    HARDWARE_ADDITIONS = "hardware_additions"
    REPLICATION_THROUGH_REMOVABLE_MEDIA = "replication_through_removable_media"
    EXTERNAL_REMOTE_SERVICES = "external_remote_services"

    # Execution
    COMMAND_LINE_INTERFACE = "command_line_interface"
    POWERSHELL = "powershell"
    WINDOWS_MANAGEMENT_INSTRUMENTATION = "windows_management_instrumentation"
    SCHEDULED_TASK = "scheduled_task"
    SCRIPTING = "scripting"
    USER_EXECUTION = "user_execution"
    EXPLOITATION_FOR_CLIENT_EXECUTION = "exploitation_for_client_execution"
    ASEP_MODIFICATION = "asep_modification"
    CONTAINER_ADMINISTRATION_COMMAND = "container_administration_command"
    SOFTWARE_DEPLOYMENT_TOOLS = "software_deployment_tools"
    NATIVE_API = "native_api"

    # Persistence
    BOOTKIT = "bootkit"
    CREATE_ACCOUNT = "create_account"
    REGISTRY_RUN_KEYS = "registry_run_keys"
    SCHEDULED_TASK_JOB = "scheduled_task_job"
    SERVER_SOFTWARE_COMPONENT = "server_software_component"
    SYSTEMD_SERVICE = "systemd_service"
    VALID_ACCOUNTS_PERSISTENCE = "valid_accounts_persistence"
    HIJACK_EXECUTION_FLOW = "hijack_execution_flow"
    OFFICE_APPLICATION_STARTUP = "office_application_startup"
    PRE_OS_BOOT = "pre_os_boot"

    # Privilege Escalation
    EXPLOIT_VULNERABILITY = "exploit_vulnerability"
    ACCESS_TOKEN_MANIPULATION = "access_token_manipulation"
    BYPASS_UAC = "bypass_user_account_control"
    SUDO_AND_SUDO_CACHING = "sudo_and_sudo_caching"
    SETUID_SETGID = "setuid_setgid"
    PROCESS_INJECTION = "process_injection"
    ESCAPE_TO_HOST = "escape_to_host"
    DOMAIN_POLICY_MODIFICATION = "domain_policy_modification"
    EXPLOITATION_FOR_PRIVILEGE_ESCALATION = "exploitation_for_privilege_escalation"
    EXTRA_WINDOW_MEMORY_INJECTION = "extra_window_memory_injection"

    # Defense Evasion
    OBFUSCATED_FILES = "obfuscated_files_or_information"
    INDICATOR_REMOVAL = "indicator_removal_on_host"
    MASQUERADING = "masquerading"
    ROOTKIT = "rootkit"
    DISABLE_SECURITY_TOOLS = "disable_security_tools"
    IMPAIR_DEFENSES = "impair_defenses"
    LIVING_OFF_THE_LAND = "living_off_the_land"
    MODIFY_REGISTRY = "modify_registry"
    TIMESTOMP = "timestomp"
    VIRTUALIZATION_SANDBOX_EVASION = "virtualization_sandbox_evasion"
    REFLECTIVE_CODE_LOADING = "reflective_code_loading"
    INDIRECT_COMMAND_EXECUTION = "indirect_command_execution"
    FILELESS_EXECUTION = "fileless_execution"
    HIDE_ARTIFACTS = "hide_artifacts"

    # Credential Access
    BRUTE_FORCE = "brute_force"
    CREDENTIAL_DUMPING = "credential_dumping"
    PASSWORD_SPRAYING = "password_spraying"
    CREDENTIALS_FROM_PASSWORD_STORES = "credentials_from_password_stores"
    FORCED_AUTHENTICATION = "forced_authentication"
    FORGE_WEB_CREDENTIALS = "forge_web_credentials"
    KERBEROASTING = "kerberoasting"
    LLMNR_NBT_NS_POISONING = "llmnr_nbt_ns_poisoning"
    MULTI_FACTOR_AUTHENTICATION_INTERCEPTION = "multi_factor_authentication_interception"
    NETWORK_SNIFFING = "network_sniffing"
    OS_CREDENTIAL_DUMPING = "os_credential_dumping"
    STEAL_WEB_SESSION_COOKIE = "steal_web_session_cookie"

    # Discovery
    NETWORK_SHARE_DISCOVERY = "network_share_discovery"
    SYSTEM_INFORMATION_DISCOVERY = "system_information_discovery"
    PROCESS_DISCOVERY = "process_discovery"
    ACCOUNT_DISCOVERY = "account_discovery"
    APPLICATION_WINDOW_DISCOVERY = "application_window_discovery"
    CLOUD_INFRASTRUCTURE_DISCOVERY = "cloud_infrastructure_discovery"
    CLOUD_SERVICE_DASHBOARD = "cloud_service_dashboard"
    CONTAINER_AND_RESOURCE_DISCOVERY = "container_and_resource_discovery"
    DOMAIN_TRUST_DISCOVERY = "domain_trust_discovery"
    FILE_AND_DIRECTORY_DISCOVERY = "file_and_directory_discovery"
    NETWORK_SERVICE_SCANNING = "network_service_scanning"
    PERMISSION_GROUPS_DISCOVERY = "permission_groups_discovery"
    REMOTE_SYSTEM_DISCOVERY = "remote_system_discovery"
    SOFTWARE_DISCOVERY = "software_discovery"
    SYSTEM_NETWORK_CONFIGURATION_DISCOVERY = "system_network_configuration_discovery"
    SYSTEM_OWNER_USER_DISCOVERY = "system_owner_user_discovery"
    VIRTUALIZATION_SANDBOX_DISCOVERY = "virtualization_sandbox_discovery"

    # Lateral Movement
    REMOTE_SERVICES = "remote_services"
    PASS_THE_HASH = "pass_the_hash"
    INTERNAL_SPEARPHISHING = "internal_spearphishing"
    LATERAL_TOOL_TRANSFER = "lateral_tool_transfer"
    PASS_THE_TICKET = "pass_the_ticket"
    REMOTE_SERVICE_SESSION_HIJACKING = "remote_service_session_hijacking"
    TAINT_SHARED_CONTENT = "taint_shared_content"
    USE_ALTERNATE_AUTHENTICATION_MATERIAL = "use_alternate_authentication_material"
    EXPLOITATION_OF_REMOTE_SERVICES = "exploitation_of_remote_services"
    SSH_HIJACKING = "ssh_hijacking"

    # Collection
    DATA_FROM_LOCAL_SYSTEM = "data_from_local_system"
    DATA_STAGED = "data_staged"
    AUTOMATED_COLLECTION = "automated_collection"
    BROWSER_SESSION_HIJACKING = "browser_session_hijacking"
    CLIPBOARD_DATA = "clipboard_data"
    DATA_FROM_CLOUD_STORAGE = "data_from_cloud_storage"
    DATA_FROM_CONFIGURATION_REPOSITORY = "data_from_configuration_repository"
    DATA_FROM_INFORMATION_REPOSITORIES = "data_from_information_repositories"
    DATA_FROM_NETWORK_SHARED_DRIVE = "data_from_network_shared_drive"
    EMAIL_COLLECTION = "email_collection"
    INPUT_CAPTURE = "input_capture"
    SCREEN_CAPTURE = "screen_capture"
    VIDEO_CAPTURE = "video_capture"

    # Exfiltration
    EXFILTRATION_OVER_WEB_SERVICE = "exfiltration_over_web_service"
    EXFILTRATION_OVER_ALTERNATIVE_PROTOCOL = "exfiltration_over_alternative_protocol"
    EXFILTRATION_OVER_BLUETOOTH = "exfiltration_over_bluetooth"
    EXFILTRATION_OVER_C2_CHANNEL = "exfiltration_over_c2_channel"
    EXFILTRATION_OVER_OTHER_NETWORK_MEDIUM = "exfiltration_over_other_network_medium"
    EXFILTRATION_OVER_PHYSICAL_MEDIUM = "exfiltration_over_physical_medium"
    SCHEDULED_TRANSFER = "scheduled_transfer"
    TRANSFER_DATA_TO_CLOUD_ACCOUNT = "transfer_data_to_cloud_account"

    # Command and Control
    WEB_PROTOCOLS = "web_protocols"
    ENCRYPTED_CHANNEL = "encrypted_channel"
    APPLICATION_LAYER_PROTOCOL = "application_layer_protocol"
    COMMUNICATION_THROUGH_REMOVABLE_MEDIA = "communication_through_removable_media"
    DATA_ENCODING = "data_encoding"
    DATA_OBFUSCATION = "data_obfuscation"
    DYNAMIC_RESOLUTION = "dynamic_resolution"
    ENCRYPTED_CHANNEL = "encrypted_channel"
    FALLBACK_CHANNELS = "fallback_channels"
    INGRESS_TOOL_TRANSFER = "ingress_tool_transfer"
    MULTI_STAGE_CHANNELS = "multi_stage_channels"
    NON_APPLICATION_LAYER_PROTOCOL = "non_application_layer_protocol"
    NON_STANDARD_PORT = "non_standard_port"
    PROTOCOL_TUNNELING = "protocol_tunneling"
    PROXY = "proxy"
    REMOTE_ACCESS_SOFTWARE = "remote_access_software"

    # Impact
    DATA_ENCRYPTION = "data_encrypted_for_impact"
    ENDPOINT_DENIAL_OF_SERVICE = "endpoint_denial_of_service"
    ACCOUNT_ACCESS_REMOVAL = "account_access_removal"
    DATA_DESTRUCTION = "data_destruction"
    DATA_MANIPULATION = "data_manipulation"
    DEFACEMENT = "defacement"
    DISK_WIPE = "disk_wipe"
    FIRMWARE_CORRUPTION = "firmware_corruption"
    INHIBIT_SYSTEM_RECOVERY = "inhibit_system_recovery"
    NETWORK_DENIAL_OF_SERVICE = "network_denial_of_service"
    RESOURCE_HIJACKING = "resource_hijacking"
    SERVICE_STOP = "service_stop"
    SYSTEM_SHUTDOWN_REBOOT = "system_shutdown_reboot"

    # Zero-Day Techniques
    ZERO_DAY_PRIVILEGE_ESCALATION = "zero_day_privilege_escalation"
    ZERO_DAY_REMOTE_CODE_EXECUTION = "zero_day_remote_code_execution"
    ZERO_DAY_BROWSER_EXPLOITATION = "zero_day_browser_exploitation"
    ZERO_DAY_KERNEL_EXPLOITATION = "zero_day_kernel_exploitation"
    ZERO_DAY_FIRMWARE_EXPLOITATION = "zero_day_firmware_exploitation"

# Mapping MITRE techniques to HYDRA vulnerability types
TECHNIQUE_TO_VULNERABILITY = {
    ATTCKTechnique.EXPLOIT_PUBLIC_FACING_APPLICATION: ["sql_injection", "cross_site_scripting"],
    ATTCKTechnique.EXPLOIT_VULNERABILITY: ["buffer_overflow", "unpatched_cve"],
    ATTCKTechnique.VALID_ACCOUNTS: ["default_credentials"],
    ATTCKTechnique.ACCESS_TOKEN_MANIPULATION: ["privilege_escalation"],
    ATTCKTechnique.MASQUERADING: ["misconfiguration"]
}

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
        self.techniques = {
            ATTCKTactic.INITIAL_ACCESS: [ATTCKTechnique.PHISHING, ATTCKTechnique.VALID_ACCOUNTS],
            ATTCKTactic.EXECUTION: [ATTCKTechnique.POWERSHELL, ATTCKTechnique.COMMAND_LINE_INTERFACE],
            ATTCKTactic.PRIVILEGE_ESCALATION: [ATTCKTechnique.EXPLOIT_VULNERABILITY, ATTCKTechnique.ACCESS_TOKEN_MANIPULATION],
            ATTCKTactic.DEFENSE_EVASION: [ATTCKTechnique.OBFUSCATED_FILES, ATTCKTechnique.MASQUERADING],
            ATTCKTactic.CREDENTIAL_ACCESS: [ATTCKTechnique.CREDENTIAL_DUMPING],
            ATTCKTactic.LATERAL_MOVEMENT: [ATTCKTechnique.REMOTE_SERVICES, ATTCKTechnique.PASS_THE_HASH]
        }
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
        self.techniques = {
            ATTCKTactic.INITIAL_ACCESS: [ATTCKTechnique.EXPLOIT_PUBLIC_FACING_APPLICATION],
            ATTCKTactic.EXECUTION: [ATTCKTechnique.COMMAND_LINE_INTERFACE, ATTCKTechnique.POWERSHELL],
            ATTCKTactic.PRIVILEGE_ESCALATION: [ATTCKTechnique.EXPLOIT_VULNERABILITY, ATTCKTechnique.BYPASS_UAC],
            ATTCKTactic.DEFENSE_EVASION: [ATTCKTechnique.INDICATOR_REMOVAL],
            ATTCKTactic.CREDENTIAL_ACCESS: [ATTCKTechnique.CREDENTIAL_DUMPING, ATTCKTechnique.BRUTE_FORCE],
            ATTCKTactic.LATERAL_MOVEMENT: [ATTCKTechnique.REMOTE_SERVICES],
            ATTCKTactic.IMPACT: [ATTCKTechnique.DATA_ENCRYPTION]
        }
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
        self.techniques = {
            ATTCKTactic.INITIAL_ACCESS: [ATTCKTechnique.PHISHING, ATTCKTechnique.VALID_ACCOUNTS],
            ATTCKTactic.EXECUTION: [ATTCKTechnique.COMMAND_LINE_INTERFACE],
            ATTCKTactic.PRIVILEGE_ESCALATION: [ATTCKTechnique.EXPLOIT_VULNERABILITY],
            ATTCKTactic.DISCOVERY: [ATTCKTechnique.NETWORK_SHARE_DISCOVERY],
            ATTCKTactic.LATERAL_MOVEMENT: [ATTCKTechnique.REMOTE_SERVICES],
            ATTCKTactic.COLLECTION: [ATTCKTechnique.DATA_FROM_LOCAL_SYSTEM],
            ATTCKTactic.EXFILTRATION: [ATTCKTechnique.EXFILTRATION_OVER_WEB_SERVICE],
            ATTCKTactic.IMPACT: [ATTCKTechnique.DATA_ENCRYPTION]
        }
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

        # Check if we can reach high-value targets directly
        neighbor_databases = [n for n in neighbors if n in databases]
        if neighbor_databases:
            return random.choice(neighbor_databases)

        neighbor_servers = [n for n in neighbors if n in servers]
        if neighbor_servers:
            return random.choice(neighbor_servers)

        neighbor_workstations = [n for n in neighbors if n in workstations]
        if neighbor_workstations:
            return random.choice(neighbor_workstations)

        # If no preferred targets in neighbors, move to any neighbor
        if neighbors:
            return random.choice(neighbors)

        # Fallback to random node
        return random.choice(all_nodes)

    def select_attack_type(self, env, target_node):
        """Select attack type focused on gaining execution rights"""
        # Ransomware prefers vulnerabilities that allow code execution
        preferred_vulns = ["buffer_overflow", "unpatched_cve", "privilege_escalation"]

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
        """Load threat intelligence data from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                self.threat_intelligence = json.load(f)
                print(f"Loaded threat intelligence from {file_path}")
        except Exception as e:
            print(f"Error loading threat intelligence: {e}")
            self.threat_intelligence = {}

    def get_state_features(self):
        """Extract enhanced features from the current environment state"""
        features = []

        # Feature 1: Percentage of nodes compromised
        total_nodes = len(self.env.graph.nodes())
        features.append(len(self.compromised_nodes) / max(1, total_nodes))

        # Feature 2: Current position type (encoded)
        if self.current_position is not None:
            node_type = self.env.graph.nodes[self.current_position]['type']
            type_encoding = {
                "workstation": 0.2,
                "server": 0.4,
                "router": 0.6,
                "firewall": 0.8,
                "database": 1.0,
                "cloud_instance": 0.7
            }
            features.append(type_encoding.get(node_type, 0.0))
        else:
            features.append(0.0)

        # Feature 3: Number of neighbors
        if self.current_position is not None:
            neighbors = list(self.env.graph.successors(self.current_position))
            features.append(len(neighbors) / 10.0)  # Normalize
        else:
            features.append(0.0)

        # Feature 4: Average security level of neighbors
        if self.current_position is not None and hasattr(self, 'neighbors') and len(neighbors) > 0:
            security_levels = []
            for node in neighbors:
                controls = len(self.env.graph.nodes[node]['security_controls'])
                security_levels.append(controls)
            features.append(sum(security_levels) / max(1, len(security_levels)) / 5.0)  # Normalize
        else:
            features.append(0.5)  # Default

        # Feature 5: Success rate of recent attacks
        if self.attack_history:
            recent_history = self.attack_history[-10:]
            success_rate = sum(1 for a in recent_history if a['success']) / len(recent_history)
            features.append(success_rate)
        else:
            features.append(0.5)  # Default

        # Feature 6: Campaign progress
        features.append(self.campaign_progress)

        # Feature 7: Campaign goal (encoded)
        goal_encoding = {
            "data_theft": 0.25,
            "persistence": 0.5,
            "disruption": 0.75,
            "ransomware": 1.0
        }
        features.append(goal_encoding.get(self.campaign_goal, 0.5))

        # Feature 8: Time elapsed in campaign (normalized)
        elapsed_time = time.time() - self.campaign_start_time
        features.append(min(1.0, elapsed_time / 3600.0))  # Normalize to 1 hour

        # Feature 9: Number of high-value targets compromised
        high_value_types = ["database", "server"]
        high_value_compromised = sum(1 for n in self.compromised_nodes
                                    if self.env.graph.nodes[n]['type'] in high_value_types)
        features.append(high_value_compromised / max(1, len([n for n in self.env.graph.nodes()
                                                           if self.env.graph.nodes[n]['type'] in high_value_types])))

        # Feature 10: Detection rate
        if self.attack_history:
            recent_history = self.attack_history[-20:]
            detected_attacks = sum(1 for a in recent_history if a.get('detected', False))
            detection_rate = detected_attacks / len(recent_history)
            features.append(detection_rate)
        else:
            features.append(0.3)  # Default

        # Pad to ensure consistent length
        while len(features) < 15:
            features.append(0.0)

        return features[:15]  # Ensure exactly 15 features

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

            # Deploy persistence mechanisms
            if self.campaign_goal == "persistence" or random.random() < 0.3:
                self._deploy_persistence_mechanism(target_node)

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

        # Probability increases with failed attempts
        failed_attempts = sum(1 for a in target_attempts if not a['success'])
        zero_day_probability = min(0.8, 0.2 + (failed_attempts * 0.15))

        if random.random() < zero_day_probability:
            self.zero_day_usage_count += 1
            return True

        return False

    def _select_zero_day_attack(self):
        """Select a zero-day attack type"""
        zero_day_attacks = [
            ATTCKTechnique.ZERO_DAY_PRIVILEGE_ESCALATION,
            ATTCKTechnique.ZERO_DAY_REMOTE_CODE_EXECUTION,
            ATTCKTechnique.ZERO_DAY_BROWSER_EXPLOITATION,
            ATTCKTechnique.ZERO_DAY_KERNEL_EXPLOITATION,
            ATTCKTechnique.ZERO_DAY_FIRMWARE_EXPLOITATION
        ]
        return random.choice(zero_day_attacks)

    def _should_use_evasion(self, target_node):
        """Determine if evasion techniques should be used"""
        # Use evasion more often as the campaign progresses
        evasion_probability = 0.3 + (self.campaign_progress * 0.5)

        # Use evasion more often if previous attacks were detected
        recent_detections = [a for a in self.attack_history[-10:] if a.get('detected', False)]
        if recent_detections:
            evasion_probability += len(recent_detections) * 0.05

        # Always use evasion on high-value targets
        if self._is_high_value_target(target_node):
            evasion_probability += 0.2

        return random.random() < min(0.9, evasion_probability)

    def _apply_evasion_techniques(self, target_node):
        """Apply advanced evasion techniques"""
        evasion_techniques = [
            ATTCKTechnique.OBFUSCATED_FILES,
            ATTCKTechnique.INDICATOR_REMOVAL,
            ATTCKTechnique.MASQUERADING,
            ATTCKTechnique.ROOTKIT,
            ATTCKTechnique.DISABLE_SECURITY_TOOLS,
            ATTCKTechnique.IMPAIR_DEFENSES,
            ATTCKTechnique.LIVING_OFF_THE_LAND,
            ATTCKTechnique.VIRTUALIZATION_SANDBOX_EVASION,
            ATTCKTechnique.REFLECTIVE_CODE_LOADING,
            ATTCKTechnique.INDIRECT_COMMAND_EXECUTION,
            ATTCKTechnique.FILELESS_EXECUTION,
            ATTCKTechnique.HIDE_ARTIFACTS
        ]

        # Select 1-3 evasion techniques
        selected_techniques = random.sample(evasion_techniques, random.randint(1, 3))

        # Record evasion techniques used
        if not hasattr(self, 'evasion_techniques_used'):
            self.evasion_techniques_used = {}

        if target_node not in self.evasion_techniques_used:
            self.evasion_techniques_used[target_node] = []

        self.evasion_techniques_used[target_node].extend(selected_techniques)

        return True

    def _is_high_value_target(self, target_node):
        """Determine if a node is a high-value target"""
        if target_node not in self.env.graph:
            return False

        high_value_types = ["database", "domain_controller", "file_server", "server"]
        node_type = self.env.graph.nodes[target_node]['type']

        return node_type in high_value_types

    def _deploy_persistence_mechanism(self, target_node):
        """Deploy persistence mechanisms on compromised node"""
        if not hasattr(self, 'persistence_mechanisms'):
            self.persistence_mechanisms = {}

        persistence_techniques = [
            ATTCKTechnique.BOOTKIT,
            ATTCKTechnique.CREATE_ACCOUNT,
            ATTCKTechnique.REGISTRY_RUN_KEYS,
            ATTCKTechnique.SCHEDULED_TASK_JOB,
            ATTCKTechnique.SERVER_SOFTWARE_COMPONENT,
            ATTCKTechnique.SYSTEMD_SERVICE,
            ATTCKTechnique.VALID_ACCOUNTS_PERSISTENCE,
            ATTCKTechnique.HIJACK_EXECUTION_FLOW,
            ATTCKTechnique.OFFICE_APPLICATION_STARTUP,
            ATTCKTechnique.PRE_OS_BOOT
        ]

        # Select 1-2 persistence techniques
        selected_techniques = random.sample(persistence_techniques, random.randint(1, 2))

        self.persistence_mechanisms[target_node] = selected_techniques

        # Update campaign progress for persistence goal
        if self.campaign_goal == "persistence":
            self.campaign_progress += 0.05
            self.campaign_progress = min(1.0, self.campaign_progress)

    def _establish_backup_access(self, target_node):
        """Establish additional access paths to important nodes"""
        if not hasattr(self, 'backup_access_paths'):
            self.backup_access_paths = {}

        backup_techniques = [
            ATTCKTechnique.CREATE_ACCOUNT,
            ATTCKTechnique.VALID_ACCOUNTS_PERSISTENCE,
            ATTCKTechnique.SSH_HIJACKING,
            ATTCKTechnique.USE_ALTERNATE_AUTHENTICATION_MATERIAL,
            ATTCKTechnique.PASS_THE_HASH,
            ATTCKTechnique.PASS_THE_TICKET
        ]

        selected_technique = random.choice(backup_techniques)

        if target_node not in self.backup_access_paths:
            self.backup_access_paths[target_node] = []

        self.backup_access_paths[target_node].append(selected_technique)

    def _update_campaign_progress(self, target_node):
        """Update campaign progress based on the current goal"""
        if target_node not in self.env.graph:
            return

        node_type = self.env.graph.nodes[target_node]['type']

        if self.campaign_goal == "data_theft":
            # Progress based on high-value data sources compromised
            if node_type == "database":
                self.campaign_progress += 0.2
            elif node_type == "server":
                self.campaign_progress += 0.1

        elif self.campaign_goal == "persistence":
            # Progress based on diversity of compromised systems
            compromised_types = set(self.env.graph.nodes[n]['type'] for n in self.compromised_nodes)
            self.campaign_progress = min(1.0, len(compromised_types) / 5.0)

        elif self.campaign_goal == "disruption" or self.campaign_goal == "ransomware":
            # Progress based on percentage of network compromised
            total_nodes = len(self.env.graph.nodes())
            self.campaign_progress = len(self.compromised_nodes) / total_nodes

        # Cap progress at 1.0
        self.campaign_progress = min(1.0, self.campaign_progress)

    def _collect_data(self, node_id):
        """Simulate data collection from a compromised node"""
        if node_id not in self.env.graph:
            return

        node_type = self.env.graph.nodes[node_id]['type']

        # Different data types based on node type
        if node_type == "database":
            data_types = ["customer_records", "financial_data", "credentials"]
        elif node_type == "server":
            data_types = ["intellectual_property", "emails", "business_plans"]
        elif node_type == "workstation":
            data_types = ["user_documents", "browser_history", "local_credentials"]
        else:
            data_types = ["configuration", "logs"]

        # Collect 1-3 types of data
        collected_data = random.sample(data_types, min(len(data_types), random.randint(1, 3)))

        # Store collected data
        if node_id not in self.data_collected:
            self.data_collected[node_id] = []

        self.data_collected[node_id].extend(collected_data)

    def _calculate_reward(self, success, detected, target_node):
        """Calculate reward based on success, stealth, and target value"""
        base_reward = 1.0 if success else -0.1

        # Penalty for detection
        if detected:
            base_reward -= 0.5

        # Bonus for high-value targets
        if target_node in self.env.graph:
            node_type = self.env.graph.nodes[target_node]['type']
            if node_type == "database":
                base_reward *= 2.0
            elif node_type == "server":
                base_reward *= 1.5
            elif node_type == "domain_controller":
                base_reward *= 2.5
            elif node_type == "file_server":
                base_reward *= 1.8
            elif node_type == "cloud_instance":
                base_reward *= 1.7

        # Bonus for campaign progress
        if self.campaign_progress > 0.5 and success:
            base_reward += 0.5

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

        # Sample batch of experiences
        batch = random.sample(self.memory, batch_size)

        for state, strategy_name, reward, next_state in batch:
            # Convert to tensors
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0)

            # Get current Q values
            current_q = self.model(state_tensor)

            # Get next Q values
            with torch.no_grad():
                next_q = self.model(next_state_tensor)

            # Update Q value for selected strategy
            strategy_idx = list(self.strategies.keys()).index(strategy_name)
            target = current_q.clone()
            target[0, strategy_idx] = reward + self.gamma * torch.max(next_q)

            # Compute loss and update model
            loss = self.criterion(current_q, target)
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

            # Normalize to create probability distribution
            total_success = sum(strategy_success.values())
            if total_success > 0:
                for strategy_name in self.strategies:
                    self.strategy_probs[strategy_name] = strategy_success[strategy_name] / total_success

    def get_compromised_nodes(self):
        """Return the set of compromised nodes"""
        return self.compromised_nodes

    def get_campaign_status(self):
        """Return the current status of the attack campaign"""
        # Calculate attack chain metrics
        attack_chains = self._identify_attack_chains()
        longest_chain = max([len(chain) for chain in attack_chains]) if attack_chains else 0

        # Calculate high-value compromises
        high_value_compromised = sum(1 for node in self.compromised_nodes
                                    if self._is_high_value_target(node))

        # Calculate persistence coverage
        persistence_coverage = len(getattr(self, 'persistence_mechanisms', {})) / max(1, len(self.compromised_nodes))

        # Calculate evasion effectiveness
        evasion_attempts = sum(1 for a in self.attack_history if a.get('evasion', False))
        evasion_success = sum(1 for a in self.attack_history
                             if a.get('evasion', False) and not a.get('detected', False))
        evasion_effectiveness = evasion_success / max(1, evasion_attempts)

        # Calculate zero-day impact
        zero_day_attacks = sum(1 for a in self.attack_history if a.get('zero_day', False))
        zero_day_success = sum(1 for a in self.attack_history
                              if a.get('zero_day', False) and a.get('success', False))

        # Calculate data exfiltration metrics
        data_types_collected = set()
        for node_data in self.data_collected.values():
            data_types_collected.update(node_data)

        return {
            "goal": self.campaign_goal,
            "progress": self.campaign_progress,
            "elapsed_time": time.time() - self.campaign_start_time,
            "compromised_nodes": len(self.compromised_nodes),
            "high_value_compromised": high_value_compromised,
            "data_collected": sum(len(data) for data in self.data_collected.values()),
            "data_types_collected": len(data_types_collected),
            "lateral_movements": len(self.lateral_movement_paths),
            "attack_chains": len(attack_chains),
            "longest_chain": longest_chain,
            "persistence_coverage": persistence_coverage,
            "evasion_effectiveness": evasion_effectiveness,
            "zero_day_attacks": zero_day_attacks,
            "zero_day_success_rate": zero_day_success / max(1, zero_day_attacks),
            "backup_access_paths": len(getattr(self, 'backup_access_paths', {}))
        }

    def _identify_attack_chains(self):
        """Identify distinct attack chains in the campaign"""
        if not self.attack_history:
            return []

        # Group attacks by target to identify chains
        chains = []
        current_chain = []

        for attack in self.attack_history:
            if attack.get('success', False):
                # If this is a continuation of the current chain
                if not current_chain or attack['target'] != current_chain[-1]['target']:
                    current_chain.append(attack)

                    # Check if this completes a chain (reached a high-value target)
                    if self._is_high_value_target(attack['target']):
                        chains.append(current_chain)
                        current_chain = []
            else:
                # Failed attack might end the current chain
                if current_chain and random.random() < 0.5:
                    chains.append(current_chain)
                    current_chain = []

        # Add any remaining chain
        if current_chain:
            chains.append(current_chain)

        return chains

    def reset(self):
        """Reset the agent state but maintain learned knowledge"""
        self.current_position = None
        self.compromised_nodes = set()
        self.data_collected = {}
        self.lateral_movement_paths = []
        self.campaign_goal = self._select_campaign_goal()
        self.campaign_progress = 0.0
        self.campaign_start_time = time.time()
        # Keep attack history and learned parameters
