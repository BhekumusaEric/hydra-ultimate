"""
Minimal version of the HYDRA dashboard for Streamlit Cloud deployment.
This file contains simplified versions of the functions needed for the dashboard.
"""

import os
import json
import glob
import pandas as pd
import networkx as nx
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Helper functions
def load_simulation_results():
    """Load all simulation results files"""
    # First try to load from the regular results directory
    result_files = glob.glob("results/simulation_results_*.json") + glob.glob("results/enhanced_simulation_results_*.json")

    # If no files found, try the sample_data directory
    if not result_files:
        result_files = glob.glob("sample_data/results/enhanced_simulation_results_*.json")

    # If still no files found, return empty list
    if not result_files:
        return []

    results = []
    for file_path in result_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")

    return results

def load_network_snapshots(timestamp):
    """Load network snapshots for a specific simulation"""
    # First try to load from the regular network_snapshots directory
    snapshot_files = glob.glob(f"network_snapshots/network_*_{timestamp}.json")

    # If no files found, try the sample_data directory
    if not snapshot_files:
        snapshot_files = glob.glob(f"sample_data/network_snapshots/network_*_{timestamp}.json")

    # If still no files found, return empty list
    if not snapshot_files:
        return []

    snapshots = []
    for file_path in snapshot_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                snapshots.append(data)
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")

    return snapshots

def extract_credential_theft_attempts(simulation_data):
    """Extract credential theft attempts from simulation data"""
    attempts = []

    for step_data in simulation_data.get('steps', []):
        red_action = step_data.get('red_action', {})
        if red_action.get('attack_type') == 'credential_theft':
            attempts.append({
                'node_id': red_action.get('target'),
                'technique': red_action.get('technique', 'unknown'),
                'success': red_action.get('success', False),
                'detected': red_action.get('detected', False),
                'timestamp': red_action.get('timestamp', 'unknown')
            })

    return attempts

def extract_lolbin_techniques(simulation_data):
    """Extract living-off-the-land techniques from simulation data"""
    techniques = []

    for step_data in simulation_data.get('steps', []):
        red_action = step_data.get('red_action', {})
        if red_action.get('attack_type') == 'lolbin':
            techniques.append({
                'node_id': red_action.get('target'),
                'technique': red_action.get('technique', 'unknown'),
                'purpose': red_action.get('purpose', 'unknown'),
                'success': red_action.get('success', False),
                'detected': red_action.get('detected', False),
                'timestamp': red_action.get('timestamp', 'unknown')
            })

    return techniques

def extract_attack_paths(simulation_data):
    """Extract attack paths from simulation data"""
    # Simplified version that returns a single path
    path = []

    for step_data in simulation_data.get('steps', []):
        red_action = step_data.get('red_action', {})
        if red_action.get('success', False) and 'source' in red_action and 'target' in red_action:
            path.append({
                'source': red_action.get('source'),
                'target': red_action.get('target'),
                'technique': red_action.get('attack_type', 'unknown'),
                'timestamp': red_action.get('timestamp', 'unknown')
            })

    return [path] if path else []

def extract_data_theft(simulation_data):
    """Extract data theft information from simulation data"""
    data_theft_info = []

    for step_data in simulation_data.get('steps', []):
        campaign_status = step_data.get('campaign_status', {})
        if campaign_status and campaign_status.get('goal') == 'data_theft':
            data_theft_info.append({
                'step': step_data.get('step', 0),
                'progress': campaign_status.get('progress', 0),
                'data_collected': campaign_status.get('data_collected', 0),
                'compromised_nodes': len(step_data.get('compromised_nodes', []))
            })

    return data_theft_info

def create_mitre_attack_mapping():
    """Create a mapping of MITRE ATT&CK tactics and techniques"""
    return {
        "Initial Access": {
            "T1190": "Exploit Public-Facing Application",
            "T1133": "External Remote Services",
            "T1566": "Phishing"
        },
        "Execution": {
            "T1059": "Command and Scripting Interpreter",
            "T1053": "Scheduled Task/Job",
            "T1204": "User Execution"
        },
        "Persistence": {
            "T1136": "Create Account",
            "T1098": "Account Manipulation",
            "T1547": "Boot or Logon Autostart Execution"
        },
        "Privilege Escalation": {
            "T1548": "Abuse Elevation Control Mechanism",
            "T1068": "Exploitation for Privilege Escalation",
            "T1078": "Valid Accounts"
        },
        "Defense Evasion": {
            "T1070": "Indicator Removal",
            "T1027": "Obfuscated Files or Information",
            "T1218": "System Binary Proxy Execution"
        },
        "Credential Access": {
            "T1110": "Brute Force",
            "T1003": "OS Credential Dumping",
            "T1552": "Unsecured Credentials"
        },
        "Discovery": {
            "T1087": "Account Discovery",
            "T1018": "Remote System Discovery",
            "T1082": "System Information Discovery"
        },
        "Lateral Movement": {
            "T1021": "Remote Services",
            "T1091": "Replication Through Removable Media",
            "T1570": "Lateral Tool Transfer"
        },
        "Collection": {
            "T1560": "Archive Collected Data",
            "T1119": "Automated Collection",
            "T1115": "Clipboard Data"
        },
        "Command and Control": {
            "T1071": "Application Layer Protocol",
            "T1105": "Ingress Tool Transfer",
            "T1572": "Protocol Tunneling"
        },
        "Exfiltration": {
            "T1048": "Exfiltration Over Alternative Protocol",
            "T1041": "Exfiltration Over C2 Channel",
            "T1567": "Exfiltration Over Web Service"
        },
        "Impact": {
            "T1485": "Data Destruction",
            "T1486": "Data Encrypted for Impact",
            "T1489": "Service Stop"
        }
    }

def create_attack_defense_timeline(simulation_data):
    """Create a timeline of attack and defense actions"""
    # Simplified version that returns a figure
    steps = []
    attack_success = []
    attack_failure = []
    defense_success = []
    defense_failure = []

    for step_data in simulation_data.get('steps', []):
        step = step_data.get('step', 0)
        steps.append(step)

        # Attack metrics
        red_action = step_data.get('red_action', {})
        if red_action:
            if red_action.get('success', False):
                attack_success.append(1)
                attack_failure.append(0)
            else:
                attack_success.append(0)
                attack_failure.append(1)
        else:
            attack_success.append(0)
            attack_failure.append(0)

        # Defense metrics
        blue_actions = step_data.get('blue_actions', [])
        success_count = sum(1 for action in blue_actions if action.get('success', False))
        failure_count = len(blue_actions) - success_count

        defense_success.append(success_count)
        defense_failure.append(failure_count)

    # Create figure
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=steps,
        y=attack_success,
        name='Successful Attacks',
        marker_color='red'
    ))

    fig.add_trace(go.Bar(
        x=steps,
        y=attack_failure,
        name='Failed Attacks',
        marker_color='pink'
    ))

    fig.add_trace(go.Bar(
        x=steps,
        y=defense_success,
        name='Successful Defenses',
        marker_color='green'
    ))

    fig.add_trace(go.Bar(
        x=steps,
        y=defense_failure,
        name='Failed Defenses',
        marker_color='lightgreen'
    ))

    fig.update_layout(
        title='Attack & Defense Actions Over Time',
        xaxis_title='Simulation Step',
        yaxis_title='Number of Actions',
        barmode='group',
        height=400
    )

    return fig

def create_compromise_patch_chart(simulation_data):
    """Create a chart showing compromised vs patched nodes over time"""
    steps = []
    compromised = []
    patched = []

    for step_data in simulation_data.get('steps', []):
        step = step_data.get('step', 0)
        steps.append(step)
        compromised.append(len(step_data.get('compromised_nodes', [])))
        patched.append(len(step_data.get('patched_nodes', [])))

    # Create figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=steps,
        y=compromised,
        mode='lines+markers',
        name='Compromised Nodes',
        line=dict(color='red', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=steps,
        y=patched,
        mode='lines+markers',
        name='Patched Nodes',
        line=dict(color='green', width=2)
    ))

    fig.update_layout(
        title='Compromised vs Patched Nodes Over Time',
        xaxis_title='Simulation Step',
        yaxis_title='Number of Nodes',
        legend_title='Node Status',
        height=400
    )

    return fig

def visualize_network(network_data, attack_paths=None):
    """Visualize network graph using Plotly with attack paths highlighted"""
    # Convert node-link data to NetworkX graph
    G = nx.node_link_graph(network_data['graph'])

    # Get node positions using a layout algorithm
    pos = nx.spring_layout(G, seed=42)

    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        # Get node attributes
        node_data = G.nodes[node]
        node_type = node_data.get('type', 'unknown')
        vulnerabilities = node_data.get('vulnerabilities', [])

        # Determine node color based on compromise status
        if node in network_data.get('compromised_nodes', []):
            color = 'red'  # Compromised
        elif node in network_data.get('patched_nodes', []):
            color = 'green'  # Patched
        else:
            color = 'blue'  # Normal

        node_color.append(color)

        # Determine node size based on type
        size_map = {
            'database': 15,
            'server': 12,
            'router': 10,
            'firewall': 13,
            'cloud_instance': 11,
            'workstation': 8
        }
        node_size.append(size_map.get(node_type, 10))

        # Create hover text
        vuln_text = '<br>'.join([f"- {v.get('type')}: Severity {v.get('severity', 0):.1f}"
                                for v in vulnerabilities[:3]])
        if len(vulnerabilities) > 3:
            vuln_text += f"<br>- ...and {len(vulnerabilities) - 3} more"

        text = f"Node {node} ({node_type})<br>Vulnerabilities: {len(vulnerabilities)}<br>{vuln_text}"
        node_text.append(text)

    # Create edge traces
    edge_x = []
    edge_y = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    # Create node trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            color=node_color,
            size=node_size,
            line=dict(width=1, color='#888'),
        )
    )

    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=0.5, color='#888'),
        hoverinfo='none'
    )

    # Create figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=f"Network Topology - Step {network_data.get('step', 'N/A')}",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600,
        )
    )

    # Add attack paths if provided
    if attack_paths:
        for i, path in enumerate(attack_paths):
            path_edge_x = []
            path_edge_y = []
            path_edge_text = []

            for step in path:
                source = step.get('source')
                target = step.get('target')
                technique = step.get('technique', 'unknown')

                if source in G.nodes and target in G.nodes:
                    x0, y0 = pos[source]
                    x1, y1 = pos[target]
                    path_edge_x.extend([x0, x1, None])
                    path_edge_y.extend([y0, y1, None])
                    path_edge_text.extend([f"Attack: {technique}", f"Attack: {technique}", ""])

            # Add attack path trace
            if path_edge_x:
                path_trace = go.Scatter(
                    x=path_edge_x, y=path_edge_y,
                    mode='lines',
                    line=dict(width=2, color='red'),
                    hoverinfo='text',
                    text=path_edge_text,
                    name=f"Attack Path {i+1}"
                )
                fig.add_trace(path_trace)

    return fig

def main():
    """Main dashboard application"""
    # Custom CSS with enhanced visual elements
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #0066cc;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #0066cc;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }
        .card {
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .metric-card {
            background-color: #f0f2f6;
            border-left: 5px solid #0066cc;
        }
        .alert-card {
            background-color: #fff0f0;
            border-left: 5px solid #cc0000;
        }
        .success-card {
            background-color: #f0fff0;
            border-left: 5px solid #00cc00;
        }
        .info-text {
            font-size: 0.9rem;
            color: #444;
            margin-top: 0.5rem;
        }
        .highlight {
            color: #0066cc;
            font-weight: bold;
            font-size: 2rem;
        }
        .footer {
            text-align: center;
            margin-top: 3rem;
            color: #666;
            font-size: 0.8rem;
        }
        .credential-theft-card {
            background-color: #f8f0ff;
            border-left: 5px solid #9b59b6;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .lolbin-card {
            background-color: #fffaf0;
            border-left: 5px solid #f39c12;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .mitre-tag {
            display: inline-block;
            background-color: #34495e;
            color: white;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-right: 5px;
            margin-bottom: 5px;
        }
        .mitre-tactic {
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 5px;
            color: #333333;
        }
        .attack-path-card {
            background-color: #f0f7ff;
            border-left: 5px solid #3498db;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .attack-button {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .data-theft-card {
            background-color: #e8f4f8;
            border-left: 5px solid #3498db;
            padding: 1.2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* New styles for enhanced dashboard */
        .overall-result-card {
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .overall-result-card h3 {
            font-size: 1.8rem;
            margin-bottom: 1rem;
            font-weight: bold;
            color: #333333;
        }
        .overall-result-card p {
            font-size: 1.1rem;
            color: #333333;
            margin-bottom: 0.5rem;
        }
        .attack-success {
            background-color: #ffebee;
            border: 2px solid #f44336;
        }
        .defense-success {
            background-color: #e8f5e9;
            border: 2px solid #4caf50;
        }
        .progress-container {
            width: 100%;
            height: 20px;
            background-color: #f0f0f0;
            border-radius: 10px;
            margin: 10px 0;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background-color: #e74c3c;
            border-radius: 10px;
        }

        /* Enhanced credential theft visualization */
        .credential-details {
            background-color: #f8f0ff;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
            border: 1px solid #9b59b6;
        }
        .credential-item {
            padding: 8px;
            margin-bottom: 5px;
            background-color: #fff;
            border-radius: 4px;
            border-left: 3px solid #9b59b6;
        }

        /* Enhanced data theft visualization */
        .data-details {
            background-color: #e8f4f8;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
            border: 1px solid #3498db;
        }
        .data-item {
            padding: 8px;
            margin-bottom: 5px;
            background-color: #fff;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }

        /* Fix specific areas with white text on white background */
        .attack-path-card li {
            color: #333333; /* Dark text for attack path steps */
        }
        .credential-theft-card p, .lolbin-card p, .data-theft-card p {
            color: #333333; /* Dark text for card content */
        }
        .attack-path-step {
            color: #333333; /* Dark text for attack path steps */
        }

        /* Fix for Streamlit's tab text */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            color: #333333; /* Dark text for tab labels */
        }

        /* Status indicators */
        .status-success {
            color: #4caf50;
            font-weight: bold;
        }
        .status-failure {
            color: #f44336;
            font-weight: bold;
        }
        .status-warning {
            color: #ff9800;
            font-weight: bold;
        }

        /* Enhanced attack technique cards */
        .technique-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .technique-name {
            font-size: 1.2rem;
            font-weight: bold;
            color: #333333;
        }
        .technique-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
        .status-successful {
            background-color: #ffebee;
            color: #d32f2f;
        }
        .status-failed {
            background-color: #e8f5e9;
            color: #388e3c;
        }
        .status-detected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        .status-undetected {
            background-color: #fff3e0;
            color: #e64a19;
        }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<h1 class="main-header">HYDRA Advanced Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">AI-based Red-Blue simulation platform for automated penetration testing and self-defense</p>', unsafe_allow_html=True)

    # Load simulation results
    simulation_results = load_simulation_results()

    if not simulation_results:
        st.warning("No simulation results found. Please run a simulation first.")
        return

    # Sidebar for simulation selection
    st.sidebar.title("Simulation Control")

    selected_sim_index = st.sidebar.selectbox(
        "Select Simulation",
        range(len(simulation_results)),
        format_func=lambda i: f"Simulation {simulation_results[i].get('timestamp', 'Unknown')}"
    )

    selected_simulation = simulation_results[selected_sim_index]

    # Display simulation configuration
    st.sidebar.subheader("Configuration")
    config = selected_simulation.get('config', {})
    st.sidebar.write(f"Network Size: {config.get('network_size', 'Unknown')}")
    st.sidebar.write(f"Network Complexity: {config.get('network_complexity', 'Unknown')}")
    st.sidebar.write(f"Steps: {config.get('num_steps', 'Unknown')}")
    st.sidebar.write(f"Red Skill Level: {config.get('red_skill_level', 'Unknown')}")

    # Load network snapshots for this simulation
    timestamp = selected_simulation.get('timestamp', '')
    network_snapshots = load_network_snapshots(timestamp)

    if network_snapshots:
        snapshot_steps = [snapshot.get('step', 0) for snapshot in network_snapshots]
        selected_step = st.sidebar.selectbox(
            "Select Network Snapshot",
            range(len(snapshot_steps)),
            format_func=lambda i: f"Step {snapshot_steps[i]}" if snapshot_steps[i] < 9999 else "Final"
        )
        selected_snapshot = network_snapshots[selected_step]
    else:
        st.warning("No network snapshots found for this simulation.")
        selected_snapshot = None

    # Extract additional data
    credential_theft_attempts = extract_credential_theft_attempts(selected_simulation)
    lolbin_techniques = extract_lolbin_techniques(selected_simulation)
    attack_paths = extract_attack_paths(selected_simulation)
    data_theft_info = extract_data_theft(selected_simulation)
    mitre_mapping = create_mitre_attack_mapping()

    # Main dashboard content
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Attack Techniques", "MITRE ATT&CK", "Detailed Logs"])

    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            # Network visualization with attack paths
            st.markdown('<h2 class="sub-header">Network Visualization with Attack Paths</h2>', unsafe_allow_html=True)
            if selected_snapshot:
                network_fig = visualize_network(selected_snapshot, attack_paths)
                st.plotly_chart(network_fig, use_container_width=True)

            # Timeline visualization
            st.markdown('<h2 class="sub-header">Attack & Defense Timeline</h2>', unsafe_allow_html=True)
            timeline_fig = create_attack_defense_timeline(selected_simulation)
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True)
            else:
                st.info("No timeline data available.")

        with col2:
            # Summary metrics with enhanced visual impact
            st.markdown('<h2 class="sub-header">Simulation Results</h2>', unsafe_allow_html=True)

            summary = selected_simulation.get('summary', {})

            # Overall assessment
            red_success = summary.get('red_success_rate', 0)
            blue_success = summary.get('blue_success_rate', 0)

            if red_success > blue_success:
                st.markdown(f"""
                <div class="overall-result-card attack-success">
                    <h3>🚨 NETWORK COMPROMISED 🚨</h3>
                    <p>The red team successfully penetrated the network defenses with a {red_success:.1%} success rate.</p>
                    <p>Critical vulnerabilities were exploited, leading to significant security breaches.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="overall-result-card defense-success">
                    <h3>✅ NETWORK DEFENDED ✅</h3>
                    <p>The blue team successfully defended the network with a {blue_success:.1%} success rate.</p>
                    <p>Security measures effectively prevented or mitigated potential attacks.</p>
                </div>
                """, unsafe_allow_html=True)

            # Detailed metrics
            col_a, col_b = st.columns(2)
            with col_a:
                total_compromised = summary.get('total_compromised', 0)
                st.markdown(f"""
                <div class="card {'alert-card' if total_compromised > 0 else 'metric-card'}">
                    <h3>Compromised Nodes</h3>
                    <h2 class="highlight">{total_compromised}</h2>
                    <p class="info-text">{'⚠️ Security breach detected' if total_compromised > 0 else '✅ No nodes compromised'}</p>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                total_patched = summary.get('total_patched', 0)
                st.markdown(f"""
                <div class="card {'success-card' if total_patched > 0 else 'metric-card'}">
                    <h3>Patched Nodes</h3>
                    <h2 class="highlight">{total_patched}</h2>
                    <p class="info-text">{'✅ Vulnerabilities remediated' if total_patched > 0 else '⚠️ No patches applied'}</p>
                </div>
                """, unsafe_allow_html=True)

            col_c, col_d = st.columns(2)
            with col_c:
                st.markdown(f"""
                <div class="card {'alert-card' if red_success > 0.5 else 'success-card'}">
                    <h3>Red Team Performance</h3>
                    <h2 class="highlight">{red_success:.1%}</h2>
                    <p class="info-text">{'⚠️ High attack success rate' if red_success > 0.5 else '✅ Low attack success rate'}</p>
                </div>
                """, unsafe_allow_html=True)

            with col_d:
                st.markdown(f"""
                <div class="card {'success-card' if blue_success > 0.5 else 'alert-card'}">
                    <h3>Blue Team Performance</h3>
                    <h2 class="highlight">{blue_success:.1%}</h2>
                    <p class="info-text">{'✅ Effective defense' if blue_success > 0.5 else '⚠️ Defense needs improvement'}</p>
                </div>
                """, unsafe_allow_html=True)

            # Campaign outcome
            campaign_status = selected_simulation.get('steps', [])[-1].get('campaign_status', {}) if selected_simulation.get('steps') else {}
            if campaign_status:
                goal = campaign_status.get('goal', 'Unknown')
                progress = campaign_status.get('progress', 0)

                if goal == 'data_theft':
                    goal_display = "Data Theft"
                    data_collected = campaign_status.get('data_collected', 0)

                    st.markdown(f"""
                    <div class="card {'alert-card' if progress > 0.5 else 'success-card'}">
                        <h3>Data Theft Campaign</h3>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {progress*100}%;"></div>
                        </div>
                        <p class="info-text">{'⚠️ Critical data compromised' if progress > 0.5 else '✅ Most data protected'}</p>
                        <p class="info-text">Data sources compromised: {data_collected}</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif goal == 'credential_theft':
                    goal_display = "Credential Theft"
                    creds_stolen = campaign_status.get('credentials_stolen', 0)

                    st.markdown(f"""
                    <div class="card {'alert-card' if progress > 0.5 else 'success-card'}">
                        <h3>Credential Theft Campaign</h3>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {progress*100}%;"></div>
                        </div>
                        <p class="info-text">{'⚠️ Credentials compromised' if progress > 0.5 else '✅ Most credentials protected'}</p>
                        <p class="info-text">Credentials stolen: {creds_stolen}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="card {'alert-card' if progress > 0.5 else 'success-card'}">
                        <h3>{goal.replace('_', ' ').title()} Campaign</h3>
                        <div class="progress-container">
                            <div class="progress-bar" style="width: {progress*100}%;"></div>
                        </div>
                        <p class="info-text">Campaign progress: {progress*100:.1f}%</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Compromise vs Patched chart
            st.markdown('<h2 class="sub-header">Security Posture Over Time</h2>', unsafe_allow_html=True)
            posture_fig = create_compromise_patch_chart(selected_simulation)
            st.plotly_chart(posture_fig, use_container_width=True)

    with tab2:
        st.markdown('<h2 class="sub-header">Advanced Attack Techniques</h2>', unsafe_allow_html=True)

        # Attack paths visualization with enhanced clarity
        st.markdown('<h3>Attack Paths</h3>', unsafe_allow_html=True)
        if attack_paths:
            # Summary of attack paths
            total_paths = len(attack_paths)
            longest_path = max([len(path) for path in attack_paths])

            # Create a summary card
            st.markdown(f"""
            <div class="overall-result-card attack-success">
                <h3>🔍 ATTACK PATHS IDENTIFIED 🔍</h3>
                <p>HYDRA identified {total_paths} distinct attack path{'s' if total_paths > 1 else ''} through your network.</p>
                <p>The longest attack path consisted of {longest_path} steps, demonstrating how attackers can chain multiple techniques.</p>
            </div>
            """, unsafe_allow_html=True)

            # Display each attack path with enhanced visualization
            for i, path in enumerate(attack_paths):
                # Create a more descriptive title based on the path
                first_node = path[0].get('source') if path else "Unknown"
                last_node = path[-1].get('target') if path else "Unknown"

                path_html = f"""
                <div class="attack-path-card">
                    <div class="technique-header">
                        <div class="technique-name">Attack Path #{i+1}: Node {first_node} → Node {last_node}</div>
                        <div class="technique-status status-successful">{len(path)} STEPS</div>
                    </div>

                    <p style="color: #333333; margin-bottom: 15px;">
                        This attack path shows how an attacker can move from Node {first_node} to Node {last_node},
                        potentially gaining access to sensitive data or critical systems.
                    </p>

                    <div style="background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                        <h4 style="color: #333333; margin-bottom: 10px;">Step-by-Step Attack Progression</h4>
                        <ol style="color: #333333;">
                """

                for j, step in enumerate(path):
                    source = step.get('source')
                    target = step.get('target')
                    technique = step.get('technique')
                    timestamp = step.get('timestamp')

                    # Add more context based on the technique
                    technique_description = ""
                    if 'exploit' in technique.lower():
                        technique_description = "Exploited a vulnerability to gain initial access"
                    elif 'lateral' in technique.lower():
                        technique_description = "Moved laterally to expand access within the network"
                    elif 'privilege' in technique.lower():
                        technique_description = "Escalated privileges to gain higher-level access"
                    elif 'credential' in technique.lower():
                        technique_description = "Stole credentials to authenticate as a legitimate user"
                    elif 'data' in technique.lower():
                        technique_description = "Accessed and exfiltrated sensitive data"
                    else:
                        technique_description = "Used attack technique to compromise the target"

                    path_html += f"""
                    <li style="color: #333333; margin-bottom: 10px;">
                        <strong>Step {j+1}:</strong> Node {source} → Node {target}
                        <div style="margin-left: 20px; margin-top: 5px;">
                            <div><strong>Technique:</strong> {technique}</div>
                            <div><strong>Description:</strong> {technique_description}</div>
                            <div><strong>Timestamp:</strong> {timestamp}</div>
                        </div>
                    </li>
                    """

                path_html += """
                        </ol>
                    </div>

                    <div style="margin-top: 15px;">
                        <strong>Recommendation:</strong> Implement network segmentation and least privilege access controls to break this attack path and prevent lateral movement.
                    </div>
                </div>
                """
                st.markdown(path_html, unsafe_allow_html=True)
        else:
            st.info("No attack paths detected in this simulation.")

        # Credential theft section with enhanced visualization
        st.markdown('<h3>Credential Theft Techniques</h3>', unsafe_allow_html=True)
        if credential_theft_attempts:
            # Summary of credential theft
            successful_attempts = sum(1 for attempt in credential_theft_attempts if attempt.get('success', False))
            total_attempts = len(credential_theft_attempts)

            # Create a summary card
            st.markdown(f"""
            <div class="overall-result-card {'attack-success' if successful_attempts > 0 else 'defense-success'}">
                <h3>{'🔑 CREDENTIALS COMPROMISED 🔑' if successful_attempts > 0 else '🔒 CREDENTIALS PROTECTED 🔒'}</h3>
                <p>{'Attackers successfully stole credentials from ' + str(successful_attempts) + ' node(s).' if successful_attempts > 0 else 'All credential theft attempts were blocked.'}</p>
                <p>Success rate: {successful_attempts}/{total_attempts} attempts ({successful_attempts/total_attempts*100:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)

            # Display each credential theft attempt with enhanced visualization
            for attempt in credential_theft_attempts:
                success = attempt.get('success', False)
                detected = attempt.get('detected', False)

                # Determine status classes
                success_class = "status-successful" if success else "status-failed"
                detection_class = "status-undetected" if success and not detected else "status-detected"

                st.markdown(f"""
                <div class="credential-theft-card">
                    <div class="technique-header">
                        <div class="technique-name">Credential Theft on Node {attempt.get('node_id')}</div>
                        <div class="technique-status {success_class}">{'SUCCESSFUL' if success else 'FAILED'}</div>
                    </div>

                    <div class="credential-details">
                        <div class="credential-item">
                            <strong>Technique:</strong> {attempt.get('technique')}
                        </div>
                        <div class="credential-item">
                            <strong>Detection Status:</strong> <span class="{detection_class}">{('UNDETECTED' if success else 'DETECTED') if not detected else 'DETECTED'}</span>
                        </div>
                        <div class="credential-item">
                            <strong>Timestamp:</strong> {attempt.get('timestamp')}
                        </div>
                        <div class="credential-item">
                            <strong>Impact:</strong> {
                                'Critical - Attacker gained access to credentials that can be used for further attacks.' if success else
                                'None - The credential theft attempt was blocked.'
                            }
                        </div>
                    </div>

                    <div style="margin-top: 15px;">
                        <strong>Recommendation:</strong> {
                            'Implement multi-factor authentication and credential guard to prevent this type of attack.' if success else
                            'Continue monitoring for similar attacks and maintain current security controls.'
                        }
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No credential theft attempts detected in this simulation.")

        # Living-off-the-land section with enhanced visualization
        st.markdown('<h3>Living-Off-The-Land Techniques</h3>', unsafe_allow_html=True)
        if lolbin_techniques:
            # Summary of LOLBin techniques
            successful_techniques = sum(1 for technique in lolbin_techniques if technique.get('success', False))
            total_techniques = len(lolbin_techniques)

            # Create a summary card
            st.markdown(f"""
            <div class="overall-result-card {'attack-success' if successful_techniques > 0 else 'defense-success'}">
                <h3>{'⚠️ SYSTEM TOOLS ABUSED ⚠️' if successful_techniques > 0 else '✅ SYSTEM TOOLS PROTECTED ✅'}</h3>
                <p>{'Attackers successfully used legitimate system tools for malicious purposes on ' + str(successful_techniques) + ' node(s).' if successful_techniques > 0 else 'All attempts to abuse system tools were blocked.'}</p>
                <p>Success rate: {successful_techniques}/{total_techniques} attempts ({successful_techniques/total_techniques*100:.1f}%)</p>
            </div>
            """, unsafe_allow_html=True)

            # Group techniques by purpose
            techniques_by_purpose = {}
            for technique in lolbin_techniques:
                purpose = technique.get('purpose', 'Unknown')
                if purpose not in techniques_by_purpose:
                    techniques_by_purpose[purpose] = []
                techniques_by_purpose[purpose].append(technique)

            # Display techniques grouped by purpose
            for purpose, techniques in techniques_by_purpose.items():
                st.markdown(f"<h4>Purpose: {purpose.replace('_', ' ').title()}</h4>", unsafe_allow_html=True)

                for technique in techniques:
                    success = technique.get('success', False)
                    detected = technique.get('detected', False)

                    # Determine status classes
                    success_class = "status-successful" if success else "status-failed"
                    detection_class = "status-undetected" if success and not detected else "status-detected"

                    # Get a description based on the technique
                    technique_name = technique.get('technique', '').lower()
                    description = ""
                    if 'powershell' in technique_name:
                        description = "PowerShell was used to execute commands with potentially elevated privileges, bypassing security controls."
                    elif 'wmic' in technique_name:
                        description = "Windows Management Instrumentation Command-line was used to gather system information or execute commands."
                    elif 'certutil' in technique_name:
                        description = "Certificate utility was abused to download files from the internet, bypassing download restrictions."
                    elif 'regsvr32' in technique_name:
                        description = "Regsvr32 was used to execute arbitrary code, bypassing application whitelisting."
                    elif 'mshta' in technique_name:
                        description = "Microsoft HTML Application host was used to execute arbitrary code, bypassing security controls."
                    else:
                        description = f"The {technique_name} tool was used for malicious purposes, potentially bypassing security controls."

                    st.markdown(f"""
                    <div class="lolbin-card">
                        <div class="technique-header">
                            <div class="technique-name">LOLBin: {technique.get('technique')} on Node {technique.get('node_id')}</div>
                            <div class="technique-status {success_class}">{'SUCCESSFUL' if success else 'FAILED'}</div>
                        </div>

                        <p style="color: #333333; margin-bottom: 15px;">{description}</p>

                        <div class="credential-details">
                            <div class="credential-item">
                                <strong>Detection Status:</strong> <span class="{detection_class}">{('UNDETECTED' if success else 'DETECTED') if not detected else 'DETECTED'}</span>
                            </div>
                            <div class="credential-item">
                                <strong>Timestamp:</strong> {technique.get('timestamp')}
                            </div>
                            <div class="credential-item">
                                <strong>Impact:</strong> {
                                    'High - Attacker used legitimate system tools to evade detection and maintain persistence.' if success else
                                    'None - The attempt to abuse system tools was blocked.'
                                }
                            </div>
                        </div>

                        <div style="margin-top: 15px;">
                            <strong>Recommendation:</strong> {
                                'Implement application control policies and monitor for suspicious use of system utilities.' if success else
                                'Continue monitoring for similar attacks and maintain current security controls.'
                            }
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No living-off-the-land techniques detected in this simulation.")

    with tab3:
        st.markdown('<h2 class="sub-header">MITRE ATT&CK Framework Mapping</h2>', unsafe_allow_html=True)

        # Create a mapping of techniques used in the simulation
        techniques_used = {}
        for step_data in selected_simulation.get('steps', []):
            red_action = step_data.get('red_action', {})
            if red_action and red_action.get('success', False):
                attack_type = red_action.get('attack_type', 'unknown')
                if attack_type not in techniques_used:
                    techniques_used[attack_type] = 0
                techniques_used[attack_type] += 1

        # Display MITRE ATT&CK matrix
        for tactic, techniques in mitre_mapping.items():
            st.markdown(f'<div class="mitre-tactic">{tactic}</div>', unsafe_allow_html=True)

            for technique_id, technique_name in techniques.items():
                # Check if this technique or something similar was used
                used = any(attack_type.lower() in technique_name.lower() or technique_name.lower() in attack_type.lower() for attack_type in techniques_used.keys())

                if used:
                    st.markdown(f'<span class="mitre-tag" style="background-color: #e74c3c;">{technique_id}</span> {technique_name}', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="mitre-tag">{technique_id}</span> {technique_name}', unsafe_allow_html=True)

    with tab4:
        st.markdown('<h2 class="sub-header">Detailed Logs</h2>', unsafe_allow_html=True)

        # Get logs from all steps
        all_logs = []
        for step_data in selected_simulation.get('steps', []):
            step = step_data.get('step', 0)

            # Red action log
            red_action = step_data.get('red_action', {})
            if red_action:
                all_logs.append({
                    'Step': step,
                    'Type': 'Attack',
                    'Message': f"{red_action.get('strategy', 'Unknown')} attack on node {red_action.get('target', 'Unknown')} - {'Success' if red_action.get('success', False) else 'Failed'}"
                })

            # Blue action logs
            for blue_action in step_data.get('blue_actions', []):
                action_type = blue_action.get('action', 'Unknown')
                node_id = blue_action.get('node_id', 'Unknown')
                success = blue_action.get('success', False)

                if action_type == 'patch':
                    vuln_type = blue_action.get('vulnerability_type', 'vulnerability')
                    message = f"Patched {vuln_type} on node {node_id} - {'Success' if success else 'Failed'}"
                elif action_type == 'investigate':
                    found = blue_action.get('found_compromise', False)
                    message = f"Investigated node {node_id} - {'Found compromise' if found else 'No compromise found'}"
                else:
                    message = f"{action_type} on node {node_id} - {'Success' if success else 'Failed'}"

                all_logs.append({
                    'Step': step,
                    'Type': 'Defense',
                    'Message': message
                })

        # Convert to DataFrame and display
        if all_logs:
            logs_df = pd.DataFrame(all_logs)
            st.dataframe(logs_df, use_container_width=True)
        else:
            st.info("No logs available.")

    # Footer
    st.markdown("""
    <div class="footer">
        <p>HYDRA Advanced Dashboard | © 2025 | Version 2.0</p>
    </div>
    """, unsafe_allow_html=True)