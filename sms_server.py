from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
API_URL = "https://apisell24.shop/sms.php"

@app.route("/")
def home():
    return """
    <h2>SMS Sender API</h2>
    <p>Usage: <code>/send?num=01XXXXXXXXX&msg=Hello&count=2</code></p>
    <form action="/send">
        <input name="num" placeholder="Number" required><br><br>
        <input name="msg" placeholder="Message" required><br><br>
        <input name="count" type="number" value="2" placeholder="Count"><br><br>
        <button type="submit">Send SMS</button>
    </form>
    """

@app.route("/send")
def send():
    num = request.args.get("num")
    msg = request.args.get("msg")
    count = int(request.args.get("count", 2))

    if not num or not msg:
        return jsonify({"error": "num and msg required"}), 400

    results = []
    for i in range(1, count + 1):
        try:
            r = requests.get(API_URL, params={"num": num, "msg": msg}, timeout=15)
            results.append(f"[{i}/{count}] {r.status_code} | {r.text.strip()}")
        except Exception as e:
            results.append(f"[{i}/{count}] FAILED: {e}")

    return jsonify({"number": num, "message": msg, "count": count, "results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)