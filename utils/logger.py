import datetime

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("logs/hydra.log", "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")