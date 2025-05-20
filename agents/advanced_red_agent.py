import random
import numpy as np
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim

class AttackStrategy:
    """Base class for attack strategies"""
    def __init__(self, name, skill_level=0.5):
        self.name = name
        self.skill_level = skill_level

    def select_target(self, env, current_position):
        """Select a target node to attack"""
        raise NotImplementedError

    def select_attack_type(self, env, target_node):
        """Select an attack type to use against the target"""
        raise NotImplementedError

class RandomAttackStrategy(AttackStrategy):
    """Randomly selects targets and attack types"""
    def __init__(self, skill_level=0.3):
        super().__init__("Random", skill_level)

    def select_target(self, env, current_position):
        """Randomly select a connected node"""
        # Get all nodes connected to current position
        if current_position is None:
            # Start from an entry point if not positioned
            return random.choice(env.entry_points)

        neighbors = list(env.graph.successors(current_position))
        if not neighbors:
            # No neighbors, try to find any node
            return random.choice(list(env.graph.nodes()))

        return random.choice(neighbors)

    def select_attack_type(self, env, target_node):
        """Randomly select an attack type"""
        # Get vulnerability types from the environment module
        from envs.enterprise_network import VulnerabilityType
        attack_types = [v.value for v in VulnerabilityType]
        return random.choice(attack_types)

class TargetedAttackStrategy(AttackStrategy):
    """Targets specific high-value nodes"""
    def __init__(self, target_types=None, skill_level=0.7):
        super().__init__("Targeted", skill_level)
        self.target_types = target_types or ["database", "server"]

    def select_target(self, env, current_position):
        """Select a high-value target that can be reached"""
        if current_position is None:
            # Start from an entry point if not positioned
            return random.choice(env.entry_points)

        # Find all reachable nodes from current position
        reachable_nodes = set()
        queue = deque([current_position])
        visited = set([current_position])

        while queue:
            node = queue.popleft()
            reachable_nodes.add(node)

            for neighbor in env.graph.successors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # Filter for high-value targets
        high_value_targets = []
        for node in reachable_nodes:
            node_type = env.graph.nodes[node]['type']
            if node_type in self.target_types:
                high_value_targets.append(node)

        if high_value_targets:
            return random.choice(high_value_targets)

        # If no high-value targets, choose a random reachable node
        if reachable_nodes:
            return random.choice(list(reachable_nodes))

        # Fallback to random node
        return random.choice(list(env.graph.nodes()))

    def select_attack_type(self, env, target_node):
        """Select an attack type based on target vulnerabilities"""
        # Get vulnerability types from the environment module
        from envs.enterprise_network import VulnerabilityType

        if target_node not in env.graph:
            return random.choice([v.value for v in VulnerabilityType])

        # Check target's vulnerabilities
        vulnerabilities = env.graph.nodes[target_node]['vulnerabilities']

        if vulnerabilities:
            # Choose from existing vulnerabilities
            vuln_types = [v['type'] for v in vulnerabilities]
            return random.choice(vuln_types)

        # Fallback to random attack type
        return random.choice([v.value for v in VulnerabilityType])

class StealthyAttackStrategy(AttackStrategy):
    """Focuses on avoiding detection"""
    def __init__(self, skill_level=0.8):
        super().__init__("Stealthy", skill_level)
        self.detection_history = {}  # Track detection rates

    def select_target(self, env, current_position):
        """Select targets with fewer security controls"""
        if current_position is None:
            # Start from an entry point if not positioned
            return random.choice(env.entry_points)

        # Get neighbors
        neighbors = list(env.graph.successors(current_position))
        if not neighbors:
            return random.choice(list(env.graph.nodes()))

        # Score neighbors by security controls (fewer is better)
        scored_neighbors = []
        for node in neighbors:
            security_controls = env.graph.nodes[node]['security_controls']
            detection_controls = sum(1 for c in security_controls
                                    if c in ["Intrusion Detection", "EDR"])

            # Check detection history
            detection_rate = self.detection_history.get(node, 0.5)

            # Lower score is better (less likely to be detected)
            score = detection_controls + detection_rate
            scored_neighbors.append((node, score))

        # Sort by score (ascending)
        scored_neighbors.sort(key=lambda x: x[1])

        # Select from top 3 or all if fewer
        top_n = min(3, len(scored_neighbors))
        selected_node = random.choice(scored_neighbors[:top_n])[0]

        return selected_node

    def select_attack_type(self, env, target_node):
        """Select less detectable attack types"""
        # Some attack types are considered stealthier
        stealthy_attacks = ["privilege_escalation", "misconfiguration", "default_credentials"]

        if target_node in env.graph:
            # Check target's vulnerabilities
            vulnerabilities = env.graph.nodes[target_node]['vulnerabilities']

            # Filter for stealthy vulnerabilities
            stealthy_vulns = [v for v in vulnerabilities if v['type'] in stealthy_attacks]

            if stealthy_vulns:
                return random.choice(stealthy_vulns)['type']

            # If no stealthy vulnerabilities, use any available
            if vulnerabilities:
                return random.choice(vulnerabilities)['type']

        # Fallback to a stealthy attack type
        return random.choice(stealthy_attacks)

    def update_detection_history(self, node_id, detected):
        """Update detection history for a node"""
        current_rate = self.detection_history.get(node_id, 0.5)
        # Exponential moving average
        self.detection_history[node_id] = 0.7 * current_rate + 0.3 * (1.0 if detected else 0.0)

class AdvancedRedAgent:
    """Advanced Red Agent with multiple attack strategies and learning capabilities"""
    def __init__(self, env, skill_level=0.5, learning_rate=0.001):
        self.env = env
        self.skill_level = skill_level
        self.current_position = None
        self.compromised_nodes = set()
        self.attack_history = []

        # Initialize attack strategies
        self.strategies = {
            "random": RandomAttackStrategy(skill_level * 0.8),
            "targeted": TargetedAttackStrategy(skill_level=skill_level),
            "stealthy": StealthyAttackStrategy(skill_level=skill_level * 1.2)
        }

        # Strategy selection probabilities
        self.strategy_probs = {
            "random": 0.2,
            "targeted": 0.5,
            "stealthy": 0.3
        }

        # Initialize learning components
        self.learning_rate = learning_rate
        self.memory = deque(maxlen=1000)
        self.gamma = 0.95  # Discount factor

        # Initialize neural network for strategy selection
        self.initialize_network()

    def initialize_network(self):
        """Initialize neural network for strategy selection"""
        # Simple network to predict success probability for each strategy
        self.model = nn.Sequential(
            nn.Linear(10, 32),  # Input: network state features
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, len(self.strategies)),
            nn.Softmax(dim=1)
        )

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

    def select_strategy(self, state_features=None):
        """Select an attack strategy based on current state"""
        if state_features is not None and random.random() > 0.3:  # Exploration rate
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

    def get_state_features(self):
        """Extract features from the current environment state"""
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
        if self.current_position is not None and len(neighbors) > 0:
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

        # Pad to ensure consistent length
        while len(features) < 10:
            features.append(0.0)

        return features[:10]  # Ensure exactly 10 features

    def act(self):
        """Execute an attack action"""
        # Get state features for strategy selection
        state_features = self.get_state_features()

        # Select strategy
        strategy = self.select_strategy(state_features)

        # Select target
        target_node = strategy.select_target(self.env, self.current_position)

        # Select attack type
        attack_type = strategy.select_attack_type(self.env, target_node)

        # Execute attack
        success, info = self.env.attack_node(target_node, attack_type, strategy.skill_level)

        # Update agent state
        if success:
            self.current_position = target_node
            self.compromised_nodes.add(target_node)

        # Record attack in history
        attack_record = {
            "strategy": strategy.name,
            "target": target_node,
            "attack_type": attack_type,
            "success": success,
            "info": info
        }
        self.attack_history.append(attack_record)

        # Update detection history for stealthy strategy
        if strategy.name == "Stealthy":
            detected = "attempt" in info
            strategy.update_detection_history(target_node, detected)

        # Store experience for learning
        reward = 1.0 if success else -0.1
        next_state_features = self.get_state_features()

        self.memory.append((state_features, strategy.name, reward, next_state_features))

        # Learn from experience
        if len(self.memory) > 32:
            self.learn(batch_size=32)

        return success, attack_record

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
        if self.attack_history:
            recent_history = self.attack_history[-50:]
            strategy_success = {}

            for strategy_name in self.strategies:
                strategy_attacks = [a for a in recent_history if a['strategy'] == strategy_name]
                if strategy_attacks:
                    success_rate = sum(1 for a in strategy_attacks if a['success']) / len(strategy_attacks)
                    strategy_success[strategy_name] = success_rate
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

    def reset(self):
        """Reset the agent state"""
        self.current_position = None
        self.compromised_nodes = set()
        # Keep attack history and learned parameters
