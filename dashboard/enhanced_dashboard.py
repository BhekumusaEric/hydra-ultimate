import os
import json
import glob
import pandas as pd
import networkx as nx
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import re

# Define the visualize_network function
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
    edge_color = []
    edge_width = []
    edge_text = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        # Default edge style
        edge_color.extend(['#888', '#888', '#888'])
        edge_width.extend([0.5, 0.5, 0.5])
        edge_text.extend(['', '', ''])

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

# Set page configuration
st.set_page_config(
    page_title="HYDRA Advanced Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
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
        color: #666;
    }
    .highlight {
        color: #0066cc;
        font-weight: bold;
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
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .lolbin-card {
        background-color: #fffaf0;
        border-left: 5px solid #f39c12;
        padding: 1rem;
        margin-bottom: 1rem;
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
        color: #333333; /* Dark text for better visibility */
    }
    .attack-path-card {
        background-color: #f0f7ff;
        border-left: 5px solid #3498db;
        padding: 1rem;
        margin-bottom: 1rem;
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
        padding: 1rem;
        margin-bottom: 1rem;
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
</style>
""", unsafe_allow_html=True)

def load_simulation_results():
    """Load all simulation results files"""
    result_files = glob.glob("results/simulation_results_*.json") + glob.glob("results/enhanced_simulation_results_*.json")
    results = []

    for file_path in result_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Extract timestamp from filename
                timestamp = file_path.split('_')[-1].replace('.json', '')
                data['timestamp'] = timestamp
                results.append(data)
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")

    return sorted(results, key=lambda x: x.get('timestamp', ''), reverse=True)

def load_network_snapshots(timestamp=None):
    """Load network snapshots"""
    if timestamp:
        snapshot_files = glob.glob(f"network_snapshots/network_*_{timestamp}.json")
    else:
        snapshot_files = glob.glob("network_snapshots/network_*.json")

    snapshots = []
    for file_path in snapshot_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Extract step and timestamp from filename
                parts = file_path.split('_')
                if 'step' in file_path:
                    step = int(parts[parts.index('step') + 1])
                    data['step'] = step
                else:
                    if 'initial' in file_path:
                        data['step'] = 0
                    elif 'final' in file_path:
                        data['step'] = 9999  # High number to sort at the end

                snapshots.append(data)
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")

    return sorted(snapshots, key=lambda x: x.get('step', 0))

def extract_credential_theft_attempts(simulation_data):
    """Extract credential theft attempts from simulation data"""
    credential_theft_attempts = []

    for step_data in simulation_data.get('steps', []):
        step = step_data.get('step', 0)

        # Check alerts for credential theft
        for alert in step_data.get('alerts', []):
            if alert.get('type') == 'credential_theft':
                credential_theft_attempts.append({
                    'step': step,
                    'node_id': alert.get('node_id', 'Unknown'),
                    'technique': alert.get('technique', 'Unknown'),
                    'timestamp': alert.get('timestamp', 'Unknown'),
                    'detected': True
                })

        # Check red actions for credential theft
        red_action = step_data.get('red_action', {})
        if 'credential' in red_action.get('attack_type', '').lower():
            if not any(a.get('step') == step and a.get('node_id') == red_action.get('target') for a in credential_theft_attempts):
                credential_theft_attempts.append({
                    'step': step,
                    'node_id': red_action.get('target', 'Unknown'),
                    'technique': red_action.get('attack_type', 'Unknown'),
                    'timestamp': red_action.get('timestamp', 'Unknown'),
                    'detected': red_action.get('detected', False),
                    'success': red_action.get('success', False)
                })

    return credential_theft_attempts

def extract_lolbin_techniques(simulation_data):
    """Extract living-off-the-land techniques from simulation data"""
    lolbin_techniques = []

    for step_data in simulation_data.get('steps', []):
        step = step_data.get('step', 0)

        # Check alerts for lolbin execution
        for alert in step_data.get('alerts', []):
            if alert.get('type') == 'lolbin_execution':
                lolbin_techniques.append({
                    'step': step,
                    'node_id': alert.get('node_id', 'Unknown'),
                    'technique': alert.get('technique', 'Unknown'),
                    'purpose': alert.get('purpose', 'Unknown'),
                    'timestamp': alert.get('timestamp', 'Unknown'),
                    'detected': True
                })

        # Check red actions for lolbin techniques
        red_action = step_data.get('red_action', {})
        if 'lolbin' in red_action.get('attack_type', '').lower() or 'living_off_the_land' in red_action.get('attack_type', '').lower():
            if not any(a.get('step') == step and a.get('node_id') == red_action.get('target') for a in lolbin_techniques):
                lolbin_techniques.append({
                    'step': step,
                    'node_id': red_action.get('target', 'Unknown'),
                    'technique': red_action.get('attack_type', 'Unknown'),
                    'timestamp': red_action.get('timestamp', 'Unknown'),
                    'detected': red_action.get('detected', False),
                    'success': red_action.get('success', False)
                })

    return lolbin_techniques

def extract_attack_paths(simulation_data):
    """Extract attack paths from simulation data"""
    attack_paths = []
    current_path = []
    current_node = None

    for step_data in simulation_data.get('steps', []):
        red_action = step_data.get('red_action', {})
        if not red_action:
            continue

        # Track attack paths
        if red_action.get('success', False):
            target = red_action.get('target', None)
            if target != current_node:
                if current_node is not None:
                    current_path.append({
                        'source': current_node,
                        'target': target,
                        'technique': red_action.get('attack_type', 'unknown'),
                        'timestamp': red_action.get('timestamp', '')
                    })
                current_node = target

        # If this is a new path or the end of a path
        if (not red_action.get('success', False) and current_path) or (len(current_path) > 0 and step_data.get('step') == simulation_data.get('config', {}).get('num_steps')):
            if len(current_path) > 0:
                attack_paths.append(current_path)
                current_path = []
                current_node = None

    return attack_paths

def extract_data_theft(simulation_data):
    """Extract data theft information from simulation data"""
    data_theft_info = []

    for step_data in simulation_data.get('steps', []):
        campaign_status = step_data.get('campaign_status', {})
        if campaign_status.get('goal') == 'data_theft' and campaign_status.get('data_collected', 0) > 0:
            data_theft_info.append({
                'step': step_data.get('step', 0),
                'data_collected': campaign_status.get('data_collected', 0),
                'progress': campaign_status.get('progress', 0),
                'compromised_nodes': campaign_status.get('compromised_nodes', 0)
            })

    return data_theft_info

def create_mitre_attack_mapping():
    """Create a mapping of MITRE ATT&CK techniques"""
    mitre_mapping = {
        "Initial Access": {
            "T1190": "Exploit Public-Facing Application",
            "T1133": "External Remote Services",
            "T1078": "Valid Accounts"
        },
        "Execution": {
            "T1059": "Command and Scripting Interpreter",
            "T1053": "Scheduled Task/Job",
            "T1569": "System Services",
            "T1203": "Exploitation for Client Execution",
            "T1559": "Inter-Process Communication"
        },
        "Persistence": {
            "T1547": "Boot or Logon Autostart Execution",
            "T1136": "Create Account",
            "T1505": "Server Software Component",
            "T1546": "Event Triggered Execution",
            "T1133": "External Remote Services"
        },
        "Privilege Escalation": {
            "T1548": "Abuse Elevation Control Mechanism",
            "T1134": "Access Token Manipulation",
            "T1068": "Exploitation for Privilege Escalation",
            "T1574": "Hijack Execution Flow"
        },
        "Defense Evasion": {
            "T1562": "Impair Defenses",
            "T1070": "Indicator Removal",
            "T1036": "Masquerading",
            "T1027": "Obfuscated Files or Information"
        },
        "Credential Access": {
            "T1110": "Brute Force",
            "T1555": "Credentials from Password Stores",
            "T1212": "Exploitation for Credential Access",
            "T1187": "Forced Authentication",
            "T1056": "Input Capture",
            "T1557": "Man-in-the-Middle",
            "T1003": "OS Credential Dumping",
            "T1528": "Steal Application Access Token",
            "T1558": "Steal or Forge Kerberos Tickets"
        },
        "Discovery": {
            "T1087": "Account Discovery",
            "T1010": "Application Window Discovery",
            "T1217": "Browser Information Discovery",
            "T1580": "Cloud Infrastructure Discovery",
            "T1538": "Cloud Service Dashboard"
        },
        "Lateral Movement": {
            "T1210": "Exploitation of Remote Services",
            "T1534": "Internal Spearphishing",
            "T1570": "Lateral Tool Transfer",
            "T1021": "Remote Services",
            "T1091": "Replication Through Removable Media"
        },
        "Collection": {
            "T1560": "Archive Collected Data",
            "T1123": "Audio Capture",
            "T1119": "Automated Collection",
            "T1115": "Clipboard Data",
            "T1530": "Data from Cloud Storage"
        },
        "Command and Control": {
            "T1071": "Application Layer Protocol",
            "T1092": "Communication Through Removable Media",
            "T1132": "Data Encoding",
            "T1001": "Data Obfuscation",
            "T1568": "Dynamic Resolution"
        },
        "Exfiltration": {
            "T1020": "Automated Exfiltration",
            "T1030": "Data Transfer Size Limits",
            "T1048": "Exfiltration Over Alternative Protocol",
            "T1041": "Exfiltration Over C2 Channel",
            "T1011": "Exfiltration Over Other Network Medium"
        },
        "Impact": {
            "T1485": "Data Destruction",
            "T1486": "Data Encrypted for Impact",
            "T1565": "Data Manipulation",
            "T1491": "Defacement",
            "T1499": "Endpoint Denial of Service"
        }
    }
    return mitre_mapping

def create_attack_defense_timeline(simulation_data):
    """Create a timeline of attacks and defenses"""
    events = []

    for step_data in simulation_data.get('steps', []):
        step = step_data.get('step', 0)

        # Add red team action
        red_action = step_data.get('red_action', {})
        if red_action:
            events.append({
                'Step': step,
                'Agent': 'Red',
                'Action': f"{red_action.get('strategy', 'Unknown')} attack",
                'Target': f"Node {red_action.get('target', 'Unknown')}",
                'Result': 'Success' if red_action.get('success', False) else 'Failed',
                'Type': red_action.get('attack_type', 'Unknown')
            })

        # Add blue team actions
        for blue_action in step_data.get('blue_actions', []):
            action_type = blue_action.get('action', 'Unknown')
            if action_type == 'patch':
                action_desc = f"Patch {blue_action.get('vulnerability_type', 'vulnerability')}"
            elif action_type == 'investigate':
                action_desc = 'Investigation'
            else:
                action_desc = action_type

            events.append({
                'Step': step,
                'Agent': 'Blue',
                'Action': action_desc,
                'Target': f"Node {blue_action.get('node_id', 'Unknown')}",
                'Result': 'Success' if blue_action.get('success', False) else 'Failed',
                'Type': blue_action.get('vulnerability_type', 'N/A')
            })

    # Convert to DataFrame
    df = pd.DataFrame(events)

    if df.empty:
        return None

    # Create figure
    fig = px.scatter(
        df,
        x='Step',
        y='Agent',
        color='Result',
        symbol='Action',
        hover_data=['Target', 'Type'],
        title='Attack and Defense Timeline',
        color_discrete_map={'Success': 'green', 'Failed': 'red'},
        height=400
    )

    fig.update_layout(
        xaxis_title='Simulation Step',
        yaxis_title='Agent',
        legend_title='Result'
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

def main():
    """Main dashboard application"""
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
            # Summary metrics
            st.markdown('<h2 class="sub-header">Simulation Summary</h2>', unsafe_allow_html=True)

            summary = selected_simulation.get('summary', {})

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="card metric-card">
                    <h3>Compromised</h3>
                    <h2 class="highlight">{summary.get('total_compromised', 'N/A')}</h2>
                    <p class="info-text">Total nodes compromised</p>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown(f"""
                <div class="card metric-card">
                    <h3>Patched</h3>
                    <h2 class="highlight">{summary.get('total_patched', 'N/A')}</h2>
                    <p class="info-text">Total nodes patched</p>
                </div>
                """, unsafe_allow_html=True)

            col_c, col_d = st.columns(2)
            with col_c:
                red_success = summary.get('red_success_rate', 0)
                st.markdown(f"""
                <div class="card {'alert-card' if red_success > 0.5 else 'success-card'}">
                    <h3>Red Team</h3>
                    <h2 class="highlight">{red_success:.1%}</h2>
                    <p class="info-text">Attack success rate</p>
                </div>
                """, unsafe_allow_html=True)

            with col_d:
                blue_success = summary.get('blue_success_rate', 0)
                st.markdown(f"""
                <div class="card {'success-card' if blue_success > 0.5 else 'alert-card'}">
                    <h3>Blue Team</h3>
                    <h2 class="highlight">{blue_success:.1%}</h2>
                    <p class="info-text">Defense success rate</p>
                </div>
                """, unsafe_allow_html=True)

            # Campaign goal and progress
            campaign_status = selected_simulation.get('steps', [])[-1].get('campaign_status', {}) if selected_simulation.get('steps') else {}
            if campaign_status:
                st.markdown(f"""
                <div class="card metric-card">
                    <h3>Campaign Goal</h3>
                    <h2 class="highlight">{campaign_status.get('goal', 'Unknown')}</h2>
                    <p class="info-text">Progress: {campaign_status.get('progress', 0)*100:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)

            # Compromise vs Patched chart
            st.markdown('<h2 class="sub-header">Security Posture Over Time</h2>', unsafe_allow_html=True)
            posture_fig = create_compromise_patch_chart(selected_simulation)
            st.plotly_chart(posture_fig, use_container_width=True)

            # Recent alerts
            st.markdown('<h2 class="sub-header">Recent Alerts</h2>', unsafe_allow_html=True)

            # Get alerts from the last step
            if selected_simulation.get('steps'):
                last_step = selected_simulation['steps'][-1]
                alerts = last_step.get('alerts', [])

                if alerts:
                    for alert in alerts:
                        alert_type = alert.get('type', 'Unknown')
                        if alert_type == 'compromise':
                            icon = "🔴"
                            severity = "High"
                        elif alert_type == 'credential_theft':
                            icon = "🟣"
                            severity = "High"
                        elif alert_type == 'lolbin_execution':
                            icon = "🟠"
                            severity = "Medium"
                        elif alert_type == 'attempt':
                            icon = "🟡"
                            severity = "Medium"
                        else:
                            icon = "🔵"
                            severity = "Low"

                        st.markdown(f"""
                        <div class="card alert-card">
                            <h4>{icon} {alert_type.title()} Alert - {severity} Severity</h4>
                            <p>Node: {alert.get('node_id', 'Unknown')}</p>
                            <p>Technique: {alert.get('technique', alert.get('attack_type', 'Unknown'))}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No recent alerts.")

    with tab2:
        st.markdown('<h2 class="sub-header">Advanced Attack Techniques</h2>', unsafe_allow_html=True)

        # Attack paths visualization
        st.markdown('<h3>Attack Paths</h3>', unsafe_allow_html=True)
        if attack_paths:
            for i, path in enumerate(attack_paths):
                path_html = f"""
                <div class="attack-path-card">
                    <h4 style="color: #333333;">Attack Path #{i+1} ({len(path)} steps)</h4>
                    <ol style="color: #333333;">
                """

                for step in path:
                    path_html += f"""
                    <li style="color: #333333;">
                        Node {step.get('source')} → Node {step.get('target')} using {step.get('technique')} ({step.get('timestamp')})
                    </li>
                    """

                path_html += """
                    </ol>
                </div>
                """
                st.markdown(path_html, unsafe_allow_html=True)
        else:
            st.info("No attack paths detected in this simulation.")

        # Credential theft section
        st.markdown('<h3>Credential Theft Techniques</h3>', unsafe_allow_html=True)
        if credential_theft_attempts:
            for attempt in credential_theft_attempts:
                success = attempt.get('success', False)
                detected = attempt.get('detected', False)

                st.markdown(f"""
                <div class="credential-theft-card">
                    <h4 style="color: #333333;">Credential Theft on Node {attempt.get('node_id')}</h4>
                    <p style="color: #333333;"><strong style="color: #333333;">Technique:</strong> {attempt.get('technique')}</p>
                    <p style="color: #333333;"><strong style="color: #333333;">Status:</strong> {'Successful' if success else 'Failed'} {'(Detected)' if detected else '(Undetected)'}</p>
                    <p style="color: #333333;"><strong style="color: #333333;">Timestamp:</strong> {attempt.get('timestamp')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No credential theft attempts detected in this simulation.")

        # Living-off-the-land section
        st.markdown('<h3>Living-Off-The-Land Techniques</h3>', unsafe_allow_html=True)
        if lolbin_techniques:
            for technique in lolbin_techniques:
                success = technique.get('success', False)
                detected = technique.get('detected', False)

                st.markdown(f"""
                <div class="lolbin-card">
                    <h4 style="color: #333333;">LOLBin Technique on Node {technique.get('node_id')}</h4>
                    <p style="color: #333333;"><strong style="color: #333333;">Technique:</strong> {technique.get('technique')}</p>
                    <p style="color: #333333;"><strong style="color: #333333;">Purpose:</strong> {technique.get('purpose', 'Unknown')}</p>
                    <p style="color: #333333;"><strong style="color: #333333;">Status:</strong> {'Successful' if success else 'Failed'} {'(Detected)' if detected else '(Undetected)'}</p>
                    <p style="color: #333333;"><strong style="color: #333333;">Timestamp:</strong> {technique.get('timestamp')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No living-off-the-land techniques detected in this simulation.")

        # Data theft section
        st.markdown('<h3>Data Theft Results</h3>', unsafe_allow_html=True)
        if data_theft_info:
            latest_theft = data_theft_info[-1]

            st.markdown(f"""
            <div class="data-theft-card">
                <h4 style="color: #333333;">Data Theft Summary</h4>
                <p style="color: #333333;"><strong style="color: #333333;">Data Sources Compromised:</strong> {latest_theft.get('data_collected')}</p>
                <p style="color: #333333;"><strong style="color: #333333;">Campaign Progress:</strong> {latest_theft.get('progress')*100:.1f}%</p>
                <p style="color: #333333;"><strong style="color: #333333;">Nodes Compromised:</strong> {latest_theft.get('compromised_nodes')}</p>
            </div>
            """, unsafe_allow_html=True)

            # Create a chart showing data theft progress
            steps = [info.get('step') for info in data_theft_info]
            progress = [info.get('progress')*100 for info in data_theft_info]
            data_collected = [info.get('data_collected') for info in data_theft_info]

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=steps,
                y=progress,
                mode='lines+markers',
                name='Campaign Progress (%)',
                line=dict(color='blue', width=2)
            ))

            fig.add_trace(go.Scatter(
                x=steps,
                y=data_collected,
                mode='lines+markers',
                name='Data Sources Compromised',
                line=dict(color='purple', width=2)
            ))

            fig.update_layout(
                title='Data Theft Progress Over Time',
                xaxis_title='Simulation Step',
                yaxis_title='Value',
                legend_title='Metric',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data theft detected in this simulation.")

        # Attack buttons section
        st.markdown('<h3>Launch Attacks</h3>', unsafe_allow_html=True)
        st.markdown('<p>Select a target node and attack technique to launch a simulated attack:</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            target_node = st.selectbox("Select Target Node", range(50))
        with col2:
            attack_technique = st.selectbox("Select Attack Technique", [
                "Privilege Escalation",
                "Credential Theft",
                "Living-Off-The-Land",
                "SQL Injection",
                "Cross-Site Scripting",
                "Remote Code Execution"
            ])

        if st.button("Launch Attack"):
            st.success(f"Simulated {attack_technique} attack launched against Node {target_node}. Check the logs for results.")

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

        # Display techniques used in the simulation
        st.markdown('<h3>Techniques Used in Simulation</h3>', unsafe_allow_html=True)

        if techniques_used:
            # Create a bar chart of techniques used
            techniques = list(techniques_used.keys())
            counts = list(techniques_used.values())

            fig = px.bar(
                x=techniques,
                y=counts,
                labels={'x': 'Attack Technique', 'y': 'Count'},
                title='Attack Techniques Used in Simulation',
                color=counts,
                color_continuous_scale='Reds'
            )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No successful attack techniques detected in this simulation.")

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

            # Alert logs
            for alert in step_data.get('alerts', []):
                alert_type = alert.get('type', 'Unknown')
                node_id = alert.get('node_id', 'Unknown')
                technique = alert.get('technique', alert.get('attack_type', 'Unknown'))

                all_logs.append({
                    'Step': step,
                    'Type': 'Alert',
                    'Message': f"{alert_type.title()} alert on node {node_id} - {technique}"
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

if __name__ == "__main__":
    main()
