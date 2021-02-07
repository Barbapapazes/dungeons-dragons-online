import subprocess
import sys


def run(cmd):
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    while True:
        out = proc.stdout.readline()
        if out == "" and proc.poll() != None:
            break
        if out != "":
            out = out.decode("ascii")
            sys.stdout.write(out)
            sys.stdout.flush()


run("./udpserver")
