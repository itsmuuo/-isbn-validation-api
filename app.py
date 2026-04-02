"""
ISBN Validation API
Author: [MARTIN MUUO NTHIWA]
Admission Number: [SCT-254-075/2021]

A Flask REST API for ISBN-10 and ISBN-13 operations including:
- Computing ISBN-10 check digits
- Validating ISBN-10 numbers
- Converting ISBN-10 to ISBN-13
- Validating ISBN-13 numbers
"""

from flask import Flask, request, jsonify

app = Flask(__name__)


# ──────────────────────────────────────────────
# Core ISBN logic
# ──────────────────────────────────────────────

def clean_isbn(isbn: str) -> str:
    """Remove hyphens and spaces from an ISBN string."""
    return isbn.replace("-", "").replace(" ", "").upper()


def compute_isbn10_check_digit(first_nine: str) -> str:
    """
    Compute the check digit for the first 9 digits of an ISBN-10.
    Returns '0'-'9' or 'X' (representing 10).
    """
    if len(first_nine) != 9 or not first_nine.isdigit():
        raise ValueError("Input must be exactly 9 numeric digits.")

    total = sum((10 - i) * int(d) for i, d in enumerate(first_nine))
    remainder = total % 11
    check = (11 - remainder) % 11
    return "X" if check == 10 else str(check)


def validate_isbn10(isbn: str) -> tuple[bool, int]:
    """
    Validate a full 10-character ISBN-10.
    Returns (is_valid, weighted_sum).
    """
    if len(isbn) != 10:
        raise ValueError("ISBN-10 must be exactly 10 characters.")

    total = 0
    for i, ch in enumerate(isbn):
        weight = 10 - i
        if i == 9 and ch == "X":
            value = 10
        elif ch.isdigit():
            value = int(ch)
        else:
            raise ValueError(f"Invalid character '{ch}' at position {i + 1}.")
        total += weight * value

    return (total % 11 == 0), total


def isbn10_to_isbn13(isbn10: str) -> str:
    """
    Convert a valid ISBN-10 to ISBN-13.
    Prepend '978', drop the old check digit, compute a new one.
    """
    first_twelve = "978" + isbn10[:9]

    total = 0
    for i, ch in enumerate(first_twelve):
        weight = 1 if i % 2 else 3  # alternating 1 and 3 starting from position 0
        # ISBN-13 uses 1 for odd positions and 3 for even (0-indexed: 1,3,1,3...)
        weight = 1 if i % 2 != 0 else 3
        # Correct pattern: positions 0,2,4,… → weight 1; positions 1,3,5,… → weight 3
        # Actually standard: pos 0→1, pos 1→3, alternating
        total += int(ch) * (1 if i % 2 == 0 else 3)

    check = (10 - (total % 10)) % 10
    return first_twelve + str(check)


def validate_isbn13(isbn: str) -> tuple[bool, int]:
    """
    Validate a full 13-digit ISBN-13.
    Returns (is_valid, weighted_sum).
    """
    if len(isbn) != 13 or not isbn.isdigit():
        raise ValueError("ISBN-13 must be exactly 13 numeric digits.")

    total = sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(isbn))
    return (total % 10 == 0), total


# ──────────────────────────────────────────────
# API Endpoints
# ──────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "ISBN Validation API",
        "endpoints": {
            "POST /isbn10/check-digit": "Compute the check digit for the first 9 digits of an ISBN-10",
            "POST /isbn10/validate":    "Validate a full ISBN-10 number",
            "POST /isbn10/to-isbn13":   "Convert a valid ISBN-10 to ISBN-13",
            "POST /isbn13/validate":    "Validate a full ISBN-13 number"
        }
    })


@app.route("/isbn10/check-digit", methods=["POST"])
def isbn10_check_digit():
    """
    Compute the check digit for the first 9 digits of an ISBN-10.

    Request JSON: { "isbn": "061826030" }
    Response JSON: {
        "input": "061826030",
        "check_digit": "7",
        "full_isbn10": "0618260307"
    }
    """
    data = request.get_json(silent=True)
    if not data or "isbn" not in data:
        return jsonify({"error": "Request body must be JSON with an 'isbn' field."}), 400

    raw = clean_isbn(str(data["isbn"]))

    if len(raw) != 9:
        return jsonify({
            "error": f"Expected exactly 9 digits, received {len(raw)} characters.",
            "input": data["isbn"]
        }), 400

    if not raw.isdigit():
        return jsonify({
            "error": "All 9 characters must be numeric digits.",
            "input": data["isbn"]
        }), 400

    try:
        check = compute_isbn10_check_digit(raw)
        return jsonify({
            "input": data["isbn"],
            "check_digit": check,
            "full_isbn10": raw + check
        })
    except ValueError as e:
        return jsonify({"error": str(e), "input": data["isbn"]}), 400


@app.route("/isbn10/validate", methods=["POST"])
def isbn10_validate():
    """
    Validate a full 10-character ISBN-10.

    Request JSON: { "isbn": "0618260307" }
    Response JSON: {
        "input": "0618260307",
        "valid": true,
        "weighted_sum": 176,
        "message": "ISBN-10 is valid (sum 176 is divisible by 11)."
    }
    """
    data = request.get_json(silent=True)
    if not data or "isbn" not in data:
        return jsonify({"error": "Request body must be JSON with an 'isbn' field."}), 400

    raw = clean_isbn(str(data["isbn"]))

    if len(raw) != 10:
        return jsonify({
            "error": f"ISBN-10 must be exactly 10 characters (got {len(raw)}).",
            "input": data["isbn"]
        }), 400

    try:
        is_valid, weighted_sum = validate_isbn10(raw)
        status = "valid" if is_valid else "invalid"
        divisibility = "divisible" if is_valid else "not divisible"
        return jsonify({
            "input": data["isbn"],
            "normalized": raw,
            "valid": is_valid,
            "weighted_sum": weighted_sum,
            "message": f"ISBN-10 is {status} (sum {weighted_sum} is {divisibility} by 11)."
        })
    except ValueError as e:
        return jsonify({"error": str(e), "input": data["isbn"]}), 400


@app.route("/isbn10/to-isbn13", methods=["POST"])
def isbn10_to_isbn13_endpoint():
    """
    Convert a valid ISBN-10 to ISBN-13.

    Request JSON: { "isbn": "0618260307" }
    Response JSON: {
        "input": "0618260307",
        "isbn13": "9780618260300",
        "valid_isbn10": true
    }
    """
    data = request.get_json(silent=True)
    if not data or "isbn" not in data:
        return jsonify({"error": "Request body must be JSON with an 'isbn' field."}), 400

    raw = clean_isbn(str(data["isbn"]))

    if len(raw) != 10:
        return jsonify({
            "error": f"ISBN-10 must be exactly 10 characters (got {len(raw)}).",
            "input": data["isbn"]
        }), 400

    try:
        is_valid, weighted_sum = validate_isbn10(raw)
        if not is_valid:
            return jsonify({
                "error": "Cannot convert an invalid ISBN-10 to ISBN-13.",
                "input": data["isbn"],
                "valid_isbn10": False,
                "weighted_sum": weighted_sum
            }), 400

        isbn13 = isbn10_to_isbn13(raw)
        return jsonify({
            "input": data["isbn"],
            "normalized_isbn10": raw,
            "valid_isbn10": True,
            "isbn13": isbn13
        })
    except ValueError as e:
        return jsonify({"error": str(e), "input": data["isbn"]}), 400


@app.route("/isbn13/validate", methods=["POST"])
def isbn13_validate():
    """
    Validate a full 13-digit ISBN-13.

    Request JSON: { "isbn": "9780618260300" }
    Response JSON: {
        "input": "9780618260300",
        "valid": true,
        "weighted_sum": 100,
        "message": "ISBN-13 is valid (sum 100 is divisible by 10)."
    }
    """
    data = request.get_json(silent=True)
    if not data or "isbn" not in data:
        return jsonify({"error": "Request body must be JSON with an 'isbn' field."}), 400

    raw = clean_isbn(str(data["isbn"]))

    if len(raw) != 13:
        return jsonify({
            "error": f"ISBN-13 must be exactly 13 digits (got {len(raw)}).",
            "input": data["isbn"]
        }), 400

    if not raw.isdigit():
        return jsonify({
            "error": "ISBN-13 must contain only numeric digits.",
            "input": data["isbn"]
        }), 400

    try:
        is_valid, weighted_sum = validate_isbn13(raw)
        status = "valid" if is_valid else "invalid"
        divisibility = "divisible" if is_valid else "not divisible"
        return jsonify({
            "input": data["isbn"],
            "normalized": raw,
            "valid": is_valid,
            "weighted_sum": weighted_sum,
            "message": f"ISBN-13 is {status} (sum {weighted_sum} is {divisibility} by 10)."
        })
    except ValueError as e:
        return jsonify({"error": str(e), "input": data["isbn"]}), 400


# ──────────────────────────────────────────────
# Run
# ──────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
