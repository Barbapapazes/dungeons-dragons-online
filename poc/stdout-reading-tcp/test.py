import subprocess
import sys


def run(cmd):
    """
    function that creates a sub-process that will execute the command given in parameter.
    While the sub-process is running the function will read stdout line-by-line and print it on screen.

    Args:
        cmd (str): string that will indicate which command Popen be execute.
    """
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    while True:
        out = proc.stdout.readline()
        if proc.poll() is not None:
            if out is not None:
                out = out.decode("ascii")
                sys.stdout.write(out)
                sys.stdout.flush()
            return
        if out != "":
            out = out.decode("ascii")
            sys.stdout.write(out)
            sys.stdout.flush()


run("./tcpserver")
print("end of the python program")
