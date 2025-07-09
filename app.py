from flask import Flask, render_template, jsonify, request
import threading
import time
import random

app = Flask(__name__)

candles = []
auto_mode = {"active": False}
ultima_decisao = ""

def gerar_candles():
    base = 30000
    while True:
        if len(candles) > 60:
            candles.pop(0)
        candles.append({
            "timestamp": time.strftime('%H:%M:%S'),
            "close": round(base + random.uniform(-200, 200), 2)
        })
        time.sleep(5)

def estrategia_simples(closes):
    if len(closes) < 2:
        return "Aguardando dados suficientes..."
    if closes[-1] > closes[-2] * 1.01:
        return "COMPRAR 📈 (subiu mais de 1%)"
    elif closes[-1] < closes[-2] * 0.99:
        return "VENDER 📉 (caiu mais de 1%)"
    else:
        return "MANTER 🤝 (movimento neutro)"

def loop_estrategia():
    global ultima_decisao
    while True:
        if auto_mode["active"] and len(candles) >= 2:
            closes = [c["close"] for c in candles]
            ultima_decisao = estrategia_simples(closes)
            print("💡 Decisão:", ultima_decisao)
        time.sleep(10)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/candles")
def get_candles():
    return jsonify({
        "timestamps": [c["timestamp"] for c in candles],
        "closes": [c["close"] for c in candles]
    })

@app.route("/api/auto", methods=["POST"])
def toggle_auto():
    auto_mode["active"] = not auto_mode["active"]
    return jsonify({"status": "ok", "auto": auto_mode["active"]})

@app.route("/api/decisao")
def get_decisao():
    return jsonify({"decisao": ultima_decisao})

threading.Thread(target=gerar_candles, daemon=True).start()
threading.Thread(target=loop_estrategia, daemon=True).start()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
