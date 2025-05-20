#!/usr/bin/env python3
"""
HYDRA Enhanced Simulation

This script runs a simulation using the Enhanced Red Agent with real-world attack patterns
to provide a more realistic security validation experience.
"""

import os
import time
import argparse
import json
import torch
import random
from datetime import datetime
from envs.enterprise_network import EnterpriseNetwork
from agents.enhanced_red_agent_new import EnhancedRedAgent
from agents.advanced_blue_agent import AdvancedBlueAgent

def setup_directories():
    """Create necessary directories for simulation results"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("network_snapshots", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

def run_enhanced_simulation(config):
    """Run a simulation with the Enhanced Red Agent"""
    print(f"Starting HYDRA Enhanced Simulation with configuration: {config}")

    # Create output directories if they don't exist
    setup_directories()

    # Record start time
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize environment
    env = EnterpriseNetwork(
        size=config['network_size'],
        complexity=config['network_complexity']
    )

    # Initialize agents
    red_agent = EnhancedRedAgent(
        env=env,
        skill_level=config['red_skill_level'],
        threat_intel_file=config['threat_intel_file']
    )

    # Load pre-trained model if specified
    if config.get('model_path') and os.path.exists(config['model_path']):
        try:
            red_agent.model.load_state_dict(torch.load(config['model_path']))
            print(f"Loaded pre-trained model from {config['model_path']}")
        except Exception as e:
            print(f"Error loading model: {e}")

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
            "campaign_progress": 0
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
    print("\n=== Starting Enhanced Simulation ===\n")
    print(f"Red Agent Campaign Goal: {red_agent.campaign_goal}")

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

        # Save network snapshot every 10 steps
        if step % 10 == 0:
            env.save_to_file(f"network_snapshots/network_step_{step}_{timestamp}.json")

        # Display campaign progress
        campaign_status = red_agent.get_campaign_status()
        print(f"Campaign Progress: {campaign_status['progress']:.2f}")
        print(f"Compromised Nodes: {campaign_status['compromised_nodes']}")

        # Print recent logs
        print("\n[Recent Logs]")
        for log in env.logs[-5:]:
            print(f"  {log}")

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
    results["summary"]["lateral_movements"] = campaign_status["lateral_movements"]

    # Save final network state
    env.save_to_file(f"network_snapshots/network_final_{timestamp}.json")

    # Save results
    results_path = f"results/enhanced_simulation_results_{timestamp}.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    # Generate report
    generate_report(results, timestamp)

    # Print summary
    print("\n=== Enhanced Simulation Complete ===")
    print(f"Total steps: {config['num_steps']}")
    print(f"Simulation time: {simulation_time:.2f} seconds")
    print(f"Compromised nodes: {len(red_agent.get_compromised_nodes())}")
    print(f"Patched nodes: {len(blue_agent.get_patched_nodes())}")
    print(f"Red agent success rate: {red_successes / max(1, red_attempts):.2f}")
    print(f"Blue agent success rate: {blue_successes / max(1, blue_actions):.2f}")
    print(f"Campaign goal: {campaign_status['goal']}")
    print(f"Campaign progress: {campaign_status['progress']:.2f}")
    print(f"Data collected: {campaign_status['data_collected']}")
    print(f"Lateral movements: {campaign_status['lateral_movements']}")
    print(f"Results saved to: {results_path}")

    return results

def generate_report(results, timestamp):
    """Generate a comprehensive HTML report of simulation results with detailed attack paths and MITRE ATT&CK mapping"""

    # Extract attack techniques used
    attack_techniques = {}
    attack_paths = []
    credential_theft_attempts = []
    lolbin_techniques = []

    # Process steps to extract attack information
    current_path = []
    current_node = None

    for step in results["steps"]:
        red_action = step.get("red_action", {})
        if not red_action:
            continue

        # Track attack techniques
        attack_type = red_action.get("attack_type", "unknown")
        if attack_type not in attack_techniques:
            attack_techniques[attack_type] = 0
        attack_techniques[attack_type] += 1

        # Track attack paths
        if red_action.get("success", False):
            target = red_action.get("target", None)
            if target != current_node:
                if current_node is not None:
                    current_path.append({
                        "source": current_node,
                        "target": target,
                        "technique": attack_type,
                        "timestamp": red_action.get("timestamp", "")
                    })
                current_node = target

        # If this is a new path or the end of a path
        if (not red_action.get("success", False) and current_path) or (len(current_path) > 0 and step["step"] == results["config"]["num_steps"]):
            if len(current_path) > 0:
                attack_paths.append(current_path)
                current_path = []
                current_node = None

        # Check for credential theft or living-off-the-land techniques
        if "credential_theft" in attack_type or "credential" in attack_type.lower():
            credential_theft_attempts.append(red_action)

        if "lolbin" in attack_type.lower() or "living_off_the_land" in attack_type.lower():
            lolbin_techniques.append(red_action)

    # Create the report content
    report_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HYDRA Enhanced Simulation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1, h2, h3, h4 {{ color: #2c3e50; }}
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
            .attack-path {{ background-color: #f9f9f9; border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px; }}
            .attack-path-step {{ margin: 5px 0; padding: 5px; border-bottom: 1px dashed #ddd; }}
            .technique-card {{ background-color: #f0f7ff; border-left: 4px solid #3498db; padding: 10px; margin: 10px 0; }}
            .mitre-tag {{ display: inline-block; background-color: #34495e; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin-right: 5px; }}
            .credential-theft {{ background-color: #fff0f7; border-left: 4px solid #9b59b6; padding: 10px; margin: 10px 0; }}
            .lolbin {{ background-color: #fffaf0; border-left: 4px solid #f39c12; padding: 10px; margin: 10px 0; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h1>HYDRA Enhanced Simulation Report</h1>
        <p>Simulation conducted on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

        <div class="summary">
            <h2>Executive Summary</h2>
            <p>This report presents the findings from an enhanced simulation conducted using HYDRA with real-world attack patterns.</p>
            <p>The simulation tested your network against advanced attack techniques including credential theft, privilege escalation, and living-off-the-land techniques.</p>

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
            </div>
        </div>

        <h2>Simulation Configuration</h2>
        <pre>{json.dumps(results["config"], indent=2)}</pre>

        <h2>Key Findings</h2>
        <p>The simulation revealed several important insights about your network's security posture:</p>
        <ul>
            <li>The Red Agent was able to compromise {results["summary"]["total_compromised"]} nodes.</li>
            <li>The Blue Agent successfully patched {results["summary"]["total_patched"]} nodes.</li>
            <li>The Red Agent's campaign goal was <strong>{results["summary"]["campaign_goal"]}</strong> and achieved {results["summary"]["campaign_progress"]*100:.1f}% progress.</li>
            <li>The Red Agent collected data from {results["summary"].get("data_collected", 0)} sources.</li>
            <li>The Red Agent performed {results["summary"].get("lateral_movements", 0)} lateral movements.</li>
            <li>The simulation identified {len(attack_paths)} distinct attack paths.</li>
            <li>The Red Agent attempted {len(credential_theft_attempts)} credential theft operations.</li>
            <li>The Red Agent used {len(lolbin_techniques)} living-off-the-land techniques.</li>
        </ul>

        <h2>MITRE ATT&CK Techniques Used</h2>
        <p>The simulation utilized techniques mapped to the MITRE ATT&CK framework:</p>
        <div class="technique-card">
            <h3>Initial Access</h3>
            <span class="mitre-tag">T1190</span> Exploit Public-Facing Application<br>
            <span class="mitre-tag">T1133</span> External Remote Services<br>
            <span class="mitre-tag">T1078</span> Valid Accounts
        </div>

        <div class="technique-card">
            <h3>Execution</h3>
            <span class="mitre-tag">T1059</span> Command and Scripting Interpreter<br>
            <span class="mitre-tag">T1053</span> Scheduled Task/Job<br>
            <span class="mitre-tag">T1569</span> System Services
        </div>

        <div class="technique-card">
            <h3>Persistence</h3>
            <span class="mitre-tag">T1547</span> Boot or Logon Autostart Execution<br>
            <span class="mitre-tag">T1136</span> Create Account<br>
            <span class="mitre-tag">T1053</span> Scheduled Task/Job<br>
            <span class="mitre-tag">T1505</span> Server Software Component
        </div>

        <div class="technique-card">
            <h3>Privilege Escalation</h3>
            <span class="mitre-tag">T1548</span> Abuse Elevation Control Mechanism<br>
            <span class="mitre-tag">T1134</span> Access Token Manipulation<br>
            <span class="mitre-tag">T1068</span> Exploitation for Privilege Escalation
        </div>

        <div class="technique-card">
            <h3>Credential Access</h3>
            <span class="mitre-tag">T1110</span> Brute Force<br>
            <span class="mitre-tag">T1555</span> Credentials from Password Stores<br>
            <span class="mitre-tag">T1003</span> OS Credential Dumping<br>
            <span class="mitre-tag">T1558</span> Steal or Forge Kerberos Tickets
        </div>
    """

    # Add attack paths section if there are any
    if attack_paths:
        report_content += """
        <h2>Attack Paths</h2>
        <p>The following attack paths were identified during the simulation:</p>
        """

        for i, path in enumerate(attack_paths):
            report_content += f"""
            <div class="attack-path">
                <h3>Attack Path #{i+1} ({len(path)} steps)</h3>
                <ol>
            """

            for step in path:
                report_content += f"""
                    <li class="attack-path-step">
                        Node {step["source"]} → Node {step["target"]} using {step["technique"]} ({step["timestamp"]})
                    </li>
                """

            report_content += """
                </ol>
            </div>
            """

    # Add credential theft section if there are any attempts
    if credential_theft_attempts:
        report_content += """
        <h2>Credential Theft Techniques</h2>
        <p>The following credential theft techniques were attempted during the simulation:</p>
        <table>
            <tr>
                <th>Target Node</th>
                <th>Technique</th>
                <th>Success</th>
                <th>Detected</th>
                <th>Timestamp</th>
            </tr>
        """

        for attempt in credential_theft_attempts:
            success_class = "success" if attempt.get("success", False) else "failure"
            detected_class = "failure" if attempt.get("detected", False) else "success"

            report_content += f"""
            <tr>
                <td>Node {attempt.get("target", "unknown")}</td>
                <td>{attempt.get("attack_type", "unknown")}</td>
                <td class="{success_class}">{attempt.get("success", False)}</td>
                <td class="{detected_class}">{attempt.get("detected", False)}</td>
                <td>{attempt.get("timestamp", "unknown")}</td>
            </tr>
            """

        report_content += """
        </table>
        """

    # Add living-off-the-land section if there are any techniques used
    if lolbin_techniques:
        report_content += """
        <h2>Living-Off-The-Land Techniques</h2>
        <p>The following living-off-the-land techniques were used during the simulation:</p>
        <table>
            <tr>
                <th>Target Node</th>
                <th>Technique</th>
                <th>Success</th>
                <th>Detected</th>
                <th>Timestamp</th>
            </tr>
        """

        for technique in lolbin_techniques:
            success_class = "success" if technique.get("success", False) else "failure"
            detected_class = "failure" if technique.get("detected", False) else "success"

            report_content += f"""
            <tr>
                <td>Node {technique.get("target", "unknown")}</td>
                <td>{technique.get("attack_type", "unknown")}</td>
                <td class="{success_class}">{technique.get("success", False)}</td>
                <td class="{detected_class}">{technique.get("detected", False)}</td>
                <td>{technique.get("timestamp", "unknown")}</td>
            </tr>
            """

        report_content += """
        </table>
        """

    # Add recommendations section
    report_content += """
        <h2>Recommendations</h2>
        <p>Based on the simulation results, consider the following recommendations:</p>
        <ol>
            <li>Improve detection capabilities for credential theft techniques, particularly memory dumping and token manipulation.</li>
            <li>Enhance network segmentation to limit lateral movement between critical systems.</li>
            <li>Implement stronger access controls and privileged access management for critical systems.</li>
            <li>Regularly patch vulnerabilities to reduce the attack surface.</li>
            <li>Deploy additional monitoring for living-off-the-land techniques that abuse legitimate system tools.</li>
            <li>Implement application whitelisting to prevent execution of unauthorized scripts and binaries.</li>
            <li>Use multi-factor authentication to mitigate the impact of credential theft.</li>
            <li>Deploy endpoint detection and response (EDR) solutions to detect and respond to advanced attacks.</li>
        </ol>
    </body>
    </html>
    """

    # Save HTML report
    report_path = f"reports/enhanced_simulation_report_{timestamp}.html"
    with open(report_path, "w") as f:
        f.write(report_content)

    print(f"Report generated: {report_path}")

def main():
    """Main function to run the enhanced simulation"""
    print("=" * 80)
    print("HYDRA ENHANCED SIMULATION")
    print("Advanced AI-based Red-Blue Simulation with Real-World Attack Patterns")
    print("=" * 80)

    parser = argparse.ArgumentParser(description="HYDRA Enhanced Simulation")
    parser.add_argument("--network-size", choices=["small", "medium", "large"],
                        default="medium", help="Size of the network")
    parser.add_argument("--network-complexity", choices=["low", "medium", "high"],
                        default="medium", help="Complexity of the network")
    parser.add_argument("--num-steps", type=int, default=30,
                        help="Number of simulation steps")
    parser.add_argument("--red-skill", type=float, default=0.7,
                        help="Red agent skill level (0.0-1.0)")
    parser.add_argument("--threat-intel", type=str, default="data/threat_intelligence.json",
                        help="Path to threat intelligence data file")
    parser.add_argument("--model", type=str, default=None,
                        help="Path to pre-trained model file")

    args = parser.parse_args()

    config = {
        "network_size": args.network_size,
        "network_complexity": args.network_complexity,
        "num_steps": args.num_steps,
        "red_skill_level": args.red_skill,
        "threat_intel_file": args.threat_intel,
        "model_path": args.model
    }

    run_enhanced_simulation(config)

    print("\nSimulation results are available in the 'results' directory.")
    print("Launch the dashboard with: streamlit run dashboard/advanced_dashboard.py")

if __name__ == "__main__":
    main()
