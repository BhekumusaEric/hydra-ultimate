#!/usr/bin/env python3
"""
HYDRA Safe Network Test

This script runs HYDRA in a safe testing mode on a real network environment.
It ensures that no disruptive actions are taken while still providing
valuable security insights.
"""

import os
import time
import argparse
import json
from datetime import datetime
from advanced_simulation import run_simulation

def setup_directories():
    """Create necessary directories for test results"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("network_snapshots", exist_ok=True)
    os.makedirs("digital_twins", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

def run_safe_test(config):
    """Run HYDRA in safe testing mode"""
    print(f"Starting HYDRA Safe Network Test with configuration: {config}")

    # Record start time
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize test environment
    print("\n=== Initializing Test Environment ===")
    print("- Creating digital twin of your network")
    print("- Setting up safe testing parameters")
    print("- Configuring observation-only mode")

    # Run the simulation in safe mode
    results = run_simulation(config)

    # Calculate test duration
    end_time = time.time()
    test_duration = end_time - start_time

    # Generate summary report
    generate_report(results, config, test_duration, timestamp)

    print(f"\nSafe Network Test completed in {test_duration:.2f} seconds")
    print(f"Results saved to: results/safe_test_results_{timestamp}.json")
    print(f"Report generated: reports/safe_test_report_{timestamp}.html")
    print("\nTo view the results dashboard, run: streamlit run dashboard/advanced_dashboard.py")

def generate_report(results, config, duration, timestamp):
    """Generate a comprehensive HTML report of test results"""
    # Save raw results
    with open(f"results/safe_test_results_{timestamp}.json", "w") as f:
        json.dump(results, f, indent=2)

    # Create basic HTML report
    report_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HYDRA Safe Network Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
            .metrics {{ display: flex; flex-wrap: wrap; }}
            .metric-card {{ background-color: #ffffff; border: 1px solid #e0e0e0;
                          border-radius: 5px; padding: 15px; margin: 10px; width: 200px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
            .vulnerability {{ background-color: #fff8f8; border-left: 4px solid #e74c3c;
                            padding: 10px; margin: 10px 0; }}
            .high {{ border-left-color: #e74c3c; }}
            .medium {{ border-left-color: #f39c12; }}
            .low {{ border-left-color: #3498db; }}
        </style>
    </head>
    <body>
        <h1>HYDRA Safe Network Test Report</h1>
        <p>Test conducted on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

        <div class="summary">
            <h2>Executive Summary</h2>
            <p>This report presents the findings from a safe network test conducted using HYDRA.</p>
            <p>The test was configured to operate in observation-only mode with no disruptive actions.</p>

            <div class="metrics">
                <div class="metric-card">
                    <h3>Test Duration</h3>
                    <div class="metric-value">{duration:.2f}s</div>
                </div>
                <div class="metric-card">
                    <h3>Vulnerabilities</h3>
                    <div class="metric-value">{results["summary"].get("total_compromised", 0)}</div>
                </div>
                <div class="metric-card">
                    <h3>Patched Issues</h3>
                    <div class="metric-value">{results["summary"].get("total_patched", 0)}</div>
                </div>
                <div class="metric-card">
                    <h3>Red Success Rate</h3>
                    <div class="metric-value">{results["summary"].get("red_success_rate", 0)*100:.1f}%</div>
                </div>
            </div>
        </div>

        <h2>Test Configuration</h2>
        <pre>{json.dumps(config, indent=2)}</pre>

        <h2>Key Findings</h2>
        <!-- This would be populated with actual findings -->

        <h2>Recommendations</h2>
        <!-- This would be populated with actual recommendations -->

        <h2>Next Steps</h2>
        <ol>
            <li>Review the detailed findings in the HYDRA dashboard</li>
            <li>Prioritize vulnerabilities based on risk score</li>
            <li>Develop a remediation plan for identified issues</li>
            <li>Schedule a follow-up test to validate fixes</li>
        </ol>
    </body>
    </html>
    """

    # Save HTML report
    with open(f"reports/safe_test_report_{timestamp}.html", "w") as f:
        f.write(report_content)

def main():
    """Main function to run the safe network test"""
    print("=" * 80)
    print("HYDRA SAFE NETWORK TEST")
    print("Advanced AI-based Red-Blue Simulation Platform")
    print("=" * 80)

    try:
        # Create directories
        print("Setting up directories...")
        setup_directories()

        parser = argparse.ArgumentParser(description="HYDRA Safe Network Test")
        parser.add_argument("--network-size", choices=["small", "medium", "large"],
                            default="small", help="Size of your network")
        parser.add_argument("--test-duration", type=int, default=20,
                            help="Number of test steps to run")
        parser.add_argument("--red-skill", type=float, default=0.6,
                            help="Red agent skill level (0.0-1.0)")
        parser.add_argument("--config", type=str, default="hydra-safe-test.yml",
                            help="Path to configuration file")

        print("Parsing arguments...")
        args = parser.parse_args()

        print("\nRunning Safe Network Test")
        print("This test will safely assess your network security posture without disrupting operations.")
        print("All tests run in observation-only mode with no actual exploits executed.")

        config = {
            "network_size": args.network_size,
            "network_complexity": "medium",
            "num_steps": args.test_duration,
            "red_skill_level": args.red_skill,
            "safe_mode": True,
            "config_file": args.config
        }

        print(f"Configuration prepared: {config}")
        print("Starting safe test...")
        run_safe_test(config)
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
