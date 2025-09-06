from flask import Flask, jsonify, render_template
import math

app = Flask(__name__)

# --- Generar un lado de Koch ---
def trace_koch(order, length, heading, x, y, pts):
    if order == 0:
        rad = math.radians(heading)
        x2 = x + length * math.cos(rad)
        y2 = y + length * math.sin(rad)
        pts.append((x2, y2))
        return x2, y2, heading
    order -= 1
    length /= 3.0
    x, y, heading = trace_koch(order, length, heading, x, y, pts)
    heading += 60
    x, y, heading = trace_koch(order, length, heading, x, y, pts)
    heading -= 120
    x, y, heading = trace_koch(order, length, heading, x, y, pts)
    heading += 60
    x, y, heading = trace_koch(order, length, heading, x, y, pts)
    return x, y, heading

# --- Construir los lados ---
def build_two_sides(order, length, start=(-200, -50), heading=60):
    pts = [start]
    x, y = start
    hdg = heading
    x, y, hdg = trace_koch(order, length, hdg, x, y, pts)
    hdg -= 120
    x, y, hdg = trace_koch(order, length, hdg, x, y, pts)
    return pts

# --- Aplicar corte ---
def clip_points(pts, y_limit):
    result = []
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]

        # ambos arriba
        if y1 >= y_limit and y2 >= y_limit:
            result.append((x1, y1))
            result.append((x2, y2))
            continue

        # ambos abajo
        if y1 < y_limit and y2 < y_limit:
            continue

        # cruza la línea
        dy = y2 - y1
        dx = x2 - x1
        if dy != 0:
            t_cross = (y_limit - y1) / dy
            x_cross = x1 + t_cross * dx
            y_cross = y_limit
            if y1 >= y_limit:
                result.append((x1, y1))
                result.append((x_cross, y_cross))
            else:
                result.append((x_cross, y_cross))
                result.append((x2, y2))
    return result

# ---------------- RUTAS ----------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fractal/<int:order>/<int:length>")
def fractal(order, length):
    pts = build_two_sides(order, length)
    ys = [p[1] for p in pts]
    y_limit = (max(ys) + min(ys)) / 2.0 - 60
    clipped = clip_points(pts, y_limit)
    return jsonify({"points": clipped, "y_limit": y_limit})

if __name__ == "__main__":
    app.run(debug=True)
