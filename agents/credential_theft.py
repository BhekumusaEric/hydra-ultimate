"""
Credential Theft Module for HYDRA

This module implements advanced credential theft techniques for the red agent,
simulating real-world credential harvesting methods used by threat actors.
"""

import random
import time
from datetime import datetime
from enum import Enum
import json
import os

# Import attack framework
from agents.attack_framework import ATTCKTactic, ATTCKTechnique

class CredentialTheftTechnique(Enum):
    """Enum for credential theft techniques"""
    MIMIKATZ = "mimikatz"
    KERBEROASTING = "kerberoasting"
    NTLM_HASH_EXTRACTION = "ntlm_hash_extraction"
    LSASS_MEMORY_DUMP = "lsass_memory_dump"
    REGISTRY_EXTRACTION = "registry_extraction"
    BROWSER_CREDENTIAL_THEFT = "browser_credential_theft"
    KEYLOGGING = "keylogging"
    CREDENTIAL_PROMPT_SPOOFING = "credential_prompt_spoofing"
    PASSWORD_SPRAYING = "password_spraying"
    BRUTE_FORCE = "brute_force"
    PASS_THE_HASH = "pass_the_hash"
    PASS_THE_TICKET = "pass_the_ticket"
    GOLDEN_TICKET = "golden_ticket"
    SILVER_TICKET = "silver_ticket"
    DPAPI_ABUSE = "dpapi_abuse"

# Mapping credential theft techniques to MITRE ATT&CK techniques
CREDENTIAL_THEFT_TO_ATTCK = {
    CredentialTheftTechnique.MIMIKATZ.value: ATTCKTechnique.OS_CREDENTIAL_DUMPING,
    CredentialTheftTechnique.KERBEROASTING.value: ATTCKTechnique.KERBEROASTING,
    CredentialTheftTechnique.NTLM_HASH_EXTRACTION.value: ATTCKTechnique.OS_CREDENTIAL_DUMPING,
    CredentialTheftTechnique.LSASS_MEMORY_DUMP.value: ATTCKTechnique.OS_CREDENTIAL_DUMPING,
    CredentialTheftTechnique.REGISTRY_EXTRACTION.value: ATTCKTechnique.CREDENTIALS_FROM_PASSWORD_STORES,
    CredentialTheftTechnique.BROWSER_CREDENTIAL_THEFT.value: ATTCKTechnique.CREDENTIALS_FROM_PASSWORD_STORES,
    CredentialTheftTechnique.KEYLOGGING.value: ATTCKTechnique.INPUT_CAPTURE,
    CredentialTheftTechnique.CREDENTIAL_PROMPT_SPOOFING.value: ATTCKTechnique.FORCED_AUTHENTICATION,
    CredentialTheftTechnique.PASSWORD_SPRAYING.value: ATTCKTechnique.BRUTE_FORCE,
    CredentialTheftTechnique.BRUTE_FORCE.value: ATTCKTechnique.BRUTE_FORCE,
    CredentialTheftTechnique.PASS_THE_HASH.value: ATTCKTechnique.PASS_THE_HASH,
    CredentialTheftTechnique.PASS_THE_TICKET.value: ATTCKTechnique.PASS_THE_TICKET,
    CredentialTheftTechnique.GOLDEN_TICKET.value: ATTCKTechnique.FORGE_KERBEROS_TICKETS,
    CredentialTheftTechnique.SILVER_TICKET.value: ATTCKTechnique.FORGE_KERBEROS_TICKETS,
    CredentialTheftTechnique.DPAPI_ABUSE.value: ATTCKTechnique.CREDENTIALS_FROM_PASSWORD_STORES
}

# Mapping OS types to compatible credential theft techniques
OS_TO_CREDENTIAL_THEFT = {
    "Windows": [
        CredentialTheftTechnique.MIMIKATZ.value,
        CredentialTheftTechnique.KERBEROASTING.value,
        CredentialTheftTechnique.NTLM_HASH_EXTRACTION.value,
        CredentialTheftTechnique.LSASS_MEMORY_DUMP.value,
        CredentialTheftTechnique.REGISTRY_EXTRACTION.value,
        CredentialTheftTechnique.BROWSER_CREDENTIAL_THEFT.value,
        CredentialTheftTechnique.KEYLOGGING.value,
        CredentialTheftTechnique.CREDENTIAL_PROMPT_SPOOFING.value,
        CredentialTheftTechnique.PASS_THE_HASH.value,
        CredentialTheftTechnique.PASS_THE_TICKET.value,
        CredentialTheftTechnique.GOLDEN_TICKET.value,
        CredentialTheftTechnique.SILVER_TICKET.value,
        CredentialTheftTechnique.DPAPI_ABUSE.value
    ],
    "Linux": [
        CredentialTheftTechnique.KEYLOGGING.value,
        CredentialTheftTechnique.CREDENTIAL_PROMPT_SPOOFING.value,
        CredentialTheftTechnique.PASSWORD_SPRAYING.value,
        CredentialTheftTechnique.BRUTE_FORCE.value,
        CredentialTheftTechnique.BROWSER_CREDENTIAL_THEFT.value
    ],
    "macOS": [
        CredentialTheftTechnique.KEYLOGGING.value,
        CredentialTheftTechnique.CREDENTIAL_PROMPT_SPOOFING.value,
        CredentialTheftTechnique.PASSWORD_SPRAYING.value,
        CredentialTheftTechnique.BRUTE_FORCE.value,
        CredentialTheftTechnique.BROWSER_CREDENTIAL_THEFT.value
    ]
}

class CredentialTheft:
    """Class for credential theft operations"""
    def __init__(self, env, skill_level=0.7):
        self.env = env
        self.skill_level = skill_level
        self.stolen_credentials = {}  # Format: {node_id: [credential_objects]}
        self.credential_theft_history = []

    def steal_credentials(self, node_id, technique=None):
        """
        Attempt to steal credentials from a node using the specified technique.
        If no technique is specified, one will be selected based on the node's OS.
        Returns a tuple of (success, credentials, detected)
        """
        if node_id not in self.env.compromised_nodes:
            return False, None, False

        # Get node information
        if node_id not in self.env.graph:
            return False, None, False

        node_info = self.env.graph.nodes[node_id]
        os_type = node_info.get('os', {}).get('type', 'Unknown')

        # Select technique if not specified
        if technique is None:
            technique = self._select_credential_theft_technique(os_type)

        # Check if technique is compatible with OS
        if os_type in OS_TO_CREDENTIAL_THEFT and technique not in OS_TO_CREDENTIAL_THEFT[os_type]:
            # Fall back to a compatible technique
            technique = random.choice(OS_TO_CREDENTIAL_THEFT.get(os_type, [CredentialTheftTechnique.BRUTE_FORCE.value]))

        # Calculate success probability based on skill level and security controls
        security_controls = node_info.get('security_controls', [])
        detection_probability = self._calculate_detection_probability(technique, security_controls)
        success_probability = self.skill_level * (1 - detection_probability * 0.5)

        # Determine success and detection
        success = random.random() < success_probability
        detected = random.random() < detection_probability

        # Generate credentials if successful
        credentials = None
        if success:
            credentials = self._generate_credentials(node_id, os_type)
            
            # Store stolen credentials
            if node_id not in self.stolen_credentials:
                self.stolen_credentials[node_id] = []
            self.stolen_credentials[node_id].append(credentials)

            # Log the credential theft
            self.env.logs.append(f"Credentials stolen from node {node_id} using {technique}")
        else:
            # Log the failed attempt
            self.env.logs.append(f"Credential theft attempt failed on node {node_id} using {technique}")

        # Generate an alert if detected
        if detected:
            self.env.alerts.append({
                "type": "credential_theft",
                "node_id": node_id,
                "technique": technique,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # Record the credential theft attempt
        theft_record = {
            "node_id": node_id,
            "technique": technique,
            "success": success,
            "detected": detected,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "attck_technique": CREDENTIAL_THEFT_TO_ATTCK.get(technique, "unknown")
        }
        self.credential_theft_history.append(theft_record)

        return success, credentials, detected

    def _select_credential_theft_technique(self, os_type):
        """Select an appropriate credential theft technique based on OS type"""
        compatible_techniques = OS_TO_CREDENTIAL_THEFT.get(os_type, [CredentialTheftTechnique.BRUTE_FORCE.value])
        return random.choice(compatible_techniques)

    def _calculate_detection_probability(self, technique, security_controls):
        """Calculate the probability of detection based on technique and security controls"""
        base_detection = 0.3  # Base detection probability
        
        # Adjust based on technique (some are stealthier than others)
        if technique in [CredentialTheftTechnique.MIMIKATZ.value, CredentialTheftTechnique.LSASS_MEMORY_DUMP.value]:
            base_detection += 0.2  # Noisy techniques
        elif technique in [CredentialTheftTechnique.PASS_THE_HASH.value, CredentialTheftTechnique.PASS_THE_TICKET.value]:
            base_detection -= 0.1  # Stealthier techniques
            
        # Adjust based on security controls
        if "EDR" in security_controls:
            base_detection += 0.3
        if "Antivirus" in security_controls:
            base_detection += 0.2
        if "File Integrity Monitoring" in security_controls:
            base_detection += 0.1
            
        # Ensure probability is between 0 and 1
        return max(0.1, min(0.9, base_detection))

    def _generate_credentials(self, node_id, os_type):
        """Generate simulated credentials based on node type and OS"""
        node_type = self.env.graph.nodes[node_id].get('type', 'unknown')
        
        # Generate username based on node type
        if node_type == "workstation":
            username = random.choice(["user", "employee", "staff", f"user{random.randint(1, 999)}"])
        elif node_type in ["server", "database"]:
            username = random.choice(["admin", "sysadmin", "dbadmin", "root", "system"])
        else:
            username = random.choice(["admin", "user", f"user{random.randint(1, 999)}"])
            
        # Generate credential type based on OS and technique
        if os_type == "Windows":
            cred_type = random.choice(["password", "ntlm_hash", "kerberos_ticket"])
        else:
            cred_type = random.choice(["password", "ssh_key", "api_token"])
            
        # Generate credential value
        if cred_type == "password":
            value = f"Password{random.randint(100, 999)}!"
        elif cred_type == "ntlm_hash":
            value = f"{random.randint(10000, 99999)}:{random.randint(100000000000000, 999999999999999)}"
        elif cred_type == "kerberos_ticket":
            value = f"ticket_{random.randint(1000000, 9999999)}"
        elif cred_type == "ssh_key":
            value = "ssh-rsa AAAA...truncated"
        else:
            value = f"token_{random.randint(10000, 99999)}"
            
        return {
            "username": username,
            "type": cred_type,
            "value": value,
            "source_node": node_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_credential_theft_report(self):
        """Generate a report of credential theft activities"""
        return {
            "stolen_credentials": self.stolen_credentials,
            "theft_attempts": len(self.credential_theft_history),
            "successful_thefts": sum(1 for record in self.credential_theft_history if record["success"]),
            "detected_thefts": sum(1 for record in self.credential_theft_history if record["detected"]),
            "techniques_used": list(set(record["technique"] for record in self.credential_theft_history)),
            "attck_techniques": list(set(record["attck_technique"] for record in self.credential_theft_history)),
            "detailed_history": self.credential_theft_history
        }
