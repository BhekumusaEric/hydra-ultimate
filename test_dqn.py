from deep_learning.dqn_agent import DQNAgent
import numpy as np

# Create a simple environment state
state_size = 5  # 5 nodes in the graph
action_size = 2  # attack or defend

# Initialize the DQN agent
agent = DQNAgent(state_size, action_size)

# Test the agent's decision-making
print("Testing DQN Agent decision-making:")
for i in range(5):
    # Create a random state
    state = np.random.randint(0, 2, size=state_size)
    action = agent.act(state)
    print(f"State: {state}, Action: {action}")

# Test the agent's learning
print("\nTesting DQN Agent learning:")
for i in range(10):
    # Generate random experiences
    state = np.random.randint(0, 2, size=state_size)
    action = agent.act(state)
    reward = np.random.randint(0, 2)  # 0 or 1
    next_state = np.random.randint(0, 2, size=state_size)
    
    # Remember the experience
    agent.remember(state, action, reward, next_state)
    
    # Print the experience
    print(f"Experience {i+1}: State={state}, Action={action}, Reward={reward}, Next State={next_state}")

# Train the agent
print("\nTraining the agent...")
agent.replay(batch_size=5)
print("Training complete!")

# Test the agent's decision-making after training
print("\nTesting DQN Agent decision-making after training:")
for i in range(5):
    # Create a random state
    state = np.random.randint(0, 2, size=state_size)
    action = agent.act(state)
    print(f"State: {state}, Action: {action}")
