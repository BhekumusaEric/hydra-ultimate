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

            # Compromise vs Patched chart
            st.markdown('<h2 class="sub-header">Security Posture Over Time</h2>', unsafe_allow_html=True)
            posture_fig = create_compromise_patch_chart(selected_simulation)
            st.plotly_chart(posture_fig, use_container_width=True)

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