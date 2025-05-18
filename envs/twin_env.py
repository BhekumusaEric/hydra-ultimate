import random

class DigitalTwinEnv:
    def __init__(self):
        self.web_app_open = True
        self.db_exposed = False
        self.ports = [22, 80, 443, 3306]  # SSH, HTTP, HTTPS, MySQL
        self.logs = []

    def scan_ports(self):
        return self.ports if self.web_app_open else []

    def try_exploit(self, port):
        if port == 3306 and self.db_exposed:
            self.logs.append("ALERT: Unauthorized DB access!")
            return True
        elif port == 80:
            success = random.random() > 0.6
            if success:
                self.logs.append("ALERT: Web exploit succeeded!")
            return success
        return False

    def deploy_patch(self, patch_type):
        if patch_type == "close_db":
            self.db_exposed = False
            self.logs.append("Blue Agent closed DB exposure.")
        elif patch_type == "block_http":
            self.ports.remove(80)
            self.logs.append("Blue Agent blocked HTTP.")