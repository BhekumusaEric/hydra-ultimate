"""
HYDRA Dashboard - Streamlit Entry Point
This file serves as the entry point for the Streamlit Cloud deployment.
"""

import os
import sys
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

# Import functions with error handling
try:
    from dashboard.enhanced_dashboard import (
        load_simulation_results,
        load_network_snapshots,
        extract_credential_theft_attempts,
        extract_lolbin_techniques,
        extract_attack_paths,
        extract_data_theft,
        create_mitre_attack_mapping,
        create_attack_defense_timeline,
        create_compromise_patch_chart,
        visualize_network
    )
except ImportError as e:
    st.error(f"Error importing dashboard modules: {e}")
    st.info("Attempting to define necessary functions directly...")

    # Define the visualize_network function directly
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

# Run the main function
if __name__ == "__main__":
    try:
        from dashboard.enhanced_dashboard import main
        main()
    except ImportError as e:
        st.error(f"Error importing main function: {e}")
        st.info("Loading demo dashboard...")

        # Display a simple demo dashboard
        st.markdown('<h1 class="main-header">HYDRA Advanced Dashboard</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center;">AI-based Red-Blue simulation platform for automated penetration testing and self-defense</p>', unsafe_allow_html=True)

        st.warning("This is a demo version of the HYDRA dashboard. For the full version, please ensure all dependencies are installed correctly.")

        # Create tabs
        tab1, tab2 = st.tabs(["Overview", "About HYDRA"])

        with tab1:
            st.markdown('<h2 class="sub-header">Network Visualization</h2>', unsafe_allow_html=True)
            st.image("https://via.placeholder.com/800x400?text=Network+Visualization", use_column_width=True)

            st.markdown('<h2 class="sub-header">Security Metrics</h2>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Compromised Nodes", "5", "+2")
            with col2:
                st.metric("Patched Nodes", "12", "+8")

        with tab2:
            st.markdown("""
            # About HYDRA

            HYDRA is a groundbreaking cybersecurity platform that leverages artificial intelligence to simulate sophisticated cyber attacks and autonomous defense responses. By creating a digital twin of your network infrastructure, HYDRA enables organizations to:

            - **Identify vulnerabilities** before real attackers do
            - **Test defense mechanisms** against advanced persistent threats
            - **Train security teams** in realistic scenarios
            - **Optimize security investments** based on quantifiable risk metrics
            - **Continuously improve** security posture through machine learning
            """)

            st.markdown("### Key Features")
            st.markdown("""
            - **Advanced Red Team Simulation**
            - **Intelligent Blue Team Response**
            - **Enterprise-Grade Environment Simulation**
            - **Advanced Analytics & Visualization**
            """)

        # Footer
        st.markdown("""
        <div class="footer">
            <p>HYDRA Advanced Dashboard | © 2025 | Version 2.0</p>
        </div>
        """, unsafe_allow_html=True)
