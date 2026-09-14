import ast
import operator

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def safe_eval(expr):
    """Evaluate a basic arithmetic expression (+, -, *, /) safely."""
    node = ast.parse(expr, mode="eval").body
    return _eval_node(node)


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    expression = request.json.get("expression", "")
    try:
        result = safe_eval(expression)
        return jsonify(result=result)
    except (ValueError, ZeroDivisionError, SyntaxError, TypeError):
        return jsonify(error="Error"), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
