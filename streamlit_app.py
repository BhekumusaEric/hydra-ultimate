"""
HYDRA Dashboard - Streamlit Entry Point
This file serves as the entry point for the Streamlit Cloud deployment.
"""

import streamlit as st

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

# Try to import from minimal_dashboard.py first (for Streamlit Cloud)
try:
    from dashboard.minimal_dashboard import main

    # Run the main function
    if __name__ == "__main__":
        main()

# If minimal_dashboard.py is not available, try enhanced_dashboard.py
except ImportError as e:
    st.warning(f"Could not import from minimal_dashboard.py: {e}")
    st.info("Trying to import from enhanced_dashboard.py...")

    try:
        from dashboard.enhanced_dashboard import main

        # Run the main function
        if __name__ == "__main__":
            main()

    # If both imports fail, display a fallback dashboard
    except ImportError as e:
        st.error(f"Error importing dashboard modules: {e}")
        st.info("Loading fallback dashboard...")

        # Display a simple fallback dashboard
        st.markdown('<h1 class="main-header">HYDRA Advanced Dashboard</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center;">AI-based Red-Blue simulation platform for automated penetration testing and self-defense</p>', unsafe_allow_html=True)

        st.warning("This is a fallback version of the HYDRA dashboard. For the full version, please ensure all dependencies are installed correctly.")

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
