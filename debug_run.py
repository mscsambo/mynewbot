import sys, os
print("python:", sys.executable)
print("python --version output:")
try:
    import subprocess, shlex
    ver = subprocess.check_output([sys.executable, "--version"], stderr=subprocess.STDOUT, text=True).strip()
    print(ver)
except Exception:
    pass
print("cwd:", os.getcwd())
print("argv:", sys.argv)
print("main.py exists:", os.path.exists("main.py"))
print("==== main.py head (first 120 lines) ====")
try:
    with open("main.py", "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 120:
                break
            print(f"{i+1:03d}: {line.rstrip()}")
except Exception as e:
    print("error reading main.py:", repr(e))
print("==== end ====")