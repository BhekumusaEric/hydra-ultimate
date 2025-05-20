#!/usr/bin/env python3
"""
HYDRA Super Red Agent Simulation

This script runs a simulation using the Super Red Agent with guaranteed success rates
to demonstrate advanced attack capabilities and provide a challenging test for blue teams.
"""

import os
import time
import argparse
import json
import torch
import random
from datetime import datetime
from envs.vulnerable_network import VulnerableNetwork
from agents.super_red_agent import SuperRedAgent
from agents.advanced_blue_agent import AdvancedBlueAgent

def setup_directories():
    """Create necessary directories for simulation results"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("network_snapshots", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

def run_super_simulation(config):
    """Run a simulation with the Super Red Agent"""
    print(f"Starting HYDRA Super Red Agent Simulation with configuration: {config}")

    # Create output directories if they don't exist
    setup_directories()

    # Record start time
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize environment with vulnerable network
    env = VulnerableNetwork(
        size=config['network_size'],
        complexity=config['network_complexity']
    )

    # Initialize agents
    red_agent = SuperRedAgent(
        env=env,
        skill_level=config['red_skill_level'],
        threat_intel_file=config['threat_intel_file']
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
            "simulation_time": 0,
            "campaign_goal": red_agent.campaign_goal,
            "campaign_progress": 0,
            "data_exfiltrated": 0,
            "data_exfiltration_percentage": 0
        }
    }

    # Save initial network state
    env.save_to_file(f"network_snapshots/network_initial_{timestamp}.json")

    # Track metrics
    red_attempts = 0
    red_successes = 0
    blue_actions = 0
    blue_successes = 0

    # Run simulation steps
    print("\n=== Starting Super Red Agent Simulation ===\n")
    print(f"Red Agent Campaign Goal: {red_agent.campaign_goal}")
    print(f"Network Size: {len(list(env.graph.nodes()))} nodes")

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
            print(f"Blue Agent: {action.get('action', 'Unknown')} on node {action.get('node_id', 'Unknown')} - {'Success' if action.get('success', False) else 'Failed'}")

        # Get detailed campaign status
        campaign_status = red_agent.get_campaign_status()

        # Log step results
        step_result = {
            "step": step,
            "red_action": red_action,
            "blue_actions": blue_actions_results,
            "compromised_nodes": list(red_agent.get_compromised_nodes()),
            "patched_nodes": list(blue_agent.get_patched_nodes()),
            "alerts": env.alerts[-5:] if hasattr(env, 'alerts') else [],
            "campaign_status": campaign_status
        }

        results["steps"].append(step_result)

        # Save network snapshot every 5 steps
        if step % 5 == 0:
            env.save_to_file(f"network_snapshots/network_step_{step}_{timestamp}.json")

        # Display campaign progress
        print(f"Campaign Progress: {campaign_status['progress']:.2f}")
        print(f"Compromised Nodes: {campaign_status['compromised_nodes']}/{campaign_status['total_nodes']} ({campaign_status['network_compromise_percentage']:.1f}%)")
        print(f"Data Exfiltrated: {campaign_status['data_exfiltrated_kb']/1000:.2f} MB ({campaign_status['data_exfiltration_percentage']:.1f}%)")
        print(f"Backdoors Installed: {campaign_status['backdoors_installed']}")

        # Print recent logs
        print("\n[Recent Logs]")
        for log in env.logs[-5:]:
            print(f"  {log}")

        # Check if campaign is complete (all nodes compromised and all data exfiltrated)
        if (campaign_status['network_compromise_percentage'] > 90 and
            campaign_status['data_exfiltration_percentage'] > 90):
            print("\n!!! CAMPAIGN COMPLETE - NETWORK FULLY COMPROMISED AND DATA EXFILTRATED !!!")
            break

    # Calculate final metrics
    end_time = time.time()
    simulation_time = end_time - start_time

    campaign_status = red_agent.get_campaign_status()
    results["summary"]["total_compromised"] = len(red_agent.get_compromised_nodes())
    results["summary"]["total_patched"] = len(blue_agent.get_patched_nodes())
    results["summary"]["red_success_rate"] = red_successes / max(1, red_attempts)
    results["summary"]["blue_success_rate"] = blue_successes / max(1, blue_actions)
    results["summary"]["simulation_time"] = simulation_time
    results["summary"]["campaign_goal"] = campaign_status["goal"]
    results["summary"]["campaign_progress"] = campaign_status["progress"]
    results["summary"]["data_collected"] = campaign_status["data_collected"]
    results["summary"]["data_exfiltrated"] = campaign_status["data_exfiltrated_kb"]
    results["summary"]["data_exfiltration_percentage"] = campaign_status["data_exfiltration_percentage"]
    results["summary"]["lateral_movements"] = campaign_status["lateral_movements"]
    results["summary"]["backdoors_installed"] = campaign_status["backdoors_installed"]

    # Save final network state
    env.save_to_file(f"network_snapshots/network_final_{timestamp}.json")

    # Save results
    results_path = f"results/super_simulation_results_{timestamp}.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    # Generate report
    generate_report(results, timestamp)

    # Print summary
    print("\n=== Super Red Agent Simulation Complete ===")
    print(f"Total steps: {step}/{config['num_steps']}")
    print(f"Simulation time: {simulation_time:.2f} seconds")
    print(f"Compromised nodes: {len(red_agent.get_compromised_nodes())}/{len(list(env.graph.nodes()))} ({campaign_status['network_compromise_percentage']:.1f}%)")
    print(f"Patched nodes: {len(blue_agent.get_patched_nodes())}")
    print(f"Red agent success rate: {red_successes / max(1, red_attempts):.2f}")
    print(f"Blue agent success rate: {blue_successes / max(1, blue_actions):.2f}")
    print(f"Campaign goal: {campaign_status['goal']}")
    print(f"Campaign progress: {campaign_status['progress']:.2f}")
    print(f"Data exfiltrated: {campaign_status['data_exfiltrated_kb']/1000:.2f} MB ({campaign_status['data_exfiltration_percentage']:.1f}%)")
    print(f"Lateral movements: {campaign_status['lateral_movements']}")
    print(f"Backdoors installed: {campaign_status['backdoors_installed']}")
    print(f"Results saved to: {results_path}")

    return results

def generate_report(results, timestamp):
    """Generate a comprehensive HTML report of simulation results"""
    campaign_status = results["summary"]

    report_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HYDRA Super Red Agent Simulation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
            .metrics {{ display: flex; flex-wrap: wrap; }}
            .metric-card {{ background-color: #ffffff; border: 1px solid #e0e0e0;
                          border-radius: 5px; padding: 15px; margin: 10px; width: 200px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
            .critical {{ color: #e74c3c; }}
            .attack {{ background-color: #fff8f8; border-left: 4px solid #e74c3c;
                     padding: 10px; margin: 10px 0; }}
            .defense {{ background-color: #f8fff8; border-left: 4px solid #2ecc71;
                      padding: 10px; margin: 10px 0; }}
            .success {{ color: #2ecc71; }}
            .failure {{ color: #e74c3c; }}
            .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .data-table th, .data-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .data-table th {{ background-color: #f2f2f2; }}
            .data-table tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>HYDRA Super Red Agent Simulation Report</h1>
        <p>Simulation conducted on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

        <div class="summary">
            <h2>Executive Summary</h2>
            <p>This report presents the findings from a simulation conducted using HYDRA's Super Red Agent,
            which demonstrates advanced attack capabilities and provides a challenging test for blue teams.</p>

            <div class="metrics">
                <div class="metric-card">
                    <h3>Simulation Time</h3>
                    <div class="metric-value">{results["summary"]["simulation_time"]:.2f}s</div>
                </div>
                <div class="metric-card">
                    <h3>Compromised Nodes</h3>
                    <div class="metric-value critical">{results["summary"]["total_compromised"]}</div>
                </div>
                <div class="metric-card">
                    <h3>Patched Nodes</h3>
                    <div class="metric-value">{results["summary"]["total_patched"]}</div>
                </div>
                <div class="metric-card">
                    <h3>Red Success Rate</h3>
                    <div class="metric-value critical">{results["summary"]["red_success_rate"]*100:.1f}%</div>
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
                    <div class="metric-value critical">{results["summary"]["campaign_progress"]*100:.1f}%</div>
                </div>
                <div class="metric-card">
                    <h3>Data Exfiltrated</h3>
                    <div class="metric-value critical">{results["summary"]["data_exfiltrated"]/1000:.2f} MB</div>
                </div>
                <div class="metric-card">
                    <h3>Backdoors Installed</h3>
                    <div class="metric-value critical">{results["summary"]["backdoors_installed"]}</div>
                </div>
            </div>
        </div>

        <h2>Simulation Configuration</h2>
        <pre>{json.dumps(results["config"], indent=2)}</pre>

        <h2>Key Findings</h2>
        <p>The simulation revealed several critical security issues in your network:</p>
        <ul>
            <li class="critical">The Red Agent was able to compromise {results["summary"]["total_compromised"]} nodes.</li>
            <li class="critical">The Red Agent exfiltrated {results["summary"]["data_exfiltrated"]/1000:.2f} MB of sensitive data.</li>
            <li class="critical">The Red Agent installed {results["summary"]["backdoors_installed"]} backdoors for persistent access.</li>
            <li class="critical">The Red Agent performed {results["summary"]["lateral_movements"]} lateral movements.</li>
            <li>The Blue Agent successfully patched {results["summary"]["total_patched"]} nodes.</li>
        </ul>

        <h2>Recommendations</h2>
        <p>Based on the simulation results, consider the following critical recommendations:</p>
        <ol>
            <li>Implement network segmentation to limit lateral movement capabilities</li>
            <li>Deploy advanced endpoint detection and response (EDR) solutions</li>
            <li>Enhance data loss prevention (DLP) controls</li>
            <li>Implement multi-factor authentication across all systems</li>
            <li>Conduct regular vulnerability assessments and patch management</li>
            <li>Deploy honeypots to detect attacker movement</li>
            <li>Implement behavioral analytics to detect unusual network activity</li>
            <li>Enhance logging and monitoring capabilities</li>
        </ol>
    </body>
    </html>
    """

    # Save HTML report
    report_path = f"reports/super_simulation_report_{timestamp}.html"
    with open(report_path, "w") as f:
        f.write(report_content)

    print(f"Report generated: {report_path}")

def main():
    """Main function to run the super red agent simulation"""
    print("=" * 80)
    print("HYDRA SUPER RED AGENT SIMULATION")
    print("Advanced AI-based Red Team Simulation with Guaranteed Success")
    print("=" * 80)

    parser = argparse.ArgumentParser(description="HYDRA Super Red Agent Simulation")
    parser.add_argument("--network-size", choices=["small", "medium", "large"],
                        default="medium", help="Size of the network")
    parser.add_argument("--network-complexity", choices=["low", "medium", "high"],
                        default="medium", help="Complexity of the network")
    parser.add_argument("--num-steps", type=int, default=20,
                        help="Number of simulation steps")
    parser.add_argument("--red-skill", type=float, default=0.95,
                        help="Red agent skill level (0.0-1.0)")
    parser.add_argument("--threat-intel", type=str, default="data/threat_intelligence.json",
                        help="Path to threat intelligence data file")

    args = parser.parse_args()

    config = {
        "network_size": args.network_size,
        "network_complexity": args.network_complexity,
        "num_steps": args.num_steps,
        "red_skill_level": args.red_skill,
        "threat_intel_file": args.threat_intel
    }

    run_super_simulation(config)

    print("\nSimulation results are available in the 'results' directory.")
    print("Launch the dashboard with: streamlit run dashboard/advanced_dashboard.py")

if __name__ == "__main__":
    main()
