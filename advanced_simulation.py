import os
import json
import time
import random
import argparse
from datetime import datetime

from envs.enterprise_network import EnterpriseNetwork
from agents.advanced_red_agent import AdvancedRedAgent
from agents.advanced_blue_agent import AdvancedBlueAgent
from utils.logger import log_event

def run_simulation(config):
    """Run the advanced HYDRA simulation"""
    print(f"Starting HYDRA Advanced Simulation with configuration: {config}")
    
    # Create output directories if they don't exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("network_snapshots", exist_ok=True)
    
    # Initialize environment
    env = EnterpriseNetwork(
        size=config['network_size'],
        complexity=config['network_complexity']
    )
    
    # Initialize agents
    red_agent = AdvancedRedAgent(
        env=env,
        skill_level=config['red_skill_level']
    )
    
    blue_agent = AdvancedBlueAgent(
        env=env
    )
    
    # Prepare results tracking
    results = {
        "config": config,
        "steps": [],
        "summary": {
            "total_compromised": 0,
            "total_patched": 0,
            "red_success_rate": 0,
            "blue_success_rate": 0,
            "simulation_time": 0
        }
    }
    
    # Save initial network state
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    env.save_to_file(f"network_snapshots/network_initial_{timestamp}.json")
    
    # Track metrics
    red_attempts = 0
    red_successes = 0
    blue_actions = 0
    blue_successes = 0
    
    # Run simulation steps
    start_time = time.time()
    
    print("\n=== Starting Simulation ===\n")
    
    for step in range(1, config['num_steps'] + 1):
        print(f"\n--- Step {step}/{config['num_steps']} ---")
        
        # Generate some network traffic
        env.simulate_traffic(num_events=random.randint(5, 15))
        
        # Red agent acts
        red_success, red_action = red_agent.act()
        red_attempts += 1
        if red_success:
            red_successes += 1
        
        print(f"Red Agent: {red_action['strategy']} attack on node {red_action['target']} - {'Success' if red_success else 'Failed'}")
        
        # Blue agent acts
        blue_actions_results = blue_agent.act()
        blue_actions += len(blue_actions_results)
        blue_successes += sum(1 for r in blue_actions_results if r.get('success', False))
        
        for action in blue_actions_results:
            action_type = action.get('action')
            node_id = action.get('node_id')
            success = action.get('success', False)
            
            if action_type == 'patch':
                vuln_type = action.get('vulnerability_type')
                print(f"Blue Agent: Patched {vuln_type} on node {node_id} - {'Success' if success else 'Failed'}")
            elif action_type == 'investigate':
                found = action.get('found_compromise', False)
                print(f"Blue Agent: Investigated node {node_id} - {'Found compromise' if found else 'No compromise found'}")
        
        # Log step results
        step_result = {
            "step": step,
            "red_action": red_action,
            "blue_actions": blue_actions_results,
            "compromised_nodes": list(red_agent.get_compromised_nodes()),
            "patched_nodes": list(blue_agent.get_patched_nodes()),
            "alerts": env.alerts[-5:] if hasattr(env, 'alerts') else []
        }
        
        results["steps"].append(step_result)
        
        # Log to file
        log_event(f"Step {step}: Red {red_action['strategy']} attack on node {red_action['target']} - {'Success' if red_success else 'Failed'}")
        for action in blue_actions_results:
            log_event(f"Step {step}: Blue {action.get('action')} on node {action.get('node_id')} - {'Success' if action.get('success', False) else 'Failed'}")
        
        # Save network snapshot every 10 steps
        if step % 10 == 0:
            env.save_to_file(f"network_snapshots/network_step_{step}_{timestamp}.json")
        
        # Print current logs
        print("\n[Recent Logs]")
        for log in env.logs[-5:]:
            print(f"  {log}")
        
        # Print current alerts
        if hasattr(env, 'alerts') and env.alerts:
            print("\n[Recent Alerts]")
            for alert in env.alerts[-3:]:
                print(f"  {alert}")
    
    # Calculate final metrics
    end_time = time.time()
    simulation_time = end_time - start_time
    
    results["summary"]["total_compromised"] = len(red_agent.get_compromised_nodes())
    results["summary"]["total_patched"] = len(blue_agent.get_patched_nodes())
    results["summary"]["red_success_rate"] = red_successes / max(1, red_attempts)
    results["summary"]["blue_success_rate"] = blue_successes / max(1, blue_actions)
    results["summary"]["simulation_time"] = simulation_time
    
    # Save final network state
    env.save_to_file(f"network_snapshots/network_final_{timestamp}.json")
    
    # Save results
    with open(f"results/simulation_results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n=== Simulation Complete ===")
    print(f"Total steps: {config['num_steps']}")
    print(f"Simulation time: {simulation_time:.2f} seconds")
    print(f"Compromised nodes: {len(red_agent.get_compromised_nodes())}")
    print(f"Patched nodes: {len(blue_agent.get_patched_nodes())}")
    print(f"Red agent success rate: {red_successes / max(1, red_attempts):.2f}")
    print(f"Blue agent success rate: {blue_successes / max(1, blue_actions):.2f}")
    print(f"Results saved to: results/simulation_results_{timestamp}.json")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HYDRA Advanced Simulation")
    parser.add_argument("--network-size", choices=["small", "medium", "large"], default="medium", help="Size of the network")
    parser.add_argument("--network-complexity", choices=["low", "medium", "high"], default="medium", help="Complexity of the network")
    parser.add_argument("--num-steps", type=int, default=50, help="Number of simulation steps")
    parser.add_argument("--red-skill", type=float, default=0.7, help="Red agent skill level (0.0-1.0)")
    
    args = parser.parse_args()
    
    config = {
        "network_size": args.network_size,
        "network_complexity": args.network_complexity,
        "num_steps": args.num_steps,
        "red_skill_level": args.red_skill
    }
    
    run_simulation(config)
