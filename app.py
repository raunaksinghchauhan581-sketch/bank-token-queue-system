import heapq
from collections import deque
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "bank-token-demo"


class BankTokenSystem:
    """Core DSA logic: deque (FIFO queue) + heapq (priority queue)."""

    def __init__(self):
        self.token_counter = 1
        self.normal_queue = deque()   # FIFO queue for regular customers
        self.priority_heap = []       # min-heap for senior citizens
        self.history = []             # served customers
        self.stats = {"Regular": 0, "Senior": 0}
        self.now_serving = None

    def issue_token(self, name, customer_type):
        token = self.token_counter
        self.token_counter += 1
        customer = {
            "token": f"T{token:03d}",
            "num": token,
            "name": name,
            "type": customer_type,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        if customer_type == "Senior":
            heapq.heappush(self.priority_heap, (token, customer))
        else:
            self.normal_queue.append(customer)
        self.stats[customer_type] += 1
        return customer

    def serve_next(self):
        if self.priority_heap:
            _, customer = heapq.heappop(self.priority_heap)
        elif self.normal_queue:
            customer = self.normal_queue.popleft()
        else:
            return None
        self.history.append(customer)
        self.now_serving = customer
        return customer

    def waiting_count(self):
        return len(self.priority_heap) + len(self.normal_queue)

    def priority_list(self):
        return [c for _, c in sorted(self.priority_heap, key=lambda x: x[0])]

    def regular_list(self):
        return list(self.normal_queue)

    def reset(self):
        self.__init__()


bank = BankTokenSystem()


@app.route("/")
def index():
    return render_template(
        "index.html",
        priority=bank.priority_list(),
        regular=bank.regular_list(),
        history=list(reversed(bank.history)),
        stats=bank.stats,
        total=bank.token_counter - 1,
        served=len(bank.history),
        waiting=bank.waiting_count(),
        now_serving=bank.now_serving,
    )


@app.route("/issue", methods=["POST"])
def issue():
    name = request.form.get("name", "").strip()
    ctype = request.form.get("type", "Regular")
    if not name:
        flash("Customer name cannot be empty.", "error")
    else:
        c = bank.issue_token(name, "Senior" if ctype == "Senior" else "Regular")
        flash(f"Token {c['token']} issued to {c['name']} ({c['type']}).", "success")
    return redirect(url_for("index"))


@app.route("/serve", methods=["POST"])
def serve():
    c = bank.serve_next()
    if c is None:
        flash("No customers waiting.", "error")
    else:
        flash(f"Now serving {c['token']} - {c['name']} ({c['type']}).", "success")
    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    bank.reset()
    flash("System reset for a new day.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
