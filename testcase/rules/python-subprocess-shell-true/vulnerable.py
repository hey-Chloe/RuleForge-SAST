import subprocess


command = input("Command: ")

subprocess.run(command, shell=True)
subprocess.call(command, shell=True)
subprocess.Popen(command, shell=True)
subprocess.check_output(command, shell=True)

