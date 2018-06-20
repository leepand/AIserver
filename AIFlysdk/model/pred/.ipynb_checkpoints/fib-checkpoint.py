import json



def load_model(model_dir):
    return fib(model_dir)


class fib:
    def __init__(self,model_dir):
        self.model_dir=None

    def predict(self, n):
        if n == 0 or n == 1:
            return 1
        else:
            return self.predict(n-1) + self.predict(n-2)

    