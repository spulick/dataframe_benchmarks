import subprocess
import os

try:
    subprocess.check_output("nvidia-smi")

    os.system("python -m cudf.pandas test_script.py")

except subprocess.CalledProcessError:
    os.system("python test_script.py")

