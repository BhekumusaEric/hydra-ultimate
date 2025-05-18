from envs.twin_env import DigitalTwinEnv
from agents.red_agent import RedAgent
from agents.blue_agent import BlueAgent
from utils.replay_buffer import ReplayBuffer
from utils.logger import log_event

env = DigitalTwinEnv()
red = RedAgent(env)
blue = BlueAgent(env)
buffer = ReplayBuffer()

env.db_exposed = True

for step in range(20):
    print(f"\n--- Step {step + 1} ---")
    state = {"ports": env.ports.copy(), "db_exposed": env.db_exposed}
    attack_success = red.act()
    blue.act()
    next_state = {"ports": env.ports.copy(), "db_exposed": env.db_exposed}
    reward = 1 if attack_success else 0
    buffer.add(state, "attack", reward, next_state)

    log_event(f"Step {step + 1}: attack_success={attack_success}, reward={reward}")

    print("[Logs]")
    for log in env.logs:
        print(" ", log)