#!/usr/bin/env python3
"""
HYDRA Enterprise Simulation Runner

This script runs a comprehensive enterprise-grade simulation with HYDRA,
demonstrating its capabilities for enterprise security testing.
"""

import os
import time
import argparse
from advanced_simulation import run_simulation

def main():
    """Run enterprise simulations with different configurations"""
    print("=" * 80)
    print("HYDRA ENTERPRISE SIMULATION SUITE")
    print("Advanced AI-based Red-Blue Simulation Platform")
    print("=" * 80)
    
    # Create directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("network_snapshots", exist_ok=True)
    
    parser = argparse.ArgumentParser(description="HYDRA Enterprise Simulation Suite")
    parser.add_argument("--mode", choices=["quick", "standard", "comprehensive"], 
                        default="standard", help="Simulation mode")
    args = parser.parse_args()
    
    if args.mode == "quick":
        print("\nRunning Quick Assessment Mode")
        print("This mode runs a small simulation to quickly assess basic security posture.")
        
        config = {
            "network_size": "small",
            "network_complexity": "medium",
            "num_steps": 20,
            "red_skill_level": 0.6
        }
        
        start_time = time.time()
        run_simulation(config)
        end_time = time.time()
        
        print(f"\nQuick Assessment completed in {end_time - start_time:.2f} seconds")
        
    elif args.mode == "comprehensive":
        print("\nRunning Comprehensive Enterprise Assessment")
        print("This mode runs multiple simulations with different configurations to provide a comprehensive security assessment.")
        
        # Configuration 1: Basic Infrastructure
        print("\n[1/3] Running Basic Infrastructure Simulation")
        config1 = {
            "network_size": "medium",
            "network_complexity": "medium",
            "num_steps": 50,
            "red_skill_level": 0.7
        }
        run_simulation(config1)
        
        # Configuration 2: Advanced Persistent Threat
        print("\n[2/3] Running Advanced Persistent Threat Simulation")
        config2 = {
            "network_size": "medium",
            "network_complexity": "high",
            "num_steps": 50,
            "red_skill_level": 0.9
        }
        run_simulation(config2)
        
        # Configuration 3: Large Enterprise
        print("\n[3/3] Running Large Enterprise Simulation")
        config3 = {
            "network_size": "large",
            "network_complexity": "medium",
            "num_steps": 30,
            "red_skill_level": 0.8
        }
        run_simulation(config3)
        
        print("\nComprehensive Enterprise Assessment completed")
        print("Please check the dashboard for detailed analysis and comparison of all simulations.")
        
    else:  # standard
        print("\nRunning Standard Assessment Mode")
        print("This mode runs a medium-sized simulation with balanced parameters.")
        
        config = {
            "network_size": "medium",
            "network_complexity": "medium",
            "num_steps": 30,
            "red_skill_level": 0.7
        }
        
        start_time = time.time()
        run_simulation(config)
        end_time = time.time()
        
        print(f"\nStandard Assessment completed in {end_time - start_time:.2f} seconds")
    
    print("\nSimulation results are available in the 'results' directory.")
    print("Launch the dashboard with: streamlit run dashboard/advanced_dashboard.py")

if __name__ == "__main__":
    main()
