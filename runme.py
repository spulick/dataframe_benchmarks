import subprocess
import os
import sys

import pip

try:
    subprocess.check_output("nvidia-smi")

    #subprocess.check_call([sys.executable, "-m", "pip", "install", ])
    pip.main(["install", "--extra-index-url=https://pypi.nvidia.com", "cudf-cu12==25.4.*", "dask-cudf-cu12==25.4.*", "cuml-cu12==25.4.*", "cugraph-cu12==25.4.*"])

    os.system("python -m cudf.pandas test_script.py")

except subprocess.CalledProcessError:
    os.system("python test_script.py")

