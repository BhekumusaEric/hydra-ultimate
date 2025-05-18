class RedAgent:
    def __init__(self, env):
        self.env = env

    def act(self):
        ports = self.env.scan_ports()
        if 3306 in ports:
            return self.env.try_exploit(3306)
        if 80 in ports:
            return self.env.try_exploit(80)
        return False