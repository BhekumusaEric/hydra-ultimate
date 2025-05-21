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

# Import all functions from dashboard/enhanced_dashboard.py
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

# Run the main function
if __name__ == "__main__":
    from dashboard.enhanced_dashboard import main
    main()
