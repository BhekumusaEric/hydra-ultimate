#!/usr/bin/env python3
"""
HYDRA Elite Red Agent Simulation

This script runs an extended simulation using the Elite Red Agent with advanced
attack techniques to demonstrate sophisticated attack campaigns.
"""

import os
import time
import argparse
import json
import torch
import random
import numpy as np
from datetime import datetime
from tqdm import tqdm
from envs.enterprise_network import EnterpriseNetwork
from agents.enhanced_red_agent import EnhancedRedAgent
from agents.advanced_blue_agent import AdvancedBlueAgent

def setup_directories():
    """Create necessary directories for simulation results"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("network_snapshots", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("attack_chains", exist_ok=True)

def create_complex_network(config):
    """Create a more complex and realistic network environment"""
    print("Creating complex network environment...")
    
    # Create base environment
    env = EnterpriseNetwork(
        size=config['network_size'],
        complexity=config['network_complexity']
    )
    
    # Enhance network with additional node types
    node_types = ["workstation", "server", "database", "firewall", "router", 
                 "domain_controller", "file_server", "web_server", "email_server", 
                 "cloud_instance", "iot_device", "scada_controller"]
    
    # Add specialized nodes
    num_nodes = len(env.graph.nodes())
    for i in range(10):  # Add 10 specialized nodes
        node_id = num_nodes + i
        node_type = random.choice(node_types)
        
        # Add node to graph
        env.graph.add_node(
            node_id,
            type=node_type,
            security_controls=random.sample(["Firewall", "Antivirus", "EDR", "IDS", "DLP"], 
                                          k=random.randint(1, 3)),
            vulnerabilities=[
                {"type": random.choice(["sql_injection", "cross_site_scripting", "buffer_overflow", 
                                      "privilege_escalation", "unpatched_cve", "default_credentials", 
                                      "misconfiguration"]),
                 "severity": random.uniform(0.5, 0.9),
                 "exploitability": random.uniform(0.6, 0.9)}
                for _ in range(random.randint(1, 3))
            ]
        )
        
        # Connect to existing nodes
        for _ in range(random.randint(2, 5)):
            target_node = random.randint(0, num_nodes - 1)
            env.graph.add_edge(node_id, target_node)
            env.graph.add_edge(target_node, node_id)
    
    # Add high-value targets
    high_value_nodes = []
    for node in env.graph.nodes():
        if env.graph.nodes[node]['type'] in ["database", "domain_controller", "file_server"]:
            env.graph.nodes[node]['high_value'] = True
            env.graph.nodes[node]['data_sensitivity'] = random.uniform(0.7, 0.95)
            high_value_nodes.append(node)
    
    print(f"Complex network created with {len(env.graph.nodes())} nodes and {len(env.graph.edges())} connections")
    print(f"High-value targets: {len(high_value_nodes)} nodes")
    
    return env

def run_elite_simulation(config):
    """Run an extended simulation with the Elite Red Agent"""
    print(f"Starting HYDRA Elite Simulation with configuration: {config}")
    
    # Create output directories
    setup_directories()
    
    # Record start time
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create complex network environment
    env = create_complex_network(config)
    
    # Initialize agents
    red_agent = EnhancedRedAgent(
        env=env,
        skill_level=config['red_skill_level'],
        threat_intel_file=config['threat_intel_file']
    )
    
    # Load pre-trained elite model if specified
    if config.get('model_path') and os.path.exists(config['model_path']):
        try:
            red_agent.model.load_state_dict(torch.load(config['model_path']))
            print(f"Loaded elite model from {config['model_path']}")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    blue_agent = AdvancedBlueAgent(
        env=env
    )
    
    # Prepare results tracking
    results = {
        "config": config,
        "steps": [],
        "attack_chains": [],
        "summary": {
            "total_compromised": 0,
            "total_patched": 0,
            "red_success_rate": 0,
            "blue_success_rate": 0,
            "simulation_time": 0,
            "campaign_goal": red_agent.campaign_goal,
            "campaign_progress": 0,
            "high_value_compromised": 0
        }
    }
    
    # Save initial network state
    env.save_to_file(f"network_snapshots/network_initial_{timestamp}.json")
    
    # Track metrics
    red_attempts = 0
    red_successes = 0
    blue_actions = 0
    blue_successes = 0
    
    # Track attack chains
    current_attack_chain = []
    attack_chains = []
    
    # Run extended simulation
    print("\n=== Starting Elite Simulation ===\n")
    print(f"Red Agent Campaign Goal: {red_agent.campaign_goal}")
    
    for step in tqdm(range(1, config['num_steps'] + 1), desc="Simulation Progress"):
        # Generate network traffic
        env.simulate_traffic(num_events=random.randint(10, 30))
        
        # Red agent acts
        red_success, red_action = red_agent.act()
        red_attempts += 1
        if red_success:
            red_successes += 1
            # Add to attack chain
            current_attack_chain.append({
                "step": step,
                "action": red_action['attack_type'],
                "target": red_action['target'],
                "target_type": env.graph.nodes[red_action['target']]['type'] if red_action['target'] in env.graph.nodes() else "unknown"
            })
        
        # If attack chain is complete or failed, store it
        if not red_success and current_attack_chain:
            attack_chains.append(current_attack_chain)
            current_attack_chain = []
        
        # Blue agent acts
        blue_actions_results = blue_agent.act()
        blue_actions += len(blue_actions_results)
        blue_successes += sum(1 for r in blue_actions_results if r.get('success', False))
        
        # Log step results
        step_result = {
            "step": step,
            "red_action": red_action,
            "blue_actions": blue_actions_results,
            "compromised_nodes": list(red_agent.get_compromised_nodes()),
            "patched_nodes": list(blue_agent.get_patched_nodes()),
            "alerts": env.alerts[-5:] if hasattr(env, 'alerts') else [],
            "campaign_status": red_agent.get_campaign_status()
        }
        
        results["steps"].append(step_result)
        
        # Save network snapshot periodically
        if step % 50 == 0:
            env.save_to_file(f"network_snapshots/network_step_{step}_{timestamp}.json")
            
        # Print status periodically
        if step % 20 == 0:
            campaign_status = red_agent.get_campaign_status()
            print(f"\n--- Step {step}/{config['num_steps']} ---")
            print(f"Red Agent: {red_action['strategy']} attack on node {red_action['target']} - {'Success' if red_success else 'Failed'}")
            print(f"Campaign Progress: {campaign_status['progress']:.2f}")
            print(f"Compromised Nodes: {campaign_status['compromised_nodes']}")
            
            # Print recent logs
            print("\n[Recent Logs]")
            for log in env.logs[-3:]:
                print(f"  {log}")
    
    # Store final attack chain if not empty
    if current_attack_chain:
        attack_chains.append(current_attack_chain)
    
    results["attack_chains"] = attack_chains
    
    # Calculate final metrics
    end_time = time.time()
    simulation_time = end_time - start_time
    
    # Count high-value compromised nodes
    high_value_compromised = 0
    for node in red_agent.get_compromised_nodes():
        if node in env.graph.nodes() and env.graph.nodes[node].get('high_value', False):
            high_value_compromised += 1
    
    campaign_status = red_agent.get_campaign_status()
    results["summary"]["total_compromised"] = len(red_agent.get_compromised_nodes())
    results["summary"]["total_patched"] = len(blue_agent.get_patched_nodes())
    results["summary"]["red_success_rate"] = red_successes / max(1, red_attempts)
    results["summary"]["blue_success_rate"] = blue_successes / max(1, blue_actions)
    results["summary"]["simulation_time"] = simulation_time
    results["summary"]["campaign_goal"] = campaign_status["goal"]
    results["summary"]["campaign_progress"] = campaign_status["progress"]
    results["summary"]["data_collected"] = campaign_status["data_collected"]
    results["summary"]["lateral_movements"] = campaign_status["lateral_movements"]
    results["summary"]["high_value_compromised"] = high_value_compromised
    
    # Save final network state
    env.save_to_file(f"network_snapshots/network_final_{timestamp}.json")
    
    # Save results
    results_path = f"results/elite_simulation_results_{timestamp}.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # Save attack chains separately
    attack_chains_path = f"attack_chains/attack_chains_{timestamp}.json"
    with open(attack_chains_path, "w") as f:
        json.dump(attack_chains, f, indent=2)
    
    # Generate comprehensive report
    generate_elite_report(results, timestamp)
    
    # Print summary
    print("\n=== Elite Simulation Complete ===")
    print(f"Total steps: {config['num_steps']}")
    print(f"Simulation time: {simulation_time:.2f} seconds")
    print(f"Compromised nodes: {len(red_agent.get_compromised_nodes())}")
    print(f"High-value nodes compromised: {high_value_compromised}")
    print(f"Patched nodes: {len(blue_agent.get_patched_nodes())}")
    print(f"Red agent success rate: {red_successes / max(1, red_attempts):.2f}")
    print(f"Blue agent success rate: {blue_successes / max(1, blue_actions):.2f}")
    print(f"Campaign goal: {campaign_status['goal']}")
    print(f"Campaign progress: {campaign_status['progress']:.2f}")
    print(f"Data collected: {campaign_status['data_collected']}")
    print(f"Lateral movements: {campaign_status['lateral_movements']}")
    print(f"Attack chains: {len(attack_chains)}")
    print(f"Results saved to: {results_path}")
    print(f"Attack chains saved to: {attack_chains_path}")
    
    return results

def generate_elite_report(results, timestamp):
    """Generate a comprehensive HTML report of elite simulation results"""
    report_path = f"reports/elite_simulation_report_{timestamp}.html"
    
    # Create HTML report content
    report_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HYDRA Elite Simulation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
            .metrics {{ display: flex; flex-wrap: wrap; }}
            .metric-card {{ background-color: #ffffff; border: 1px solid #e0e0e0; 
                          border-radius: 5px; padding: 15px; margin: 10px; width: 200px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
            .attack {{ background-color: #fff8f8; border-left: 4px solid #e74c3c; 
                     padding: 10px; margin: 10px 0; }}
            .defense {{ background-color: #f8fff8; border-left: 4px solid #2ecc71; 
                      padding: 10px; margin: 10px 0; }}
            .success {{ color: #2ecc71; }}
            .failure {{ color: #e74c3c; }}
            .attack-chain {{ background-color: #f0f8ff; border: 1px solid #b0c4de;
                           padding: 15px; margin: 15px 0; border-radius: 5px; }}
            .high-value {{ background-color: #fff0f0; }}
        </style>
    </head>
    <body>
        <h1>HYDRA Elite Simulation Report</h1>
        <p>Advanced simulation conducted on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        
        <div class="summary">
            <h2>Executive Summary</h2>
            <p>This report presents the findings from an elite simulation conducted using HYDRA with advanced attack techniques.</p>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Simulation Time</h3>
                    <div class="metric-value">{results["summary"]["simulation_time"]:.2f}s</div>
                </div>
                <div class="metric-card">
                    <h3>Compromised Nodes</h3>
                    <div class="metric-value">{results["summary"]["total_compromised"]}</div>
                </div>
                <div class="metric-card">
                    <h3>High-Value Compromised</h3>
                    <div class="metric-value">{results["summary"]["high_value_compromised"]}</div>
                </div>
                <div class="metric-card">
                    <h3>Patched Nodes</h3>
                    <div class="metric-value">{results["summary"]["total_patched"]}</div>
                </div>
                <div class="metric-card">
                    <h3>Red Success Rate</h3>
                    <div class="metric-value">{results["summary"]["red_success_rate"]*100:.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Blue Success Rate</h3>
                    <div class="metric-value">{results["summary"]["blue_success_rate"]*100:.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Campaign Goal</h3>
                    <div class="metric-value">{results["summary"]["campaign_goal"]}</div>
                </div>
                <div class="metric-card">
                    <h3>Campaign Progress</h3>
                    <div class="metric-value">{results["summary"]["campaign_progress"]*100:.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Data Collected</h3>
                    <div class="metric-value">{results["summary"]["data_collected"]}</div>
                </div>
                <div class="metric-card">
                    <h3>Lateral Movements</h3>
                    <div class="metric-value">{results["summary"]["lateral_movements"]}</div>
                </div>
                <div class="metric-card">
                    <h3>Attack Chains</h3>
                    <div class="metric-value">{len(results["attack_chains"])}</div>
                </div>
            </div>
        </div>
        
        <h2>Simulation Configuration</h2>
        <pre>{json.dumps(results["config"], indent=2)}</pre>
        
        <h2>Key Findings</h2>
        <p>The elite simulation revealed several important insights about your network's security posture:</p>
        <ul>
            <li>The Red Agent was able to compromise {results["summary"]["total_compromised"]} nodes, including {results["summary"]["high_value_compromised"]} high-value targets.</li>
            <li>The Blue Agent successfully patched {results["summary"]["total_patched"]} nodes.</li>
            <li>The Red Agent's campaign goal was <strong>{results["summary"]["campaign_goal"]}</strong> and achieved {results["summary"]["campaign_progress"]*100:.1f}% progress.</li>
            <li>The Red Agent collected data from {results["summary"].get("data_collected", 0)} sources.</li>
            <li>The Red Agent performed {results["summary"].get("lateral_movements", 0)} lateral movements.</li>
            <li>The simulation identified {len(results["attack_chains"])} distinct attack chains.</li>
        </ul>
        
        <h2>Notable Attack Chains</h2>
    """
    
    # Add attack chains to report
    for i, chain in enumerate(results["attack_chains"][:5]):  # Show top 5 chains
        report_content += f"""
        <div class="attack-chain">
            <h3>Attack Chain #{i+1} ({len(chain)} steps)</h3>
            <ol>
        """
        
        for step in chain:
            high_value_class = " high-value" if step.get("target_type") in ["database", "domain_controller", "file_server"] else ""
            report_content += f"""
                <li class="{high_value_class}">
                    Step {step["step"]}: {step["action"]} attack on {step["target_type"]} (Node {step["target"]})
                </li>
            """
        
        report_content += """
            </ol>
        </div>
        """
    
    # Add recommendations
    report_content += """
        <h2>Recommendations</h2>
        <p>Based on the elite simulation results, consider the following recommendations:</p>
        <ol>
            <li>Implement advanced threat detection capabilities to identify sophisticated attack patterns.</li>
            <li>Enhance network segmentation to limit lateral movement opportunities.</li>
            <li>Deploy additional security controls for high-value assets.</li>
            <li>Implement a comprehensive vulnerability management program.</li>
            <li>Develop incident response playbooks for advanced persistent threats.</li>
            <li>Conduct regular red team exercises to test defenses against sophisticated attacks.</li>
            <li>Implement a zero-trust architecture for critical systems.</li>
            <li>Deploy deception technology to detect and divert attackers.</li>
        </ol>
    </body>
    </html>
    """
    
    # Save HTML report
    with open(report_path, "w") as f:
        f.write(report_content)
    
    print(f"Elite report generated: {report_path}")

def main():
    """Main function to run the elite simulation"""
    print("=" * 80)
    print("HYDRA ELITE SIMULATION")
    print("Advanced Red-Blue Simulation with Elite Hacking Capabilities")
    print("=" * 80)
    
    parser = argparse.ArgumentParser(description="HYDRA Elite Simulation")
    parser.add_argument("--network-size", choices=["small", "medium", "large"], 
                        default="large", help="Base size of the network")
    parser.add_argument("--network-complexity", choices=["low", "medium", "high"], 
                        default="high", help="Complexity of the network")
    parser.add_argument("--num-steps", type=int, default=200, 
                        help="Number of simulation steps")
    parser.add_argument("--red-skill", type=float, default=0.95, 
                        help="Red agent skill level (0.0-1.0)")
    parser.add_argument("--threat-intel", type=str, default="data/advanced_threat_intelligence.json",
                        help="Path to advanced threat intelligence data file")
    parser.add_argument("--model", type=str, default=None,
                        help="Path to elite model file")
    
    args = parser.parse_args()
    
    config = {
        "network_size": args.network_size,
        "network_complexity": args.network_complexity,
        "num_steps": args.num_steps,
        "red_skill_level": args.red_skill,
        "threat_intel_file": args.threat_intel,
        "model_path": args.model
    }
    
    run_elite_simulation(config)
    
    print("\nElite simulation results are available in the 'results' directory.")
    print("Launch the dashboard with: streamlit run dashboard/advanced_dashboard.py")

if __name__ == "__main__":
    main()
