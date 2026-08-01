import shutil
import subprocess


executable = shutil.which("python")

subprocess.run([executable, "--version"], shell=False, check=True)
subprocess.call([executable, "--version"])
subprocess.Popen([executable, "--version"], shell=False)
subprocess.check_output([executable, "--version"])

