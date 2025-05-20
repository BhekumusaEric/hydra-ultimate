"""
HYDRA Dashboard - Streamlit Entry Point
This file serves as the entry point for the Streamlit Cloud deployment.
"""

import os
import sys

# Add the current directory to the path so we can import from dashboard
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the enhanced_dashboard.py
from dashboard.enhanced_dashboard import main

# Run the main function
if __name__ == "__main__":
    main()
