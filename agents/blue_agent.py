class BlueAgent:
    def __init__(self, env):
        self.env = env

    def act(self):
        for log in self.env.logs[-3:]:  # Monitor recent logs
            if "DB access" in log:
                self.env.deploy_patch("close_db")
            elif "Web exploit" in log:
                self.env.deploy_patch("block_http")