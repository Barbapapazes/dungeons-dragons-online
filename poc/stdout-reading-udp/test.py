import subprocess
import sys


def run(cmd):
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate()

    return proc.returncode, stdout, stderr


code, out, err = run([sys.executable, "poc/stdout-reading-udp/print.py"])
out = out.decode("ascii")
err = err.decode("ascii")
print("out: ", out)
print("err: ", err)
print("exit: ", code)
