import random
import numpy as np
from collections import deque, Counter
import torch
import torch.nn as nn
import torch.optim as optim
import networkx as nx

class DefenseStrategy:
    """Base class for defense strategies"""
    def __init__(self, name):
        self.name = name

    def select_actions(self, env, alerts, logs):
        """Select defense actions based on current state"""
        raise NotImplementedError

class ReactiveDefenseStrategy(DefenseStrategy):
    """Reacts to alerts by patching affected nodes"""
    def __init__(self):
        super().__init__("Reactive")

    def select_actions(self, env, alerts, logs):
        """React to alerts by patching affected nodes"""
        actions = []

        # Process recent alerts
        recent_alerts = alerts[-10:] if alerts else []

        for alert in recent_alerts:
            if alert.get('type') == 'compromise' or alert.get('type') == 'attempt':
                node_id = alert.get('node_id')
                attack_type = alert.get('attack_type')

                if node_id is not None:
                    actions.append({
                        'action': 'patch',
                        'node_id': node_id,
                        'vulnerability_type': attack_type
                    })

        return actions

class ProactiveDefenseStrategy(DefenseStrategy):
    """Proactively patches critical nodes"""
    def __init__(self):
        super().__init__("Proactive")

    def select_actions(self, env, alerts, logs):
        """Proactively patch critical nodes"""
        actions = []

        # Identify critical nodes
        critical_nodes = env.get_critical_nodes()

        # Check each critical node for vulnerabilities
        for node_id in critical_nodes:
            if node_id in env.graph:
                node_data = env.graph.nodes[node_id]
                vulnerabilities = node_data.get('vulnerabilities', [])

                # Find unpatched vulnerabilities
                unpatched_vulns = [v for v in vulnerabilities if not v.get('patched', False)]

                if unpatched_vulns:
                    # Patch the most severe vulnerability
                    most_severe = max(unpatched_vulns, key=lambda v: v.get('severity', 0))
                    actions.append({
                        'action': 'patch',
                        'node_id': node_id,
                        'vulnerability_type': most_severe.get('type')
                    })

        return actions

class ThreatHuntingStrategy(DefenseStrategy):
    """Actively hunts for compromised nodes based on traffic analysis"""
    def __init__(self):
        super().__init__("ThreatHunting")

    def select_actions(self, env, alerts, logs):
        """Hunt for threats by analyzing traffic patterns"""
        actions = []

        # Analyze traffic logs for suspicious patterns
        traffic_logs = env.traffic_logs[-50:] if hasattr(env, 'traffic_logs') else []

        # Count traffic by source
        source_counts = Counter(log['source'] for log in traffic_logs)

        # Identify nodes with unusually high traffic
        avg_traffic = sum(source_counts.values()) / max(1, len(source_counts))
        suspicious_nodes = [node for node, count in source_counts.items()
                           if count > avg_traffic * 1.5]

        # Check suspicious nodes
        for node_id in suspicious_nodes:
            if node_id in env.graph:
                actions.append({
                    'action': 'investigate',
                    'node_id': node_id
                })

        return actions

class AdvancedBlueAgent:
    """Advanced Blue Agent with multiple defense strategies and learning capabilities"""
    def __init__(self, env, learning_rate=0.001):
        self.env = env
        self.strategies = {
            "Reactive": ReactiveDefenseStrategy(),
            "Proactive": ProactiveDefenseStrategy(),
            "ThreatHunting": ThreatHuntingStrategy()
        }

        # Strategy selection probabilities
        self.strategy_probs = {
            "Reactive": 0.4,
            "Proactive": 0.3,
            "ThreatHunting": 0.3
        }

        # Track patched nodes and investigations
        self.patched_nodes = set()
        self.investigated_nodes = set()
        self.action_history = []

        # Initialize learning components
        self.learning_rate = learning_rate
        self.memory = deque(maxlen=1000)
        self.gamma = 0.95  # Discount factor

        # Initialize neural network for strategy selection
        self.initialize_network()

        # Threat intelligence database
        self.threat_intelligence = {
            "known_attack_patterns": {},
            "vulnerability_exploitability": {},
            "node_risk_scores": {}
        }

    def initialize_network(self):
        """Initialize neural network for strategy selection"""
        # Network to predict effectiveness of each strategy
        self.model = nn.Sequential(
            nn.Linear(15, 64),  # Input: environment state features
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, len(self.strategies)),
            nn.Softmax(dim=1)
        )

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

    def get_state_features(self):
        """Extract features from the current environment state"""
        features = []

        # Feature 1: Number of recent alerts
        alerts = getattr(self.env, 'alerts', [])
        recent_alerts = alerts[-20:] if alerts else []
        features.append(len(recent_alerts) / 20.0)  # Normalize

        # Feature 2: Types of recent alerts
        alert_types = Counter(alert.get('type', '') for alert in recent_alerts)
        features.append(alert_types.get('compromise', 0) / max(1, len(recent_alerts)))
        features.append(alert_types.get('attempt', 0) / max(1, len(recent_alerts)))
        features.append(alert_types.get('suspicious_traffic', 0) / max(1, len(recent_alerts)))

        # Feature 3: Percentage of nodes patched
        total_nodes = len(self.env.graph.nodes())
        features.append(len(self.patched_nodes) / max(1, total_nodes))

        # Feature 4: Network vulnerability density
        total_vulns = 0
        unpatched_vulns = 0

        for node in self.env.graph.nodes():
            node_data = self.env.graph.nodes[node]
            vulnerabilities = node_data.get('vulnerabilities', [])
            total_vulns += len(vulnerabilities)
            unpatched_vulns += sum(1 for v in vulnerabilities if not v.get('patched', False))

        features.append(unpatched_vulns / max(1, total_vulns))

        # Feature 5: Critical node security
        critical_nodes = self.env.get_critical_nodes()
        critical_node_vulns = 0

        for node in critical_nodes:
            if node in self.env.graph:
                node_data = self.env.graph.nodes[node]
                vulnerabilities = node_data.get('vulnerabilities', [])
                critical_node_vulns += sum(1 for v in vulnerabilities if not v.get('patched', False))

        features.append(critical_node_vulns / max(1, len(critical_nodes)))

        # Feature 6: Recent traffic volume
        traffic_logs = getattr(self.env, 'traffic_logs', [])
        recent_traffic = traffic_logs[-50:] if traffic_logs else []
        features.append(len(recent_traffic) / 50.0)  # Normalize

        # Feature 7: Malicious traffic ratio
        malicious_traffic = sum(1 for log in recent_traffic if log.get('malicious', False))
        features.append(malicious_traffic / max(1, len(recent_traffic)))

        # Feature 8: Success rate of recent actions
        if self.action_history:
            recent_actions = self.action_history[-20:]
            success_rate = sum(1 for a in recent_actions if a.get('success', False)) / len(recent_actions)
            features.append(success_rate)
        else:
            features.append(0.5)  # Default

        # Pad to ensure consistent length
        while len(features) < 15:
            features.append(0.0)

        return features[:15]  # Ensure exactly 15 features

    def select_strategy(self, state_features=None):
        """Select a defense strategy based on current state"""
        if state_features is not None and random.random() > 0.2:  # Exploration rate
            # Use neural network to select strategy
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
        """Execute defense actions"""
        # Get current state features
        state_features = self.get_state_features()

        # Select strategy
        strategy = self.select_strategy(state_features)

        # Get alerts and logs
        alerts = getattr(self.env, 'alerts', [])
        logs = getattr(self.env, 'logs', [])

        # Get actions from strategy
        actions = strategy.select_actions(self.env, alerts, logs)

        # Execute actions
        results = []
        for action in actions:
            action_type = action.get('action')
            node_id = action.get('node_id')

            if action_type == 'patch':
                vulnerability_type = action.get('vulnerability_type')
                success = self.env.patch_node(node_id, vulnerability_type)

                if success:
                    self.patched_nodes.add(node_id)

                results.append({
                    'action': 'patch',
                    'node_id': node_id,
                    'vulnerability_type': vulnerability_type,
                    'success': success
                })

            elif action_type == 'investigate':
                # Simulate investigation
                is_compromised = node_id in getattr(self.env, 'compromised_nodes', set())

                if is_compromised:
                    # Found a compromised node, patch it
                    success = self.env.patch_node(node_id)
                    self.env.logs.append(f"Investigation found compromise on node {node_id}")

                    if hasattr(self.env, 'compromised_nodes'):
                        if node_id in self.env.compromised_nodes:
                            self.env.compromised_nodes.remove(node_id)
                else:
                    success = True  # Investigation completed successfully
                    self.env.logs.append(f"Investigation found no compromise on node {node_id}")

                self.investigated_nodes.add(node_id)

                results.append({
                    'action': 'investigate',
                    'node_id': node_id,
                    'found_compromise': is_compromised,
                    'success': success
                })

        # Record actions in history
        self.action_history.extend(results)

        # Calculate reward based on action results
        reward = sum(1.0 if r.get('success', False) else -0.1 for r in results)

        # Store experience for learning
        next_state_features = self.get_state_features()

        if results:  # Only learn if actions were taken
            self.memory.append((state_features, strategy.name, reward, next_state_features))

        # Learn from experience
        if len(self.memory) > 32:
            self.learn(batch_size=32)

        # Update threat intelligence
        self.update_threat_intelligence()

        return results

    def learn(self, batch_size=32):
        """Learn from past experiences"""
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
        if self.action_history:
            recent_history = self.action_history[-50:]
            strategy_success = {}

            for strategy_name in self.strategies:
                strategy_actions = [a for a in recent_history if a.get('strategy') == strategy_name]
                if strategy_actions:
                    success_rate = sum(1 for a in strategy_actions if a.get('success', True)) / len(strategy_actions)
                    strategy_success[strategy_name] = success_rate
                else:
                    strategy_success[strategy_name] = 0.33  # Default

            # Normalize to create probability distribution
            total_success = sum(strategy_success.values())
            if total_success > 0:
                for strategy_name in self.strategies:
                    self.strategy_probs[strategy_name] = strategy_success[strategy_name] / total_success

    def update_threat_intelligence(self):
        """Update threat intelligence database based on observations"""
        alerts = getattr(self.env, 'alerts', [])
        recent_alerts = alerts[-50:] if alerts else []

        # Update known attack patterns
        for alert in recent_alerts:
            attack_type = alert.get('attack_type')
            if attack_type:
                if attack_type not in self.threat_intelligence['known_attack_patterns']:
                    self.threat_intelligence['known_attack_patterns'][attack_type] = 0
                self.threat_intelligence['known_attack_patterns'][attack_type] += 1

        # Update node risk scores
        for node in self.env.graph.nodes():
            node_data = self.env.graph.nodes[node]

            # Calculate risk based on vulnerabilities
            vulnerabilities = node_data.get('vulnerabilities', [])
            unpatched_vulns = [v for v in vulnerabilities if not v.get('patched', False)]

            # Risk is based on severity and exploitability
            risk_score = sum(v.get('severity', 5.0) * v.get('exploitability', 0.5) for v in unpatched_vulns)

            # Adjust risk based on node type
            node_type = node_data.get('type', '')
            type_multiplier = {
                "database": 2.0,
                "server": 1.5,
                "cloud_instance": 1.3,
                "workstation": 0.8,
                "router": 1.2,
                "firewall": 1.0
            }

            risk_score *= type_multiplier.get(node_type, 1.0)

            # Store risk score
            self.threat_intelligence['node_risk_scores'][node] = risk_score

    def get_patched_nodes(self):
        """Return the set of patched nodes"""
        return self.patched_nodes

    def reset(self):
        """Reset the agent state"""
        self.patched_nodes = set()
        self.investigated_nodes = set()
        # Keep action history and learned parameters
