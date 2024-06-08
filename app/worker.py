from celery import Celery
import time

app = Celery('worker', broker='pyamqp://guest@rabbitmq//', backend='rpc://')

@app.task
def fibonacci(n):
    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    result = fib(n)
    # Simulate long-running task

    time.sleep(10)
    print("plus que 10 sc")
    time.sleep(10)
    # Write result to a shared volume
    with open(f"/data/{fibonacci.request.id}.txt", "w") as file:
        file.write(str(result))
    return result
