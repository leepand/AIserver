import json
def load_model(dr):
    with open(dr+'/test.txt') as line:
        for f in line:
            print line
def fib(n):
	if n == 0 or n == 1:
		return 1
	else:
		return fib(n-1) + fib(n-2)
#funcs=['simple.predict']