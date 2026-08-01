import pickle
import sys


serialized_data = sys.stdin.buffer.read()
pickle.loads(serialized_data)

with open(sys.argv[1], "rb") as serialized_file:
    pickle.load(serialized_file)

