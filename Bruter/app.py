import subprocess as sp
import time
import os
import signal
from colorama import init, Fore, Style

# 12/4/2024 last updated

class Sentient:
    def __init__(self, script_path, num_instances, restart_interval):
        self.script_path = script_path
        self.num_instances = num_instances
        self.restart_interval = restart_interval

    def clear_console(self):
        cmd = 'clear' if os.name == 'posix' else 'cls'
        _ = sp.call(cmd, shell=True)

    def start_process(self):
        return sp.Popen(['python', self.script_path])

    def stop_process(self, proc):
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except sp.TimeoutExpired:
            os.kill(proc.pid, signal.SIGKILL)

    def log_instance(self, action, num, proc):
        status = "OPEN" if action == "start" else "STOPPED"
        color = Fore.GREEN if action == "start" else Fore.RED
        print(f"{color}[ PROCESS ]{Style.RESET_ALL} #{num} | ID: {proc.pid} | STATUS: {status}")
        time.sleep(0.2)

    def start_instances(self):
        procs = []
        self.clear_console()
        print(f"{Fore.YELLOW}[ INFO ]{Style.RESET_ALL} STARTING {self.num_instances} PROCESSES..")
        time.sleep(1)
        self.clear_console()
        for i in range(self.num_instances):
            time.sleep(0.5)
            proc = self.start_process()
            procs.append(proc)
            self.log_instance("start", i+1, proc)
            time.sleep(0.5)
            self.clear_console()
        return procs

    def stop_instances(self, procs):
        print(f"{Fore.YELLOW}[ INFO ]{Style.RESET_ALL} STOPPING {len(procs)} PROCESSES..")
        time.sleep(1)
        self.clear_console()
        for i, proc in enumerate(procs):
            time.sleep(0.5)
            self.stop_process(proc)
            self.log_instance("stop", i+1, proc)
            self.clear_console()

    def countdown(self, seconds):
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            timeformat = f"{mins:02d}:{secs:02d}"
            time.sleep(1)
            seconds -= 1

    def main_loop(self):
        while True:
            procs = self.start_instances()
            self.countdown(self.restart_interval)
            self.stop_instances(procs)
            time.sleep(1)
            self.clear_console()

# Settings
script_path = 'checker.py'
num_instances = 1
restart_interval = 60 # 5 minutes

if __name__ == "__main__":
    manager = Sentient(script_path, num_instances, restart_interval)
    manager.main_loop()