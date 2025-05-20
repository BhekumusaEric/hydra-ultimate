import networkx as nx
import random
import json
import os
from enum import Enum

class NodeType(Enum):
    WORKSTATION = "workstation"
    SERVER = "server"
    ROUTER = "router"
    FIREWALL = "firewall"
    DATABASE = "database"
    CLOUD_INSTANCE = "cloud_instance"

class VulnerabilityType(Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    BUFFER_OVERFLOW = "buffer_overflow"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNPATCHED_CVE = "unpatched_cve"
    DEFAULT_CREDENTIALS = "default_credentials"
    MISCONFIGURATION = "misconfiguration"

class EnterpriseNetwork:
    def __init__(self, size="medium", complexity="medium", load_from_file=None):
        """
        Initialize an enterprise network simulation.

        Args:
            size: small (10-20 nodes), medium (30-50 nodes), large (100-200 nodes)
            complexity: low, medium, high (affects connectivity and vulnerability density)
            load_from_file: Path to a JSON file to load a pre-configured network
        """
        self.graph = nx.DiGraph()  # Directed graph for network topology
        self.compromised_nodes = set()
        self.patched_nodes = set()
        self.logs = []
        self.alerts = []
        self.traffic_logs = []
        self.size = size
        self.complexity = complexity

        if load_from_file and os.path.exists(load_from_file):
            self._load_from_file(load_from_file)
        else:
            self._generate_network()

    def _generate_network(self):
        """Generate a realistic enterprise network based on size and complexity."""
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

            # Assign vulnerabilities based on complexity
            vulnerabilities = []
            vuln_count = 0
            if self.complexity == "low":
                vuln_chance = 0.1
            elif self.complexity == "medium":
                vuln_chance = 0.3
            else:  # high
                vuln_chance = 0.5

            # Assign random vulnerabilities
            for vuln_type in VulnerabilityType:
                if random.random() < vuln_chance:
                    # Assign severity and exploitability
                    severity = random.uniform(1.0, 10.0)
                    exploitability = random.uniform(0.1, 1.0)
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
                patch_level=random.uniform(0.5, 1.0),
                security_controls=self._generate_security_controls(node_type)
            )

        # Create edges (connections) between nodes
        self._generate_connections()

        # Set entry points
        self.entry_points = [0]  # Firewall is the main entry point

        # Log network creation
        self.logs.append(f"Enterprise network created with {num_nodes} nodes and {self.graph.number_of_edges()} connections")

    def _generate_connections(self):
        """Generate realistic network connections based on node types."""
        nodes = list(self.graph.nodes())

        # Connect all nodes to at least one router
        routers = [n for n in nodes if self.graph.nodes[n]['type'] == NodeType.ROUTER.value]
        firewalls = [n for n in nodes if self.graph.nodes[n]['type'] == NodeType.FIREWALL.value]

        # Connect firewall to routers
        for router in routers:
            for firewall in firewalls:
                self.graph.add_edge(firewall, router, weight=1.0)

        # Connect nodes based on type relationships
        for node in nodes:
            node_type = self.graph.nodes[node]['type']

            # Different connection patterns based on node type
            if node_type == NodeType.WORKSTATION.value:
                # Workstations connect to routers
                for router in routers:
                    if random.random() < 0.7:  # 70% chance to connect to each router
                        self.graph.add_edge(node, router, weight=random.uniform(0.5, 1.0))
                        self.graph.add_edge(router, node, weight=random.uniform(0.5, 1.0))

            elif node_type == NodeType.SERVER.value:
                # Servers connect to routers and databases
                for router in routers:
                    self.graph.add_edge(router, node, weight=random.uniform(0.8, 1.0))
                    self.graph.add_edge(node, router, weight=random.uniform(0.8, 1.0))

                # Connect to some databases
                databases = [n for n in nodes if self.graph.nodes[n]['type'] == NodeType.DATABASE.value]
                for db in databases:
                    if random.random() < 0.4:  # 40% chance to connect to each database
                        self.graph.add_edge(node, db, weight=random.uniform(0.7, 1.0))
                        self.graph.add_edge(db, node, weight=random.uniform(0.7, 1.0))

            elif node_type == NodeType.CLOUD_INSTANCE.value:
                # Cloud instances connect to internet and some servers
                for firewall in firewalls:
                    self.graph.add_edge(firewall, node, weight=random.uniform(0.6, 0.9))
                    self.graph.add_edge(node, firewall, weight=random.uniform(0.6, 0.9))

                # Connect to some servers
                servers = [n for n in nodes if self.graph.nodes[n]['type'] == NodeType.SERVER.value]
                for server in servers:
                    if random.random() < 0.3:  # 30% chance to connect to each server
                        self.graph.add_edge(node, server, weight=random.uniform(0.5, 0.8))
                        self.graph.add_edge(server, node, weight=random.uniform(0.5, 0.8))

    def _generate_services(self, node_type):
        """Generate realistic services based on node type."""
        services = []

        if node_type == NodeType.SERVER:
            potential_services = ["HTTP", "HTTPS", "FTP", "SSH", "SMTP", "DNS", "LDAP"]
            # Servers run 3-5 services
            for _ in range(random.randint(3, 5)):
                if potential_services:
                    service = random.choice(potential_services)
                    potential_services.remove(service)
                    services.append({
                        "name": service,
                        "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 20)}",
                        "port": self._get_default_port(service),
                        "exposed": random.random() < 0.8  # 80% chance of being exposed
                    })

        elif node_type == NodeType.DATABASE:
            db_types = ["MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQL Server"]
            db_type = random.choice(db_types)
            services.append({
                "name": db_type,
                "version": f"{random.randint(5, 12)}.{random.randint(0, 9)}",
                "port": self._get_default_port(db_type),
                "exposed": random.random() < 0.3  # 30% chance of being exposed
            })

        elif node_type == NodeType.WORKSTATION:
            if random.random() < 0.2:  # 20% chance of running a service
                service = random.choice(["HTTP", "FTP", "SSH"])
                services.append({
                    "name": service,
                    "version": f"{random.randint(1, 3)}.{random.randint(0, 9)}",
                    "port": self._get_default_port(service),
                    "exposed": random.random() < 0.5  # 50% chance of being exposed
                })

        return services

    def _get_default_port(self, service):
        """Return the default port for a given service."""
        port_map = {
            "HTTP": 80,
            "HTTPS": 443,
            "FTP": 21,
            "SSH": 22,
            "SMTP": 25,
            "DNS": 53,
            "LDAP": 389,
            "MySQL": 3306,
            "PostgreSQL": 5432,
            "MongoDB": 27017,
            "Oracle": 1521,
            "SQL Server": 1433
        }
        return port_map.get(service, random.randint(8000, 9000))

    def _generate_os(self):
        """Generate a random operating system configuration."""
        os_types = ["Windows", "Linux", "macOS"]
        os_type = random.choice(os_types)

        if os_type == "Windows":
            versions = ["10", "11", "Server 2019", "Server 2022"]
            patches = ["KB5001330", "KB5003173", "KB5004945", "KB5005033"]
        elif os_type == "Linux":
            versions = ["Ubuntu 20.04", "Ubuntu 22.04", "CentOS 7", "RHEL 8", "Debian 11"]
            patches = []
        else:  # macOS
            versions = ["Monterey", "Ventura", "Sonoma"]
            patches = []

        return {
            "type": os_type,
            "version": random.choice(versions),
            "patch_level": random.choice(["Low", "Medium", "High", "Latest"]),
            "installed_patches": random.sample(patches, k=min(random.randint(0, 3), len(patches)))
        }

    def _generate_security_controls(self, node_type):
        """Generate security controls based on node type."""
        controls = []

        # Common controls with varying probabilities
        if random.random() < 0.7:  # 70% chance
            controls.append("Antivirus")

        if random.random() < 0.5:  # 50% chance
            controls.append("Host Firewall")

        if random.random() < 0.3:  # 30% chance
            controls.append("EDR")

        # Type-specific controls
        if node_type == NodeType.SERVER or node_type == NodeType.DATABASE:
            if random.random() < 0.6:
                controls.append("Intrusion Detection")

            if random.random() < 0.4:
                controls.append("File Integrity Monitoring")

        elif node_type == NodeType.FIREWALL:
            controls.append("Packet Inspection")
            if random.random() < 0.7:
                controls.append("IPS")

        return controls

    def _load_from_file(self, file_path):
        """Load network configuration from a JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Create graph from JSON data
        self.graph = nx.node_link_graph(data["graph"])
        self.compromised_nodes = set(data.get("compromised_nodes", []))
        self.patched_nodes = set(data.get("patched_nodes", []))
        self.logs = data.get("logs", [])
        self.alerts = data.get("alerts", [])
        self.entry_points = data.get("entry_points", [0])

        self.logs.append(f"Network loaded from {file_path}")

    def save_to_file(self, file_path):
        """Save the current network state to a JSON file."""
        data = {
            "graph": nx.node_link_data(self.graph),
            "compromised_nodes": list(self.compromised_nodes),
            "patched_nodes": list(self.patched_nodes),
            "logs": self.logs,
            "alerts": self.alerts,
            "entry_points": self.entry_points
        }

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        self.logs.append(f"Network saved to {file_path}")
        return True

    def get_node_info(self, node_id):
        """Get detailed information about a node."""
        if node_id in self.graph:
            return self.graph.nodes[node_id]
        return None

    def get_network_state(self):
        """Get the current state of the network as a feature vector."""
        # Create a feature vector for ML algorithms
        state = []

        for node in sorted(self.graph.nodes()):
            # Node compromised status (1 if compromised, 0 otherwise)
            state.append(1 if node in self.compromised_nodes else 0)

            # Node patched status (1 if patched, 0 otherwise)
            state.append(1 if node in self.patched_nodes else 0)

            # Vulnerability count
            state.append(len(self.graph.nodes[node]['vulnerabilities']))

            # Average vulnerability severity
            vulns = self.graph.nodes[node]['vulnerabilities']
            if vulns:
                avg_severity = sum(v['severity'] for v in vulns) / len(vulns)
                state.append(avg_severity)
            else:
                state.append(0)

        return state

    def attack_node(self, node_id, attack_type, skill_level=0.5):
        """
        Attempt to attack a node with a specific attack type.

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

        # Check if the node has vulnerabilities
        vulnerabilities = node_data['vulnerabilities']
        matching_vulns = [v for v in vulnerabilities if v['type'] == attack_type]

        if not matching_vulns:
            self.logs.append(f"Attack failed: No {attack_type} vulnerability on node {node_id}")
            return False, f"No {attack_type} vulnerability found"

        # Calculate attack success probability
        vuln = matching_vulns[0]  # Use the first matching vulnerability
        base_probability = vuln['exploitability']

        # Adjust based on security controls
        security_controls = node_data['security_controls']
        control_factor = 1.0 - (len(security_controls) * 0.1)  # Each control reduces success by 10%

        # Adjust based on patch level (default to 0 if not present)
        patch_factor = 1.0 - node_data.get('patch_level', 0.0)

        # Final probability calculation
        success_probability = base_probability * control_factor * patch_factor * skill_level

        # Determine if attack succeeds
        success = random.random() < success_probability

        if success:
            self.compromised_nodes.add(node_id)
            self.logs.append(f"Node {node_id} ({node_type}) compromised via {attack_type}")
            self.alerts.append({
                "type": "compromise",
                "node_id": node_id,
                "attack_type": attack_type,
                "timestamp": "now"  # In a real implementation, use actual timestamps
            })
            return True, "Attack successful"
        else:
            self.logs.append(f"Attack failed: {attack_type} on node {node_id}")

            # Determine if the attack was detected
            detection_chance = sum(0.2 for control in security_controls if control in ["Intrusion Detection", "EDR"])
            if random.random() < detection_chance:
                self.alerts.append({
                    "type": "attempt",
                    "node_id": node_id,
                    "attack_type": attack_type,
                    "timestamp": "now"
                })

            return False, "Attack failed"

    def patch_node(self, node_id, vulnerability_type=None):
        """
        Apply security patches to a node.

        Args:
            node_id: ID of the node to patch
            vulnerability_type: Specific vulnerability to patch (None for all)

        Returns:
            success: Whether the patching was successful
        """
        if node_id not in self.graph:
            return False

        node_data = self.graph.nodes[node_id]
        vulnerabilities = node_data['vulnerabilities']

        if vulnerability_type:
            # Patch specific vulnerability type
            for vuln in vulnerabilities:
                if vuln['type'] == vulnerability_type:
                    vuln['patched'] = True

            self.logs.append(f"Patched {vulnerability_type} on node {node_id}")
        else:
            # Patch all vulnerabilities
            for vuln in vulnerabilities:
                vuln['patched'] = True

            self.logs.append(f"Applied all patches to node {node_id}")

        # Update node data
        self.graph.nodes[node_id]['vulnerabilities'] = vulnerabilities
        self.patched_nodes.add(node_id)

        # If node was compromised, there's a chance to remove the compromise
        if node_id in self.compromised_nodes and random.random() < 0.7:
            self.compromised_nodes.remove(node_id)
            self.logs.append(f"Node {node_id} secured after patching")

        return True

    def get_attack_paths(self, target_node):
        """
        Find possible attack paths to a target node from entry points.

        Args:
            target_node: ID of the target node

        Returns:
            paths: List of possible attack paths
        """
        paths = []

        for entry_point in self.entry_points:
            try:
                # Find shortest path from entry point to target
                path = nx.shortest_path(self.graph, entry_point, target_node)
                paths.append(path)
            except nx.NetworkXNoPath:
                # No path exists
                continue

        return paths

    def get_critical_nodes(self):
        """Identify critical nodes in the network based on centrality."""
        # Calculate betweenness centrality
        centrality = nx.betweenness_centrality(self.graph)

        # Get top 10% of nodes by centrality
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        num_critical = max(1, int(len(sorted_nodes) * 0.1))

        return [node for node, _ in sorted_nodes[:num_critical]]

    def simulate_traffic(self, num_events=10):
        """
        Simulate realistic network traffic events with patterns based on node types,
        time of day, and business functions.
        """
        from datetime import datetime
        import time

        nodes = list(self.graph.nodes())
        if len(nodes) < 2:
            return []

        # Get current timestamp for more realistic traffic patterns
        current_time = datetime.now()
        hour = current_time.hour

        # Define traffic patterns based on time of day
        if 9 <= hour <= 17:  # Business hours
            traffic_pattern = "business_hours"
        elif 18 <= hour <= 22:  # Evening
            traffic_pattern = "evening"
        elif 23 <= hour or hour <= 5:  # Night
            traffic_pattern = "night"
        else:  # Early morning
            traffic_pattern = "early_morning"

        # Traffic type distribution based on pattern
        traffic_distributions = {
            "business_hours": {
                "HTTP": 0.35, "HTTPS": 0.25, "DNS": 0.15,
                "Database": 0.15, "SMTP": 0.05, "File Transfer": 0.05
            },
            "evening": {
                "HTTP": 0.25, "HTTPS": 0.30, "DNS": 0.15,
                "Database": 0.10, "SMTP": 0.05, "File Transfer": 0.15
            },
            "night": {
                "HTTP": 0.10, "HTTPS": 0.15, "DNS": 0.10,
                "Database": 0.30, "SMTP": 0.05, "File Transfer": 0.30
            },
            "early_morning": {
                "HTTP": 0.15, "HTTPS": 0.15, "DNS": 0.20,
                "Database": 0.25, "SMTP": 0.10, "File Transfer": 0.15
            }
        }

        # Get distribution for current pattern
        current_distribution = traffic_distributions[traffic_pattern]

        # Generate traffic events
        generated_events = []

        for _ in range(num_events):
            # Select source node with bias toward servers during business hours
            if traffic_pattern == "business_hours" and random.random() < 0.7:
                # Prefer servers and workstations during business hours
                potential_sources = [n for n in nodes if self.graph.nodes[n]['type'] in ['server', 'workstation']]
                if potential_sources:
                    source = random.choice(potential_sources)
                else:
                    source = random.choice(nodes)
            elif traffic_pattern == "night" and random.random() < 0.8:
                # Prefer servers and databases during night (automated processes)
                potential_sources = [n for n in nodes if self.graph.nodes[n]['type'] in ['server', 'database']]
                if potential_sources:
                    source = random.choice(potential_sources)
                else:
                    source = random.choice(nodes)
            else:
                source = random.choice(nodes)

            # Find neighbors that source can reach
            neighbors = list(self.graph.successors(source))
            if not neighbors:
                continue

            # Select destination with bias based on traffic type
            # For example, database traffic should go to database nodes
            traffic_type = self._select_weighted_traffic_type(current_distribution)

            if traffic_type == "Database":
                # Database traffic should target database nodes
                db_nodes = [n for n in neighbors if self.graph.nodes[n]['type'] == 'database']
                if db_nodes:
                    destination = random.choice(db_nodes)
                else:
                    destination = random.choice(neighbors)
            elif traffic_type == "File Transfer":
                # File transfers often target servers
                server_nodes = [n for n in neighbors if self.graph.nodes[n]['type'] == 'server']
                if server_nodes:
                    destination = random.choice(server_nodes)
                else:
                    destination = random.choice(neighbors)
            else:
                destination = random.choice(neighbors)

            # Generate realistic traffic size based on type
            if traffic_type == "DNS":
                size = random.randint(50, 500)  # DNS queries are small
            elif traffic_type == "HTTP" or traffic_type == "HTTPS":
                size = random.randint(1000, 500000)  # Web traffic varies widely
            elif traffic_type == "File Transfer":
                size = random.randint(100000, 10000000)  # File transfers are large
            elif traffic_type == "Database":
                size = random.randint(500, 50000)  # Database queries vary
            elif traffic_type == "SMTP":
                size = random.randint(1000, 100000)  # Emails vary in size
            else:
                size = random.randint(100, 10000)  # Default range

            # Add protocol-specific details
            details = {}
            if traffic_type == "HTTP" or traffic_type == "HTTPS":
                methods = ["GET", "POST", "PUT", "DELETE"]
                weights = [0.7, 0.2, 0.05, 0.05]  # GET is most common
                method = random.choices(methods, weights=weights)[0]
                paths = ["/", "/api/v1/data", "/login", "/dashboard", "/images", "/static/js", "/users"]
                details = {
                    "method": method,
                    "path": random.choice(paths),
                    "status_code": random.choice([200, 200, 200, 200, 404, 500, 403, 401])  # Weighted toward 200
                }
            elif traffic_type == "Database":
                operations = ["SELECT", "INSERT", "UPDATE", "DELETE"]
                weights = [0.8, 0.1, 0.08, 0.02]  # SELECT is most common
                details = {
                    "operation": random.choices(operations, weights=weights)[0],
                    "table": random.choice(["users", "products", "orders", "logs", "transactions"])
                }

            # Check if this is malicious traffic from compromised node
            is_malicious = source in self.compromised_nodes and random.random() < 0.3

            # Add malicious indicators if traffic is malicious
            if is_malicious:
                if traffic_type == "HTTP" or traffic_type == "HTTPS":
                    # Suspicious HTTP patterns
                    suspicious_paths = ["/admin", "/wp-admin", "/phpmyadmin", "/.git", "/etc/passwd"]
                    suspicious_methods = ["POST", "PUT"]  # More likely to be malicious
                    details["path"] = random.choice(suspicious_paths)
                    details["method"] = random.choice(suspicious_methods)
                    if random.random() < 0.3:
                        details["user_agent"] = "Mozilla/5.0 (compatible; MSIE 11.0; Windows NT 6.1; Trident/5.0)"
                elif traffic_type == "Database":
                    # SQL injection patterns
                    details["operation"] = "SELECT"
                    details["query"] = "SELECT * FROM users WHERE username='' OR 1=1; --"
                elif traffic_type == "DNS":
                    # DNS exfiltration or C2
                    details["query"] = f"data{random.randint(1000, 9999)}.evil-domain.com"

            # Create the event with timestamp
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            event = {
                "source": source,
                "destination": destination,
                "type": traffic_type,
                "timestamp": timestamp,
                "size": size,
                "malicious": is_malicious,
                "details": details
            }

            self.traffic_logs.append(event)
            generated_events.append(event)

            # If malicious, generate an alert with some probability
            if is_malicious:
                # Check if there are security controls that might detect this
                source_controls = self.graph.nodes[source].get('security_controls', [])
                dest_controls = self.graph.nodes[destination].get('security_controls', [])

                # Calculate detection probability based on security controls
                detection_base = 0.4  # Base detection rate
                if "Intrusion Detection" in dest_controls:
                    detection_base += 0.3
                if "EDR" in dest_controls:
                    detection_base += 0.2
                if "Packet Inspection" in dest_controls:
                    detection_base += 0.2

                # Stealthy malicious traffic is harder to detect
                if traffic_type == "HTTPS" or traffic_type == "DNS":
                    detection_base *= 0.7

                if random.random() < detection_base:
                    self.alerts.append({
                        "type": "suspicious_traffic",
                        "source": source,
                        "destination": destination,
                        "traffic_type": traffic_type,
                        "timestamp": timestamp,
                        "details": details
                    })

        return generated_events

    def _select_weighted_traffic_type(self, distribution):
        """Select a traffic type based on weighted distribution."""
        types = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(types, weights=weights)[0]
