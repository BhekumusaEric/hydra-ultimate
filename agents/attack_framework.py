"""
Attack Framework Module for HYDRA

This module defines common enums and constants used across the attack simulation components.
It provides a shared framework for tactics, techniques, and procedures based on the MITRE ATT&CK framework.
"""

from enum import Enum

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
    COMMAND_AND_CONTROL = "command_and_control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"

# MITRE ATT&CK Framework Techniques
class ATTCKTechnique:
    # Initial Access
    DRIVE_BY_COMPROMISE = "drive_by_compromise"
    EXPLOIT_PUBLIC_FACING_APPLICATION = "exploit_public_facing_application"
    EXTERNAL_REMOTE_SERVICES = "external_remote_services"
    HARDWARE_ADDITIONS = "hardware_additions"
    PHISHING = "phishing"
    REPLICATION_THROUGH_REMOVABLE_MEDIA = "replication_through_removable_media"
    SUPPLY_CHAIN_COMPROMISE = "supply_chain_compromise"
    TRUSTED_RELATIONSHIP = "trusted_relationship"
    VALID_ACCOUNTS = "valid_accounts"

    # Execution
    COMMAND_AND_SCRIPTING_INTERPRETER = "command_and_scripting_interpreter"
    CONTAINER_ADMINISTRATION_COMMAND = "container_administration_command"
    DEPLOY_CONTAINER = "deploy_container"
    EXPLOITATION_FOR_CLIENT_EXECUTION = "exploitation_for_client_execution"
    INTER_PROCESS_COMMUNICATION = "inter_process_communication"
    NATIVE_API = "native_api"
    SCHEDULED_TASK_JOB = "scheduled_task_job"
    SHARED_MODULES = "shared_modules"
    SOFTWARE_DEPLOYMENT_TOOLS = "software_deployment_tools"
    SYSTEM_SERVICES = "system_services"
    USER_EXECUTION = "user_execution"
    WINDOWS_MANAGEMENT_INSTRUMENTATION = "windows_management_instrumentation"
    REGSVR32 = "regsvr32"
    MSHTA = "mshta"
    RUNDLL32 = "rundll32"
    SIGNED_BINARY_PROXY_EXECUTION = "signed_binary_proxy_execution"
    BITS_JOBS = "bits_jobs"
    REFLECTIVE_CODE_LOADING = "reflective_code_loading"

    # Persistence
    ACCOUNT_MANIPULATION = "account_manipulation"
    BOOT_OR_LOGON_AUTOSTART_EXECUTION = "boot_or_logon_autostart_execution"
    BROWSER_EXTENSIONS = "browser_extensions"
    COMPROMISE_CLIENT_SOFTWARE_BINARY = "compromise_client_software_binary"
    CREATE_ACCOUNT = "create_account"
    CREATE_OR_MODIFY_SYSTEM_PROCESS = "create_or_modify_system_process"
    EVENT_TRIGGERED_EXECUTION = "event_triggered_execution"
    EXTERNAL_REMOTE_SERVICES = "external_remote_services"
    HIJACK_EXECUTION_FLOW = "hijack_execution_flow"
    IMPLANT_CONTAINER_IMAGE = "implant_container_image"
    OFFICE_APPLICATION_STARTUP = "office_application_startup"
    PRE_OS_BOOT = "pre_os_boot"
    SCHEDULED_TASK_JOB = "scheduled_task_job"
    SERVER_SOFTWARE_COMPONENT = "server_software_component"
    TRAFFIC_SIGNALING = "traffic_signaling"
    VALID_ACCOUNTS = "valid_accounts"
    REGISTRY_RUN_KEYS_STARTUP_FOLDER = "registry_run_keys_startup_folder"
    SCHEDULED_TASK = "scheduled_task"

    # Privilege Escalation
    ABUSE_ELEVATION_CONTROL_MECHANISM = "abuse_elevation_control_mechanism"
    ACCESS_TOKEN_MANIPULATION = "access_token_manipulation"
    BOOT_OR_LOGON_AUTOSTART_EXECUTION = "boot_or_logon_autostart_execution"
    DOMAIN_POLICY_MODIFICATION = "domain_policy_modification"
    ESCAPE_TO_HOST = "escape_to_host"
    EVENT_TRIGGERED_EXECUTION = "event_triggered_execution"
    EXPLOITATION_FOR_PRIVILEGE_ESCALATION = "exploitation_for_privilege_escalation"
    HIJACK_EXECUTION_FLOW = "hijack_execution_flow"
    PROCESS_INJECTION = "process_injection"
    SCHEDULED_TASK_JOB = "scheduled_task_job"
    VALID_ACCOUNTS = "valid_accounts"

    # Defense Evasion
    ABUSE_ELEVATION_CONTROL_MECHANISM = "abuse_elevation_control_mechanism"
    ACCESS_TOKEN_MANIPULATION = "access_token_manipulation"
    OBFUSCATED_FILES_OR_INFORMATION = "obfuscated_files_or_information"
    MASQUERADING = "masquerading"
    MODIFY_REGISTRY = "modify_registry"
    ROOTKIT = "rootkit"
    INDICATOR_REMOVAL = "indicator_removal"
    IMPAIR_DEFENSES = "impair_defenses"
    HIDE_ARTIFACTS = "hide_artifacts"
    EXPLOIT_VULNERABILITY = "exploit_vulnerability"

    # Credential Access
    BRUTE_FORCE = "brute_force"
    CREDENTIAL_DUMPING = "credential_dumping"
    CREDENTIALS_FROM_PASSWORD_STORES = "credentials_from_password_stores"
    FORCED_AUTHENTICATION = "forced_authentication"
    FORGE_WEB_CREDENTIALS = "forge_web_credentials"
    KERBEROASTING = "kerberoasting"
    LLMNR_NBT_NS_POISONING = "llmnr_nbt_ns_poisoning"
    MULTI_FACTOR_AUTHENTICATION_INTERCEPTION = "multi_factor_authentication_interception"
    NETWORK_SNIFFING = "network_sniffing"
    OS_CREDENTIAL_DUMPING = "os_credential_dumping"
    STEAL_WEB_SESSION_COOKIE = "steal_web_session_cookie"
    PASSWORD_SPRAYING = "password_spraying"
    INPUT_CAPTURE = "input_capture"
    PASS_THE_HASH = "pass_the_hash"
    PASS_THE_TICKET = "pass_the_ticket"
    FORGE_KERBEROS_TICKETS = "forge_kerberos_tickets"

    # Discovery
    ACCOUNT_DISCOVERY = "account_discovery"
    APPLICATION_WINDOW_DISCOVERY = "application_window_discovery"
    BROWSER_INFORMATION_DISCOVERY = "browser_information_discovery"
    CLOUD_INFRASTRUCTURE_DISCOVERY = "cloud_infrastructure_discovery"
    CLOUD_SERVICE_DASHBOARD = "cloud_service_dashboard"
    CLOUD_SERVICE_DISCOVERY = "cloud_service_discovery"
    CONTAINER_AND_RESOURCE_DISCOVERY = "container_and_resource_discovery"
    DOMAIN_TRUST_DISCOVERY = "domain_trust_discovery"
    FILE_AND_DIRECTORY_DISCOVERY = "file_and_directory_discovery"
    NETWORK_SERVICE_SCANNING = "network_service_scanning"
    NETWORK_SHARE_DISCOVERY = "network_share_discovery"
    NETWORK_SNIFFING = "network_sniffing"
    PASSWORD_POLICY_DISCOVERY = "password_policy_discovery"
    PERIPHERAL_DEVICE_DISCOVERY = "peripheral_device_discovery"
    PERMISSION_GROUPS_DISCOVERY = "permission_groups_discovery"
    PROCESS_DISCOVERY = "process_discovery"
    QUERY_REGISTRY = "query_registry"
    REMOTE_SYSTEM_DISCOVERY = "remote_system_discovery"
    SOFTWARE_DISCOVERY = "software_discovery"
    SYSTEM_INFORMATION_DISCOVERY = "system_information_discovery"
    SYSTEM_LOCATION_DISCOVERY = "system_location_discovery"
    SYSTEM_NETWORK_CONFIGURATION_DISCOVERY = "system_network_configuration_discovery"
    SYSTEM_NETWORK_CONNECTIONS_DISCOVERY = "system_network_connections_discovery"
    SYSTEM_OWNER_USER_DISCOVERY = "system_owner_user_discovery"
    SYSTEM_SERVICE_DISCOVERY = "system_service_discovery"
    SYSTEM_TIME_DISCOVERY = "system_time_discovery"
    VIRTUALIZATION_SANDBOX_EVASION = "virtualization_sandbox_evasion"

    # Lateral Movement
    EXPLOITATION_OF_REMOTE_SERVICES = "exploitation_of_remote_services"
    INTERNAL_SPEARPHISHING = "internal_spearphishing"
    LATERAL_TOOL_TRANSFER = "lateral_tool_transfer"
    REMOTE_SERVICE_SESSION_HIJACKING = "remote_service_session_hijacking"
    REMOTE_SERVICES = "remote_services"
    REPLICATION_THROUGH_REMOVABLE_MEDIA = "replication_through_removable_media"
    SOFTWARE_DEPLOYMENT_TOOLS = "software_deployment_tools"
    TAINT_SHARED_CONTENT = "taint_shared_content"
    USE_ALTERNATE_AUTHENTICATION_MATERIAL = "use_alternate_authentication_material"

    # Collection
    ADVERSARY_IN_THE_MIDDLE = "adversary_in_the_middle"
    ARCHIVE_COLLECTED_DATA = "archive_collected_data"
    AUDIO_CAPTURE = "audio_capture"
    AUTOMATED_COLLECTION = "automated_collection"
    BROWSER_SESSION_HIJACKING = "browser_session_hijacking"
    CLIPBOARD_DATA = "clipboard_data"
    DATA_FROM_CLOUD_STORAGE_OBJECT = "data_from_cloud_storage_object"
    DATA_FROM_CONFIGURATION_REPOSITORY = "data_from_configuration_repository"
    DATA_FROM_INFORMATION_REPOSITORIES = "data_from_information_repositories"
    DATA_FROM_LOCAL_SYSTEM = "data_from_local_system"
    DATA_FROM_NETWORK_SHARED_DRIVE = "data_from_network_shared_drive"
    DATA_FROM_REMOVABLE_MEDIA = "data_from_removable_media"
    DATA_STAGED = "data_staged"
    EMAIL_COLLECTION = "email_collection"
    INPUT_CAPTURE = "input_capture"
    SCREEN_CAPTURE = "screen_capture"
    VIDEO_CAPTURE = "video_capture"

    # Command and Control
    APPLICATION_LAYER_PROTOCOL = "application_layer_protocol"
    COMMUNICATION_THROUGH_REMOVABLE_MEDIA = "communication_through_removable_media"
    DATA_ENCODING = "data_encoding"
    DATA_OBFUSCATION = "data_obfuscation"
    DYNAMIC_RESOLUTION = "dynamic_resolution"
    ENCRYPTED_CHANNEL = "encrypted_channel"
    FALLBACK_CHANNELS = "fallback_channels"
    INGRESS_TOOL_TRANSFER = "ingress_tool_transfer"
    NON_APPLICATION_LAYER_PROTOCOL = "non_application_layer_protocol"
    NON_STANDARD_PORT = "non_standard_port"
    PROTOCOL_TUNNELING = "protocol_tunneling"
    PROXY = "proxy"
    REMOTE_ACCESS_SOFTWARE = "remote_access_software"
    TRAFFIC_SIGNALING = "traffic_signaling"
    WEB_SERVICE = "web_service"

    # Exfiltration
    AUTOMATED_EXFILTRATION = "automated_exfiltration"
    DATA_TRANSFER_SIZE_LIMITS = "data_transfer_size_limits"
    EXFILTRATION_OVER_ALTERNATIVE_PROTOCOL = "exfiltration_over_alternative_protocol"
    EXFILTRATION_OVER_BLUETOOTH = "exfiltration_over_bluetooth"
    EXFILTRATION_OVER_C2_CHANNEL = "exfiltration_over_c2_channel"
    EXFILTRATION_OVER_OTHER_NETWORK_MEDIUM = "exfiltration_over_other_network_medium"
    EXFILTRATION_OVER_PHYSICAL_MEDIUM = "exfiltration_over_physical_medium"
    EXFILTRATION_OVER_WEB_SERVICE = "exfiltration_over_web_service"
    SCHEDULED_TRANSFER = "scheduled_transfer"
    TRANSFER_DATA_TO_CLOUD_ACCOUNT = "transfer_data_to_cloud_account"

    # Impact
    ACCOUNT_ACCESS_REMOVAL = "account_access_removal"
    DATA_DESTRUCTION = "data_destruction"
    DATA_ENCRYPTED_FOR_IMPACT = "data_encrypted_for_impact"
    DATA_MANIPULATION = "data_manipulation"
    DEFACEMENT = "defacement"
    DENIAL_OF_SERVICE = "denial_of_service"
    DISK_WIPE = "disk_wipe"
    ENDPOINT_DENIAL_OF_SERVICE = "endpoint_denial_of_service"
    FIRMWARE_CORRUPTION = "firmware_corruption"
    INHIBIT_SYSTEM_RECOVERY = "inhibit_system_recovery"
    NETWORK_DENIAL_OF_SERVICE = "network_denial_of_service"
    RESOURCE_HIJACKING = "resource_hijacking"
    SERVICE_STOP = "service_stop"
    SYSTEM_SHUTDOWN_REBOOT = "system_shutdown_reboot"

# Mapping of techniques to vulnerability types
TECHNIQUE_TO_VULNERABILITY = {
    ATTCKTechnique.EXPLOIT_PUBLIC_FACING_APPLICATION: ["unpatched_cve", "buffer_overflow"],
    ATTCKTechnique.VALID_ACCOUNTS: ["default_credentials"],
    ATTCKTechnique.PHISHING: ["cross_site_scripting"],
    ATTCKTechnique.ACCESS_TOKEN_MANIPULATION: ["privilege_escalation"],
    ATTCKTechnique.MASQUERADING: ["misconfiguration"],
    ATTCKTechnique.EXPLOIT_VULNERABILITY: ["unpatched_cve", "buffer_overflow", "sql_injection"],
    ATTCKTechnique.BRUTE_FORCE: ["default_credentials"],
    ATTCKTechnique.NETWORK_SERVICE_SCANNING: ["misconfiguration"],
    ATTCKTechnique.REMOTE_SERVICES: ["default_credentials", "misconfiguration"],
    ATTCKTechnique.DATA_FROM_LOCAL_SYSTEM: ["privilege_escalation"],
    ATTCKTechnique.DATA_STAGED: ["privilege_escalation"],
    ATTCKTechnique.EXFILTRATION_OVER_C2_CHANNEL: ["privilege_escalation"],
    ATTCKTechnique.SCHEDULED_TRANSFER: ["privilege_escalation"],
    ATTCKTechnique.DATA_ENCRYPTED_FOR_IMPACT: ["privilege_escalation"],
    ATTCKTechnique.SERVICE_STOP: ["privilege_escalation"],

    # Credential Access
    ATTCKTechnique.OS_CREDENTIAL_DUMPING: ["privilege_escalation"],
    ATTCKTechnique.CREDENTIALS_FROM_PASSWORD_STORES: ["privilege_escalation"],
    ATTCKTechnique.KERBEROASTING: ["default_credentials"],
    ATTCKTechnique.PASSWORD_SPRAYING: ["default_credentials"],
    ATTCKTechnique.PASS_THE_HASH: ["privilege_escalation"],
    ATTCKTechnique.PASS_THE_TICKET: ["privilege_escalation"],
    ATTCKTechnique.FORGE_KERBEROS_TICKETS: ["privilege_escalation"],

    # Living Off The Land
    ATTCKTechnique.COMMAND_AND_SCRIPTING_INTERPRETER: ["misconfiguration"],
    ATTCKTechnique.WINDOWS_MANAGEMENT_INSTRUMENTATION: ["misconfiguration"],
    ATTCKTechnique.REGSVR32: ["misconfiguration"],
    ATTCKTechnique.RUNDLL32: ["misconfiguration"],
    ATTCKTechnique.MSHTA: ["misconfiguration"],
    ATTCKTechnique.SIGNED_BINARY_PROXY_EXECUTION: ["misconfiguration"],
    ATTCKTechnique.SCHEDULED_TASK: ["misconfiguration"],
    ATTCKTechnique.REGISTRY_RUN_KEYS_STARTUP_FOLDER: ["misconfiguration"]
}
