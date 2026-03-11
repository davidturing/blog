import os
import subprocess

env = os.environ.copy()
env["GIT_TERMINAL_PROMPT"] = "0"
env["GIT_EDITOR"] = "true"

print("Starting force push...")
try:
    res = subprocess.run(
        "git push -f work main", cwd="/Users/zhaoqinhuang/david_project", shell=True, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60
    )
    print(f"Return code: {res.returncode}")
    print(f"STDOUT: {res.stdout}")
    print(f"STDERR: {res.stderr}")
except Exception as e:
    print(f"Error: {e}")
