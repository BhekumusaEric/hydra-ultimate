#!/usr/bin/env python3
"""
HYDRA ROI Calculator

This tool helps organizations calculate the return on investment (ROI) from implementing
HYDRA for security validation and improvement.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="HYDRA ROI Calculator",
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
    .info-box {
        background-color: #f0f2f6;
        border-left: 5px solid #0066cc;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .result-box {
        background-color: #f0fff0;
        border-left: 5px solid #00cc00;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .footnote {
        font-size: 0.8rem;
        color: #666;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">HYDRA ROI Calculator</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center;">Calculate the return on investment from implementing HYDRA for security validation and improvement</p>', unsafe_allow_html=True)

# Information box
st.markdown("""
<div class="info-box">
<p>This calculator helps you estimate the potential return on investment (ROI) from implementing HYDRA in your organization. 
The calculations are based on industry benchmarks and can be customized to your specific environment.</p>
<p>Adjust the parameters in the sidebar to match your organization's profile and see the projected ROI over time.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for inputs
st.sidebar.title("Organization Profile")

# Organization size
org_size = st.sidebar.selectbox(
    "Organization Size",
    ["Small (< 1,000 employees)", "Medium (1,000-5,000 employees)", "Large (5,000-15,000 employees)", "Enterprise (> 15,000 employees)"]
)

# Industry
industry = st.sidebar.selectbox(
    "Industry",
    ["Financial Services", "Healthcare", "Manufacturing", "Retail", "Technology", "Government", "Energy", "Other"]
)

# Infrastructure complexity
infrastructure_complexity = st.sidebar.select_slider(
    "Infrastructure Complexity",
    options=["Low", "Medium", "High", "Very High"],
    value="Medium"
)

# Security maturity
security_maturity = st.sidebar.select_slider(
    "Security Program Maturity",
    options=["Initial", "Developing", "Established", "Advanced", "Leading"],
    value="Established"
)

# Current security spending
annual_security_budget = st.sidebar.number_input(
    "Annual Security Budget (USD)",
    min_value=100000,
    max_value=50000000,
    value=1000000,
    step=100000,
    format="%d"
)

# Breach risk
st.sidebar.subheader("Risk Profile")

# Data breach cost
data_breach_cost_map = {
    "Financial Services": 5.85,
    "Healthcare": 10.93,
    "Manufacturing": 4.35,
    "Retail": 3.28,
    "Technology": 5.04,
    "Government": 9.44,
    "Energy": 4.72,
    "Other": 4.24
}

data_breach_cost_base = data_breach_cost_map.get(industry, 4.24)
data_breach_cost = st.sidebar.number_input(
    "Average Cost of Data Breach (USD Millions)",
    min_value=1.0,
    max_value=20.0,
    value=data_breach_cost_base,
    step=0.1,
    format="%.2f"
)

# Breach probability
breach_probability_map = {
    "Initial": 0.35,
    "Developing": 0.28,
    "Established": 0.20,
    "Advanced": 0.15,
    "Leading": 0.10
}

breach_probability_base = breach_probability_map.get(security_maturity, 0.20)
annual_breach_probability = st.sidebar.slider(
    "Annual Breach Probability (%)",
    min_value=5.0,
    max_value=50.0,
    value=breach_probability_base * 100,
    step=1.0,
    format="%.1f"
) / 100

# HYDRA implementation
st.sidebar.subheader("HYDRA Implementation")

# Implementation model
implementation_model = st.sidebar.selectbox(
    "Implementation Model",
    ["Basic", "Standard", "Enterprise", "Custom"]
)

# Implementation cost map
implementation_cost_map = {
    "Basic": {
        "Small (< 1,000 employees)": 50000,
        "Medium (1,000-5,000 employees)": 75000,
        "Large (5,000-15,000 employees)": 100000,
        "Enterprise (> 15,000 employees)": 150000
    },
    "Standard": {
        "Small (< 1,000 employees)": 100000,
        "Medium (1,000-5,000 employees)": 150000,
        "Large (5,000-15,000 employees)": 200000,
        "Enterprise (> 15,000 employees)": 300000
    },
    "Enterprise": {
        "Small (< 1,000 employees)": 200000,
        "Medium (1,000-5,000 employees)": 300000,
        "Large (5,000-15,000 employees)": 400000,
        "Enterprise (> 15,000 employees)": 600000
    },
    "Custom": {
        "Small (< 1,000 employees)": 150000,
        "Medium (1,000-5,000 employees)": 225000,
        "Large (5,000-15,000 employees)": 300000,
        "Enterprise (> 15,000 employees)": 450000
    }
}

# Get default implementation cost
default_implementation_cost = implementation_cost_map.get(implementation_model, {}).get(org_size, 150000)

# Implementation cost
implementation_cost = st.sidebar.number_input(
    "Implementation Cost (USD)",
    min_value=10000,
    max_value=1000000,
    value=default_implementation_cost,
    step=10000,
    format="%d"
)

# Annual subscription
annual_subscription_map = {
    "Basic": {
        "Small (< 1,000 employees)": 40000,
        "Medium (1,000-5,000 employees)": 60000,
        "Large (5,000-15,000 employees)": 80000,
        "Enterprise (> 15,000 employees)": 120000
    },
    "Standard": {
        "Small (< 1,000 employees)": 80000,
        "Medium (1,000-5,000 employees)": 120000,
        "Large (5,000-15,000 employees)": 160000,
        "Enterprise (> 15,000 employees)": 240000
    },
    "Enterprise": {
        "Small (< 1,000 employees)": 160000,
        "Medium (1,000-5,000 employees)": 240000,
        "Large (5,000-15,000 employees)": 320000,
        "Enterprise (> 15,000 employees)": 480000
    },
    "Custom": {
        "Small (< 1,000 employees)": 120000,
        "Medium (1,000-5,000 employees)": 180000,
        "Large (5,000-15,000 employees)": 240000,
        "Enterprise (> 15,000 employees)": 360000
    }
}

# Get default annual subscription
default_annual_subscription = annual_subscription_map.get(implementation_model, {}).get(org_size, 120000)

# Annual subscription
annual_subscription = st.sidebar.number_input(
    "Annual Subscription (USD)",
    min_value=10000,
    max_value=1000000,
    value=default_annual_subscription,
    step=10000,
    format="%d"
)

# Benefits
st.sidebar.subheader("Expected Benefits")

# Risk reduction
risk_reduction = st.sidebar.slider(
    "Breach Risk Reduction (%)",
    min_value=10,
    max_value=80,
    value=40,
    step=5
) / 100

# Security tool optimization
security_tool_optimization = st.sidebar.slider(
    "Security Tool Optimization (%)",
    min_value=5,
    max_value=40,
    value=15,
    step=5
) / 100

# Penetration testing reduction
pentest_reduction = st.sidebar.slider(
    "Penetration Testing Cost Reduction (%)",
    min_value=10,
    max_value=70,
    value=30,
    step=5
) / 100

# Security team efficiency
security_team_efficiency = st.sidebar.slider(
    "Security Team Efficiency Improvement (%)",
    min_value=10,
    max_value=50,
    value=25,
    step=5
) / 100

# Calculate ROI
st.markdown('<h2 class="sub-header">ROI Analysis</h2>', unsafe_allow_html=True)

# Time period
years = 3
quarters = years * 4

# Create time periods
periods = [f"Q{i%4+1} Y{i//4+1}" for i in range(quarters)]

# Calculate costs
implementation_costs = [implementation_cost] + [0] * (quarters - 1)
subscription_costs = [annual_subscription/4] * quarters

# Calculate benefits
# 1. Risk reduction benefit
annual_breach_cost = data_breach_cost * 1000000 * annual_breach_probability
quarterly_breach_cost = annual_breach_cost / 4
risk_reduction_benefit = [quarterly_breach_cost * risk_reduction * min(1, (i+1)/4) for i in range(quarters)]

# 2. Security tool optimization
quarterly_tool_spend = annual_security_budget * 0.4 / 4  # Assume 40% of security budget is on tools
tool_optimization_benefit = [quarterly_tool_spend * security_tool_optimization * min(1, (i+1)/4) for i in range(quarters)]

# 3. Penetration testing reduction
quarterly_pentest_spend = annual_security_budget * 0.15 / 4  # Assume 15% of security budget is on pentesting
pentest_reduction_benefit = [quarterly_pentest_spend * pentest_reduction * min(1, (i+1)/4) for i in range(quarters)]

# 4. Security team efficiency
quarterly_team_spend = annual_security_budget * 0.35 / 4  # Assume 35% of security budget is on personnel
efficiency_benefit = [quarterly_team_spend * security_team_efficiency * min(1, (i+1)/8) for i in range(quarters)]  # Slower realization

# Total benefits
total_benefits = [risk_reduction_benefit[i] + tool_optimization_benefit[i] + pentest_reduction_benefit[i] + efficiency_benefit[i] for i in range(quarters)]

# Total costs
total_costs = [implementation_costs[i] + subscription_costs[i] for i in range(quarters)]

# Net benefit
net_benefits = [total_benefits[i] - total_costs[i] for i in range(quarters)]

# Cumulative net benefit
cumulative_net_benefits = np.cumsum(net_benefits)

# ROI calculation
total_investment = sum(total_costs)
total_benefit = sum(total_benefits)
roi_percentage = ((total_benefit - total_investment) / total_investment) * 100
payback_period_quarters = next((i for i, x in enumerate(cumulative_net_benefits) if x > 0), quarters)
payback_period_years = payback_period_quarters / 4

# Create DataFrame for visualization
roi_data = pd.DataFrame({
    'Period': periods,
    'Implementation Cost': implementation_costs,
    'Subscription Cost': subscription_costs,
    'Risk Reduction Benefit': risk_reduction_benefit,
    'Tool Optimization Benefit': tool_optimization_benefit,
    'Pentest Reduction Benefit': pentest_reduction_benefit,
    'Efficiency Benefit': efficiency_benefit,
    'Total Benefit': total_benefits,
    'Total Cost': total_costs,
    'Net Benefit': net_benefits,
    'Cumulative Net Benefit': cumulative_net_benefits
})

# Display ROI metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total 3-Year ROI", f"{roi_percentage:.1f}%")

with col2:
    st.metric("Payback Period", f"{payback_period_years:.2f} years")

with col3:
    st.metric("3-Year Net Benefit", f"${(total_benefit - total_investment):,.0f}")

# Display ROI chart
st.subheader("ROI Over Time")

fig = go.Figure()

# Add costs as negative values
fig.add_trace(go.Bar(
    x=periods,
    y=[-cost for cost in implementation_costs],
    name='Implementation Cost',
    marker_color='#ff9999'
))

fig.add_trace(go.Bar(
    x=periods,
    y=[-cost for cost in subscription_costs],
    name='Subscription Cost',
    marker_color='#ffcc99'
))

# Add benefits
fig.add_trace(go.Bar(
    x=periods,
    y=risk_reduction_benefit,
    name='Risk Reduction',
    marker_color='#99ff99'
))

fig.add_trace(go.Bar(
    x=periods,
    y=tool_optimization_benefit,
    name='Tool Optimization',
    marker_color='#99ffcc'
))

fig.add_trace(go.Bar(
    x=periods,
    y=pentest_reduction_benefit,
    name='Pentest Reduction',
    marker_color='#99ccff'
))

fig.add_trace(go.Bar(
    x=periods,
    y=efficiency_benefit,
    name='Efficiency Improvement',
    marker_color='#cc99ff'
))

# Add cumulative line
fig.add_trace(go.Scatter(
    x=periods,
    y=cumulative_net_benefits,
    name='Cumulative Net Benefit',
    line=dict(color='#0066cc', width=3),
    mode='lines+markers'
))

# Update layout
fig.update_layout(
    barmode='relative',
    title='Quarterly Costs, Benefits, and Cumulative ROI',
    xaxis_title='Time Period',
    yaxis_title='Amount (USD)',
    legend_title='Category',
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# Display benefit breakdown
st.subheader("Benefit Breakdown")

# Calculate total benefits by category
total_risk_reduction = sum(risk_reduction_benefit)
total_tool_optimization = sum(tool_optimization_benefit)
total_pentest_reduction = sum(pentest_reduction_benefit)
total_efficiency = sum(efficiency_benefit)

# Create pie chart
benefit_labels = ['Risk Reduction', 'Tool Optimization', 'Pentest Reduction', 'Efficiency Improvement']
benefit_values = [total_risk_reduction, total_tool_optimization, total_pentest_reduction, total_efficiency]
benefit_colors = ['#99ff99', '#99ffcc', '#99ccff', '#cc99ff']

fig_pie = go.Figure(data=[go.Pie(
    labels=benefit_labels,
    values=benefit_values,
    hole=.4,
    marker_colors=benefit_colors
)])

fig_pie.update_layout(
    title='3-Year Benefit Distribution',
    height=500
)

st.plotly_chart(fig_pie, use_container_width=True)

# Detailed ROI table
st.subheader("Detailed ROI Analysis")
st.dataframe(roi_data.style.format({
    'Implementation Cost': '${:,.0f}',
    'Subscription Cost': '${:,.0f}',
    'Risk Reduction Benefit': '${:,.0f}',
    'Tool Optimization Benefit': '${:,.0f}',
    'Pentest Reduction Benefit': '${:,.0f}',
    'Efficiency Benefit': '${:,.0f}',
    'Total Benefit': '${:,.0f}',
    'Total Cost': '${:,.0f}',
    'Net Benefit': '${:,.0f}',
    'Cumulative Net Benefit': '${:,.0f}'
}))

# Assumptions and methodology
st.markdown('<h2 class="sub-header">Assumptions and Methodology</h2>', unsafe_allow_html=True)

st.markdown("""
This ROI calculator uses the following methodology and assumptions:

1. **Risk Reduction Benefit**: Calculated as the reduction in expected breach costs (probability × impact) due to improved security posture.

2. **Tool Optimization Benefit**: Savings from optimizing security tool investments based on HYDRA's findings.

3. **Penetration Testing Reduction**: Savings from reduced external penetration testing needs.

4. **Efficiency Benefit**: Value of improved security team productivity through better prioritization and automation.

5. **Implementation Timeline**:
   - Risk reduction benefits ramp up over the first year
   - Tool optimization and pentest reduction benefits realize within the first year
   - Efficiency benefits gradually increase over two years

6. **Industry Benchmarks**:
   - Data breach costs based on IBM Cost of a Data Breach Report 2023
   - Breach probabilities based on industry statistics and security maturity
   - Security budget allocation based on Gartner security spending benchmarks
""")

st.markdown('<p class="footnote">Note: This calculator provides estimates based on industry benchmarks and typical results. Actual results may vary based on your specific environment, implementation approach, and other factors.</p>', unsafe_allow_html=True)

# Call to action
st.markdown("""
<div class="result-box">
<h3>Next Steps</h3>
<p>Based on this analysis, implementing HYDRA could provide significant return on investment for your organization through reduced risk, optimized security spending, and improved operational efficiency.</p>
<p>To get a more detailed and customized ROI analysis for your specific environment, contact our team at <a href="mailto:sales@hydra-security.ai">sales@hydra-security.ai</a> or schedule a demo at <a href="https://hydra-security.ai/demo">hydra-security.ai/demo</a>.</p>
</div>
""", unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    # This code will be executed when the script is run directly
    pass
