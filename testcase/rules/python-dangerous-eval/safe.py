import ast


literal = input("Python literal: ")
value = ast.literal_eval(literal)

print(value)

