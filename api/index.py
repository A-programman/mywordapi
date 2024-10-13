from flask import Flask
import threading
import time

app = Flask(__name__)

# 定义全局变量
a = 0

def increment_a():
    global a
    while True:
        a += 1
        time.sleep(1)  # 等待1秒钟

@app.route("/")
def main():
    return f"Counter: {a}666"

@app.route("/z")
def add():
    # 开启一个新的线程，执行increment_a函数
    thread = threading.Thread(target=increment_a, daemon=True)
    thread.start()
    return "Started incrementing 'a' every second."
