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
</style>
""", unsafe_allow_html=True)

def load_simulation_results():
    """Load all simulation results files"""
    result_files = glob.glob("results/simulation_results_*.json")
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

def visualize_network(network_data):
    """Visualize network graph using Plotly"""
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
    
    return fig

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
    
    # Main dashboard content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Network visualization
        if selected_snapshot:
            st.markdown('<h2 class="sub-header">Network Visualization</h2>', unsafe_allow_html=True)
            network_fig = visualize_network(selected_snapshot)
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
                    elif alert_type == 'attempt':
                        icon = "🟠"
                        severity = "Medium"
                    else:
                        icon = "🟡"
                        severity = "Low"
                    
                    st.markdown(f"""
                    <div class="card alert-card">
                        <h4>{icon} {alert_type.title()} Alert - {severity} Severity</h4>
                        <p>Node: {alert.get('node_id', 'Unknown')}</p>
                        <p>Attack: {alert.get('attack_type', 'Unknown')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent alerts.")
    
    # Logs section
    st.markdown('<h2 class="sub-header">Simulation Logs</h2>', unsafe_allow_html=True)
    
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

if __name__ == "__main__":
    main()
