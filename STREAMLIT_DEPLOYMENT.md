# HYDRA Dashboard - Streamlit Cloud Deployment

This document provides instructions for deploying the HYDRA dashboard to Streamlit Cloud.

## Deployment Steps

1. **Fork or clone this repository**
   - Create your own copy of this repository on GitHub

2. **Sign up for Streamlit Cloud**
   - Go to [Streamlit Cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account

3. **Deploy your app**
   - Click on "New app" button
   - Select your repository from the list
   - Set the main file path to "streamlit_app.py"
   - Choose the branch (usually "master" or "main")
   - Click "Deploy"

4. **Wait for deployment**
   - Streamlit Cloud will build and deploy your app
   - Once deployed, you'll receive a URL for your dashboard

## Configuration

The dashboard is configured using the following files:

- **streamlit_app.py**: Main entry point for the Streamlit app
- **.streamlit/config.toml**: Configuration file for Streamlit
- **streamlit_requirements.txt**: Dependencies required for the dashboard

## Sample Data

The repository includes sample data in the `sample_data` directory:

- **sample_data/results/**: Sample simulation results
- **sample_data/network_snapshots/**: Sample network snapshots

## Features

The HYDRA dashboard includes the following features:

- **Network Visualization**: Interactive visualization of network topology
- **Attack Path Visualization**: Visual representation of attack paths
- **Credential Theft Visualization**: Detailed information about credential theft techniques
- **Living-Off-The-Land Techniques**: Visualization of LOLBin techniques
- **MITRE ATT&CK Mapping**: Mapping of attack techniques to the MITRE ATT&CK framework
- **Detailed Logs**: Comprehensive logs of all activities

## Troubleshooting

If you encounter any issues during deployment:

1. Check the Streamlit Cloud logs for error messages
2. Ensure all dependencies are listed in streamlit_requirements.txt
3. Verify that the main file path is set to "streamlit_app.py"
4. Check that the sample data files are properly formatted
