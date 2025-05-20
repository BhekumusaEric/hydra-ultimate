# HYDRA Enhanced Red Agent

This package enhances HYDRA's Red Agent with real-world attack patterns, threat intelligence, and advanced learning capabilities to provide a more realistic security validation experience.

## Overview

The Enhanced Red Agent introduces several significant improvements:

1. **Real-World Attack Patterns**: Implements attack strategies based on actual threat actors like APT29, APT41, and modern ransomware groups.

2. **MITRE ATT&CK Framework Integration**: Aligns attack techniques with the MITRE ATT&CK framework for better mapping to real-world threats.

3. **Advanced Learning Capabilities**: Uses deep reinforcement learning to adapt attack strategies based on success and detection rates.

4. **Campaign-Based Attacks**: Simulates realistic attack campaigns with specific goals like data theft, persistence, disruption, or ransomware deployment.

5. **Threat Intelligence Integration**: Incorporates real-world threat intelligence to inform attack decisions and techniques.

## Components

This package includes:

- **Enhanced Red Agent Implementation** (`agents/enhanced_red_agent.py`): The core agent implementation with advanced attack strategies and learning capabilities.

- **Threat Intelligence Data** (`data/threat_intelligence.json`): Real-world threat intelligence data used to train and inform the agent.

- **Training Script** (`train_enhanced_red_agent.py`): Script to train the Enhanced Red Agent with real-world data.

- **Enhanced Simulation Script** (`run_enhanced_simulation.py`): Script to run simulations with the Enhanced Red Agent.

## Installation

No additional installation is required beyond the standard HYDRA platform. The Enhanced Red Agent is designed to work with your existing HYDRA installation.

## Usage

### Training the Enhanced Red Agent

To train the Enhanced Red Agent with real-world threat intelligence:

```bash
./train_enhanced_red_agent.py --network-size medium --num-episodes 50 --steps-per-episode 100
```

Options:
- `--network-size`: Size of the network for training (small, medium, large)
- `--network-complexity`: Complexity of the network (low, medium, high)
- `--num-episodes`: Number of training episodes
- `--steps-per-episode`: Number of steps per episode
- `--red-skill`: Initial red agent skill level (0.0-1.0)
- `--learning-rate`: Learning rate for neural network
- `--threat-intel`: Path to threat intelligence data file

### Running Enhanced Simulations

To run a simulation with the Enhanced Red Agent:

```bash
./run_enhanced_simulation.py --network-size medium --num-steps 30
```

Options:
- `--network-size`: Size of the network (small, medium, large)
- `--network-complexity`: Complexity of the network (low, medium, high)
- `--num-steps`: Number of simulation steps
- `--red-skill`: Red agent skill level (0.0-1.0)
- `--threat-intel`: Path to threat intelligence data file
- `--model`: Path to pre-trained model file (optional)

### Using the GUI

You can also use the Enhanced Red Agent through the HYDRA dashboard:

1. Start the dashboard:
   ```bash
   streamlit run dashboard/advanced_dashboard.py
   ```

2. In the dashboard, navigate to the "Agent Configuration" section

3. Select "Enhanced Red Agent" as the Red Agent type

4. Configure the agent parameters:
   - Skill Level
   - Threat Intelligence File
   - Pre-trained Model (optional)

5. Run the simulation through the dashboard interface

## Advanced Attack Strategies

The Enhanced Red Agent includes several sophisticated attack strategies based on real-world threat actors:

### APT29 Strategy (Cozy Bear)

- **Description**: Sophisticated state-sponsored threat actor known for stealthy operations
- **Tactics**: Initial access, execution, persistence, privilege escalation, defense evasion, credential access, discovery, lateral movement, collection, exfiltration
- **Target Preference**: High-value targets with low security visibility

### APT41 Strategy (Double Dragon)

- **Description**: Dual espionage and financially-motivated threat actor
- **Tactics**: Initial access, execution, persistence, privilege escalation, defense evasion, credential access, discovery, lateral movement, collection, exfiltration, impact
- **Target Preference**: Databases, servers, and cloud instances

### Ransomware Strategy

- **Description**: Modern ransomware operation with double extortion tactics
- **Tactics**: Initial access, execution, privilege escalation, discovery, lateral movement, collection, exfiltration, impact
- **Target Preference**: Data storage systems for maximum impact

## Campaign Goals

The Enhanced Red Agent can pursue different campaign goals:

1. **Data Theft**: Focus on stealing sensitive data from high-value targets
2. **Persistence**: Establish long-term access across diverse systems
3. **Disruption**: Disrupt operations by compromising critical systems
4. **Ransomware**: Deploy ransomware across the network for maximum impact

## Customizing Threat Intelligence

You can customize the threat intelligence data to focus on specific threats relevant to your environment:

1. Edit the `data/threat_intelligence.json` file
2. Add or modify threat actors, techniques, and vulnerabilities
3. Adjust success rates and detection rates based on your environment
4. Re-train the agent with your customized threat intelligence

## Viewing Results

After running a simulation:

1. Check the `results` directory for detailed JSON results
2. View HTML reports in the `reports` directory
3. Explore network snapshots in the `network_snapshots` directory
4. Use the dashboard to visualize attack paths and compromised nodes

## Best Practices

1. **Start with Training**: Train the agent on a small network before running full simulations
2. **Gradually Increase Complexity**: Start with simple scenarios and gradually increase complexity
3. **Customize Threat Intelligence**: Tailor the threat intelligence to match your threat landscape
4. **Compare Strategies**: Run simulations with different attack strategies to understand various threat models
5. **Analyze Campaign Progress**: Focus on how different campaigns progress to understand your security posture

## Troubleshooting

- **Agent Not Learning**: Increase the number of training episodes and steps per episode
- **Too Aggressive**: Reduce the red skill level or modify the threat intelligence data
- **Too Stealthy**: Increase the detection rates in the threat intelligence data
- **Performance Issues**: Reduce network size or complexity for faster simulations

## Support

For additional assistance:
- Documentation: [docs.hydra-security.ai](https://docs.hydra-security.ai)
- Knowledge Base: [kb.hydra-security.ai](https://kb.hydra-security.ai)
- Support Portal: [support.hydra-security.ai](https://support.hydra-security.ai)
