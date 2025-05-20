#!/usr/bin/env python3
"""
HYDRA Enhanced Red Agent Training

This script trains the Enhanced Red Agent with real-world threat intelligence data
to improve its attack capabilities and make it more realistic.
"""

import os
import time
import argparse
import json
import torch
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from envs.enterprise_network import EnterpriseNetwork
from agents.enhanced_red_agent import EnhancedRedAgent

def setup_directories():
    """Create necessary directories for training results"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("training_plots", exist_ok=True)

def train_agent(config):
    """Train the Enhanced Red Agent with real-world data"""
    print(f"Starting Enhanced Red Agent Training with configuration: {config}")
    
    # Record start time
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize environment
    env = EnterpriseNetwork(
        size=config['network_size'],
        complexity=config['network_complexity']
    )
    
    # Initialize enhanced red agent
    red_agent = EnhancedRedAgent(
        env=env,
        skill_level=config['red_skill_level'],
        learning_rate=config['learning_rate'],
        threat_intel_file=config['threat_intel_file']
    )
    
    # Training metrics
    training_metrics = {
        "episodes": [],
        "success_rates": [],
        "detection_rates": [],
        "campaign_progress": [],
        "rewards": []
    }
    
    # Train for specified number of episodes
    for episode in range(1, config['num_episodes'] + 1):
        print(f"\n--- Episode {episode}/{config['num_episodes']} ---")
        
        # Reset environment and agent for new episode
        env = EnterpriseNetwork(
            size=config['network_size'],
            complexity=config['network_complexity']
        )
        red_agent.env = env
        red_agent.reset()
        
        # Track episode metrics
        episode_rewards = []
        episode_successes = 0
        episode_attempts = 0
        episode_detections = 0
        
        # Run episode for specified number of steps
        for step in range(1, config['steps_per_episode'] + 1):
            # Execute attack action
            success, attack_record = red_agent.act()
            
            # Update metrics
            episode_attempts += 1
            if success:
                episode_successes += 1
            if attack_record.get('detected', False):
                episode_detections += 1
                
            # Calculate reward
            reward = 1.0 if success else -0.1
            if attack_record.get('detected', False):
                reward -= 0.5
            episode_rewards.append(reward)
            
            # Print progress every 10 steps
            if step % 10 == 0:
                success_rate = episode_successes / max(1, episode_attempts)
                detection_rate = episode_detections / max(1, episode_attempts)
                campaign_status = red_agent.get_campaign_status()
                
                print(f"  Step {step}: Success Rate: {success_rate:.2f}, Detection Rate: {detection_rate:.2f}")
                print(f"  Campaign Goal: {campaign_status['goal']}, Progress: {campaign_status['progress']:.2f}")
                print(f"  Compromised Nodes: {campaign_status['compromised_nodes']}")
        
        # Calculate episode metrics
        success_rate = episode_successes / max(1, episode_attempts)
        detection_rate = episode_detections / max(1, episode_attempts)
        avg_reward = sum(episode_rewards) / max(1, len(episode_rewards))
        campaign_status = red_agent.get_campaign_status()
        
        # Update training metrics
        training_metrics["episodes"].append(episode)
        training_metrics["success_rates"].append(success_rate)
        training_metrics["detection_rates"].append(detection_rate)
        training_metrics["campaign_progress"].append(campaign_status["progress"])
        training_metrics["rewards"].append(avg_reward)
        
        print(f"\nEpisode {episode} Summary:")
        print(f"  Success Rate: {success_rate:.2f}")
        print(f"  Detection Rate: {detection_rate:.2f}")
        print(f"  Average Reward: {avg_reward:.2f}")
        print(f"  Campaign Progress: {campaign_status['progress']:.2f}")
        print(f"  Compromised Nodes: {campaign_status['compromised_nodes']}")
        print(f"  Data Collected: {campaign_status['data_collected']}")
        print(f"  Lateral Movements: {campaign_status['lateral_movements']}")
        
        # Save model checkpoint every 10 episodes
        if episode % 10 == 0:
            model_path = f"models/enhanced_red_agent_{timestamp}_ep{episode}.pt"
            torch.save(red_agent.model.state_dict(), model_path)
            print(f"  Model checkpoint saved to {model_path}")
    
    # Calculate training duration
    end_time = time.time()
    training_duration = end_time - start_time
    
    # Save final model
    final_model_path = f"models/enhanced_red_agent_{timestamp}_final.pt"
    torch.save(red_agent.model.state_dict(), final_model_path)
    
    # Save training metrics
    metrics_path = f"results/training_metrics_{timestamp}.json"
    with open(metrics_path, "w") as f:
        json.dump(training_metrics, f, indent=2)
    
    # Generate training plots
    generate_training_plots(training_metrics, timestamp)
    
    print(f"\nTraining completed in {training_duration:.2f} seconds")
    print(f"Final model saved to {final_model_path}")
    print(f"Training metrics saved to {metrics_path}")
    
    return red_agent, training_metrics

def generate_training_plots(metrics, timestamp):
    """Generate plots visualizing the training progress"""
    # Create figure with multiple subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    
    # Plot success rate
    axs[0, 0].plot(metrics["episodes"], metrics["success_rates"], 'b-')
    axs[0, 0].set_title('Attack Success Rate')
    axs[0, 0].set_xlabel('Episode')
    axs[0, 0].set_ylabel('Success Rate')
    axs[0, 0].grid(True)
    
    # Plot detection rate
    axs[0, 1].plot(metrics["episodes"], metrics["detection_rates"], 'r-')
    axs[0, 1].set_title('Attack Detection Rate')
    axs[0, 1].set_xlabel('Episode')
    axs[0, 1].set_ylabel('Detection Rate')
    axs[0, 1].grid(True)
    
    # Plot campaign progress
    axs[1, 0].plot(metrics["episodes"], metrics["campaign_progress"], 'g-')
    axs[1, 0].set_title('Campaign Progress')
    axs[1, 0].set_xlabel('Episode')
    axs[1, 0].set_ylabel('Progress')
    axs[1, 0].grid(True)
    
    # Plot average reward
    axs[1, 1].plot(metrics["episodes"], metrics["rewards"], 'y-')
    axs[1, 1].set_title('Average Reward')
    axs[1, 1].set_xlabel('Episode')
    axs[1, 1].set_ylabel('Reward')
    axs[1, 1].grid(True)
    
    # Adjust layout and save
    plt.tight_layout()
    plot_path = f"training_plots/training_progress_{timestamp}.png"
    plt.savefig(plot_path)
    print(f"Training plots saved to {plot_path}")

def main():
    """Main function to run the training"""
    print("=" * 80)
    print("HYDRA ENHANCED RED AGENT TRAINING")
    print("Training with real-world threat intelligence data")
    print("=" * 80)
    
    # Create directories
    setup_directories()
    
    parser = argparse.ArgumentParser(description="HYDRA Enhanced Red Agent Training")
    parser.add_argument("--network-size", choices=["small", "medium", "large"], 
                        default="small", help="Size of the network for training")
    parser.add_argument("--network-complexity", choices=["low", "medium", "high"], 
                        default="medium", help="Complexity of the network")
    parser.add_argument("--num-episodes", type=int, default=50, 
                        help="Number of training episodes")
    parser.add_argument("--steps-per-episode", type=int, default=100, 
                        help="Number of steps per episode")
    parser.add_argument("--red-skill", type=float, default=0.7, 
                        help="Initial red agent skill level (0.0-1.0)")
    parser.add_argument("--learning-rate", type=float, default=0.001, 
                        help="Learning rate for neural network")
    parser.add_argument("--threat-intel", type=str, default="data/threat_intelligence.json",
                        help="Path to threat intelligence data file")
    
    args = parser.parse_args()
    
    config = {
        "network_size": args.network_size,
        "network_complexity": args.network_complexity,
        "num_episodes": args.num_episodes,
        "steps_per_episode": args.steps_per_episode,
        "red_skill_level": args.red_skill,
        "learning_rate": args.learning_rate,
        "threat_intel_file": args.threat_intel
    }
    
    # Train the agent
    agent, metrics = train_agent(config)
    
    print("\nTraining complete!")
    print("The Enhanced Red Agent has been trained with real-world threat intelligence.")
    print("You can now use this agent in your simulations for more realistic attacks.")

if __name__ == "__main__":
    main()
