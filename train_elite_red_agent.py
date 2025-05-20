#!/usr/bin/env python3
"""
HYDRA Elite Red Agent Training

This script implements an advanced training regimen for the Red Agent,
using sophisticated techniques to create an elite hacker-level agent.
"""

import os
import time
import argparse
import json
import torch
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import random
from tqdm import tqdm
from envs.enterprise_network import EnterpriseNetwork
from agents.enhanced_red_agent import EnhancedRedAgent

def setup_directories():
    """Create necessary directories for training results"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("training_plots", exist_ok=True)

def create_diverse_environments(config, num_environments=5):
    """Create a diverse set of training environments"""
    environments = []
    
    # Create environments with different sizes and complexities
    sizes = ["small", "medium", "large"]
    complexities = ["low", "medium", "high"]
    
    for _ in range(num_environments):
        size = random.choice(sizes)
        complexity = random.choice(complexities)
        
        env = EnterpriseNetwork(
            size=size,
            complexity=complexity
        )
        environments.append(env)
    
    return environments

def progressive_difficulty_training(agent, environments, config):
    """Implement progressive difficulty training"""
    print("Starting progressive difficulty training...")
    
    # Start with easier environments and gradually increase difficulty
    for difficulty_level in range(1, 6):
        print(f"\n=== Difficulty Level {difficulty_level}/5 ===")
        
        # Adjust parameters based on difficulty
        steps_per_episode = config['steps_per_episode'] * difficulty_level
        detection_penalty = 0.1 * difficulty_level
        
        # Train for specified number of episodes at this difficulty
        episodes_at_level = max(5, config['num_episodes'] // 5)
        
        for episode in range(1, episodes_at_level + 1):
            print(f"\n--- Episode {episode}/{episodes_at_level} (Difficulty {difficulty_level}) ---")
            
            # Select environment based on difficulty
            env_index = min(difficulty_level - 1, len(environments) - 1)
            env = environments[env_index]
            
            # Reset agent for new episode
            agent.env = env
            agent.reset()
            
            # Track episode metrics
            episode_rewards = []
            episode_successes = 0
            episode_attempts = 0
            episode_detections = 0
            
            # Run episode
            for step in tqdm(range(1, steps_per_episode + 1), desc="Training"):
                # Execute attack action
                success, attack_record = agent.act()
                
                # Update metrics
                episode_attempts += 1
                if success:
                    episode_successes += 1
                if attack_record.get('detected', False):
                    episode_detections += 1
                    
                # Calculate reward with increasing penalty for detection
                reward = 1.0 if success else -0.1
                if attack_record.get('detected', False):
                    reward -= detection_penalty
                episode_rewards.append(reward)
                
                # Print progress every 20 steps
                if step % 20 == 0:
                    success_rate = episode_successes / max(1, episode_attempts)
                    detection_rate = episode_detections / max(1, episode_attempts)
                    campaign_status = agent.get_campaign_status()
                    
                    print(f"  Step {step}: Success Rate: {success_rate:.2f}, Detection Rate: {detection_rate:.2f}")
                    print(f"  Campaign Goal: {campaign_status['goal']}, Progress: {campaign_status['progress']:.2f}")
                    print(f"  Compromised Nodes: {campaign_status['compromised_nodes']}")
            
            # Calculate episode metrics
            success_rate = episode_successes / max(1, episode_attempts)
            detection_rate = episode_detections / max(1, episode_attempts)
            avg_reward = sum(episode_rewards) / max(1, len(episode_rewards))
            campaign_status = agent.get_campaign_status()
            
            print(f"\nEpisode {episode} Summary (Difficulty {difficulty_level}):")
            print(f"  Success Rate: {success_rate:.2f}")
            print(f"  Detection Rate: {detection_rate:.2f}")
            print(f"  Average Reward: {avg_reward:.2f}")
            print(f"  Campaign Progress: {campaign_status['progress']:.2f}")
            print(f"  Compromised Nodes: {campaign_status['compromised_nodes']}")
            
            # Save model checkpoint
            if episode % 5 == 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                model_path = f"models/elite_red_agent_d{difficulty_level}_ep{episode}_{timestamp}.pt"
                torch.save(agent.model.state_dict(), model_path)
                print(f"  Model checkpoint saved to {model_path}")
    
    return agent

def adversarial_training(agent, config):
    """Implement adversarial training to improve agent capabilities"""
    print("\nStarting adversarial training...")
    
    # Create a challenging environment
    env = EnterpriseNetwork(
        size="large",
        complexity="high"
    )
    
    # Reset agent for new training phase
    agent.env = env
    agent.reset()
    
    # Track metrics
    adversarial_rewards = []
    
    # Run adversarial training episodes
    for episode in range(1, config['adversarial_episodes'] + 1):
        print(f"\n--- Adversarial Episode {episode}/{config['adversarial_episodes']} ---")
        
        # Reset environment but keep agent learning
        env = EnterpriseNetwork(
            size="large",
            complexity="high"
        )
        agent.env = env
        agent.reset()
        
        # Increase defense capabilities
        for node in env.graph.nodes():
            # Add more security controls
            current_controls = env.graph.nodes[node]['security_controls']
            additional_controls = ["Advanced EDR", "Next-Gen Firewall", "Behavioral Analysis"]
            env.graph.nodes[node]['security_controls'] = list(set(current_controls + additional_controls))
            
            # Patch some vulnerabilities
            if random.random() < 0.5:  # 50% chance to patch vulnerabilities
                env.graph.nodes[node]['vulnerabilities'] = []
        
        # Track episode metrics
        episode_rewards = []
        episode_successes = 0
        episode_attempts = 0
        
        # Run episode with more steps
        steps = config['steps_per_episode'] * 2
        for step in tqdm(range(1, steps + 1), desc="Adversarial Training"):
            # Execute attack action
            success, attack_record = agent.act()
            
            # Update metrics
            episode_attempts += 1
            if success:
                episode_successes += 1
                
            # Calculate reward with higher rewards for success against tough defenses
            reward = 2.0 if success else -0.2
            if attack_record.get('detected', False):
                reward -= 0.3
            episode_rewards.append(reward)
            
            # Print progress every 20 steps
            if step % 20 == 0:
                success_rate = episode_successes / max(1, episode_attempts)
                campaign_status = agent.get_campaign_status()
                
                print(f"  Step {step}: Success Rate: {success_rate:.2f}")
                print(f"  Campaign Progress: {campaign_status['progress']:.2f}")
                print(f"  Compromised Nodes: {campaign_status['compromised_nodes']}")
        
        # Calculate episode metrics
        success_rate = episode_successes / max(1, episode_attempts)
        avg_reward = sum(episode_rewards) / max(1, len(episode_rewards))
        campaign_status = agent.get_campaign_status()
        
        print(f"\nAdversarial Episode {episode} Summary:")
        print(f"  Success Rate: {success_rate:.2f}")
        print(f"  Average Reward: {avg_reward:.2f}")
        print(f"  Campaign Progress: {campaign_status['progress']:.2f}")
        print(f"  Compromised Nodes: {campaign_status['compromised_nodes']}")
        
        adversarial_rewards.append(avg_reward)
        
        # Save model checkpoint
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"models/elite_red_agent_adversarial_ep{episode}_{timestamp}.pt"
        torch.save(agent.model.state_dict(), model_path)
        print(f"  Model checkpoint saved to {model_path}")
    
    return agent, adversarial_rewards

def specialized_training(agent, config):
    """Train the agent on specialized attack techniques"""
    print("\nStarting specialized technique training...")
    
    # Define specialized techniques to train
    techniques = [
        "zero_day_exploitation",
        "supply_chain_compromise",
        "firmware_implants",
        "living_off_the_land",
        "credential_theft"
    ]
    
    # Create a standard environment
    env = EnterpriseNetwork(
        size="medium",
        complexity="medium"
    )
    
    # Train each technique
    for technique in techniques:
        print(f"\n--- Training Technique: {technique} ---")
        
        # Reset agent but keep learning
        agent.env = env
        agent.reset()
        
        # Modify agent to focus on this technique
        if hasattr(agent, 'campaign_goal'):
            if technique == "zero_day_exploitation":
                agent.campaign_goal = "persistence"
            elif technique == "supply_chain_compromise":
                agent.campaign_goal = "data_theft"
            elif technique == "firmware_implants":
                agent.campaign_goal = "persistence"
            elif technique == "living_off_the_land":
                agent.campaign_goal = "disruption"
            elif technique == "credential_theft":
                agent.campaign_goal = "data_theft"
        
        # Run focused training episodes
        for episode in range(1, config['specialized_episodes'] + 1):
            print(f"  Episode {episode}/{config['specialized_episodes']} for {technique}")
            
            # Reset environment but keep agent learning
            env = EnterpriseNetwork(
                size="medium",
                complexity="medium"
            )
            agent.env = env
            agent.reset()
            
            # Track metrics
            episode_successes = 0
            episode_attempts = 0
            
            # Run episode
            for step in range(1, config['steps_per_episode'] + 1):
                # Execute attack action
                success, _ = agent.act()
                
                # Update metrics
                episode_attempts += 1
                if success:
                    episode_successes += 1
            
            # Calculate success rate
            success_rate = episode_successes / max(1, episode_attempts)
            print(f"    Success Rate: {success_rate:.2f}")
        
        # Save specialized model
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"models/elite_red_agent_{technique}_{timestamp}.pt"
        torch.save(agent.model.state_dict(), model_path)
        print(f"  Specialized model for {technique} saved to {model_path}")
    
    return agent

def train_elite_agent(config):
    """Train an elite Red Agent using advanced training techniques"""
    print(f"Starting Elite Red Agent Training with configuration: {config}")
    
    # Record start time
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create diverse training environments
    environments = create_diverse_environments(config)
    
    # Initialize enhanced red agent with advanced threat intelligence
    env = environments[0]  # Start with first environment
    red_agent = EnhancedRedAgent(
        env=env,
        skill_level=config['red_skill_level'],
        learning_rate=config['learning_rate'],
        threat_intel_file=config['threat_intel_file']
    )
    
    # Phase 1: Progressive Difficulty Training
    red_agent = progressive_difficulty_training(red_agent, environments, config)
    
    # Phase 2: Adversarial Training
    red_agent, adversarial_rewards = adversarial_training(red_agent, config)
    
    # Phase 3: Specialized Technique Training
    red_agent = specialized_training(red_agent, config)
    
    # Calculate training duration
    end_time = time.time()
    training_duration = end_time - start_time
    
    # Save final elite model
    final_model_path = f"models/elite_red_agent_final_{timestamp}.pt"
    torch.save(red_agent.model.state_dict(), final_model_path)
    
    print(f"\nElite training completed in {training_duration:.2f} seconds")
    print(f"Final elite model saved to {final_model_path}")
    
    return red_agent, final_model_path

def main():
    """Main function to run the elite training"""
    print("=" * 80)
    print("HYDRA ELITE RED AGENT TRAINING")
    print("Advanced training regimen to create a top-tier hacking agent")
    print("=" * 80)
    
    # Create directories
    setup_directories()
    
    parser = argparse.ArgumentParser(description="HYDRA Elite Red Agent Training")
    parser.add_argument("--num-episodes", type=int, default=100, 
                        help="Number of training episodes per difficulty level")
    parser.add_argument("--steps-per-episode", type=int, default=100, 
                        help="Base number of steps per episode")
    parser.add_argument("--red-skill", type=float, default=0.9, 
                        help="Initial red agent skill level (0.0-1.0)")
    parser.add_argument("--learning-rate", type=float, default=0.0005, 
                        help="Learning rate for neural network")
    parser.add_argument("--threat-intel", type=str, default="data/advanced_threat_intelligence.json",
                        help="Path to advanced threat intelligence data file")
    parser.add_argument("--adversarial-episodes", type=int, default=20,
                        help="Number of adversarial training episodes")
    parser.add_argument("--specialized-episodes", type=int, default=10,
                        help="Number of specialized technique training episodes")
    
    args = parser.parse_args()
    
    config = {
        "num_episodes": args.num_episodes,
        "steps_per_episode": args.steps_per_episode,
        "red_skill_level": args.red_skill,
        "learning_rate": args.learning_rate,
        "threat_intel_file": args.threat_intel,
        "adversarial_episodes": args.adversarial_episodes,
        "specialized_episodes": args.specialized_episodes
    }
    
    # Train the elite agent
    agent, model_path = train_elite_agent(config)
    
    print("\nElite Training complete!")
    print("The Red Agent has been trained to perform like a top-notch hacker.")
    print(f"Elite model saved to: {model_path}")
    print("\nTo use this elite agent in simulations, run:")
    print(f"python3 run_enhanced_simulation.py --model {model_path} --threat-intel {args.threat_intel}")

if __name__ == "__main__":
    main()
