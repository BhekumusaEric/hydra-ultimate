import networkx as nx
import plotly.graph_objects as go

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
