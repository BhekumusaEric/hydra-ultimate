from graph_env.graph_env import GraphEnv

# Create the graph environment
env = GraphEnv()

# Print initial state
print("Initial state:", env.get_state())
print("Graph nodes:", list(env.graph.nodes))
print("Graph edges:", list(env.graph.edges))

# Simulate some attacks
print("\n--- Simulating attacks ---")
for node in range(5):
    success = env.attack_node(node)
    print(f"Attack on node {node}: {'Successful' if success else 'Failed'}")

# Print state after attacks
print("\nState after attacks:", env.get_state())
print("Compromised nodes:", env.compromised)

# Simulate some defenses
print("\n--- Simulating defenses ---")
for node in env.compromised.copy():
    env.defend_node(node)
    print(f"Node {node} defended")

# Print final state
print("\nFinal state:", env.get_state())
print("Compromised nodes:", env.compromised)

# Print logs
print("\n--- Logs ---")
for log in env.logs:
    print(log)
