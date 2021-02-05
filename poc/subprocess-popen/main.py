import subprocess

cmd = ["./sub"]

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

for line in iter(p.stdout.readline, b""):
    print(">>> " + str(line.rstrip()))
