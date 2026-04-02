# ISBN Validation API

**Author:** [MARTINMUUONTHIWA]  
**Admission Number:** [SCT-254-075/2021]  
**Course:** [PURE MATHEMATICS AND COMPUTERSCIENCE]  
**Lecturer:** Mr. Nyaga  

---

## Overview

A REST API built with Python and Flask that exposes four ISBN-related functionalities:

| # | Feature | Endpoint |
|---|---------|----------|
| a | Compute the check digit of an ISBN-10 | `POST /isbn10/check-digit` |
| b | Validate an ISBN-10 | `POST /isbn10/validate` |
| c | Convert an ISBN-10 to ISBN-13 | `POST /isbn10/to-isbn13` |
| d | Validate an ISBN-13 | `POST /isbn13/validate` |

---

## How ISBN-10 Validation Works

Each digit is multiplied by a descending weight (10 down to 1). The sum must be **divisible by 11**. The last character can be `X`, representing the value **10**.

```
sum = d1×10 + d2×9 + d3×8 + ... + d10×1
valid if sum mod 11 == 0
```

## How ISBN-13 Validation Works

Digits are multiplied by alternating weights of **1** and **3**. The sum must be **divisible by 10**.

```
sum = d1×1 + d2×3 + d3×1 + d4×3 + ...
valid if sum mod 10 == 0
```

---

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/isbn-validation-api.git
cd isbn-validation-api

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python app.py
```

The API will be available at `http://localhost:5000`.

---

## API Reference

All endpoints accept `Content-Type: application/json` and return JSON.

---

### `POST /isbn10/check-digit`

Computes the check digit for the **first 9 digits** of an ISBN-10.

**Request**
```json
{ "isbn": "061826030" }
```

**Response**
```json
{
  "input": "061826030",
  "check_digit": "7",
  "full_isbn10": "0618260307"
}
```

**Error example** (wrong length)
```json
{
  "error": "Expected exactly 9 digits, received 10 characters.",
  "input": "0618260307"
}
```

---

### `POST /isbn10/validate`

Validates a **full 10-character** ISBN-10.

**Request**
```json
{ "isbn": "0618260307" }
```

**Response (valid)**
```json
{
  "input": "0618260307",
  "normalized": "0618260307",
  "valid": true,
  "weighted_sum": 176,
  "message": "ISBN-10 is valid (sum 176 is divisible by 11)."
}
```

**Response (invalid)**
```json
{
  "input": "0618260308",
  "normalized": "0618260308",
  "valid": false,
  "weighted_sum": 177,
  "message": "ISBN-10 is invalid (sum 177 is not divisible by 11)."
}
```

**Example with X check digit**
```json
{ "isbn": "020161622X" }
```
```json
{
  "input": "020161622X",
  "normalized": "020161622X",
  "valid": true,
  "weighted_sum": 110,
  "message": "ISBN-10 is valid (sum 110 is divisible by 11)."
}
```

---

### `POST /isbn10/to-isbn13`

Converts a **valid ISBN-10** to an ISBN-13 by prepending `978` and recomputing the check digit.

**Request**
```json
{ "isbn": "0618260307" }
```

**Response**
```json
{
  "input": "0618260307",
  "normalized_isbn10": "0618260307",
  "valid_isbn10": true,
  "isbn13": "9780618260300"
}
```

**Error (invalid ISBN-10 provided)**
```json
{
  "error": "Cannot convert an invalid ISBN-10 to ISBN-13.",
  "input": "0618260308",
  "valid_isbn10": false,
  "weighted_sum": 177
}
```

---

### `POST /isbn13/validate`

Validates a **full 13-digit** ISBN-13.

**Request**
```json
{ "isbn": "9780618260300" }
```

**Response (valid)**
```json
{
  "input": "9780618260300",
  "normalized": "9780618260300",
  "valid": true,
  "weighted_sum": 100,
  "message": "ISBN-13 is valid (sum 100 is divisible by 10)."
}
```

---

## Part A — Manual Validation Answers

| ISBN-10 | Valid / Invalid | Weighted Sum |
|---------|-----------------|--------------|
| 0618260307 | ✅ Valid | 176 |
| 0451524934 | ✅ Valid | 99 |
| 0262033844 | ✅ Valid | 143 |
| 0131103628 | ✅ Valid | 88 |
| 0132350882 | ✅ Valid | 132 |
| 020161622X | ✅ Valid | 110 |
| 0201633612 | ✅ Valid | 110 |
| 0735619670 | ✅ Valid | 231 |
| 0521642981 | ✅ Valid | 176 |
| 0198538030 | ✅ Valid | 220 |

---

## Part C — Reflection

Manually validating the ISBN numbers in Part A directly informed the design and testing of the API in Part B in several key ways:

1. **Understanding edge cases** — Working through `020161622X` by hand made it clear that the check digit `X` (representing 10) had to be handled explicitly in the code. Without the manual step, this edge case could easily have been overlooked.

2. **Verifying computation logic** — The manual weighted-sum calculations gave known-good expected outputs. These were immediately usable as test cases to confirm the API functions (`compute_isbn10_check_digit`, `validate_isbn10`) returned correct results.

3. **Separating concerns** — Doing Part A first clarified that computing a check digit (given 9 digits) and validating a full ISBN-10 (given 10 characters) are logically distinct operations, which is why they became two separate endpoints rather than one.

4. **ISBN-13 conversion intuition** — After manually understanding the ISBN-10 check digit algorithm, the conversion process (drop old check digit → prepend 978 → compute new check digit with the 1/3 alternating scheme) was much easier to implement correctly.

---

## Project Structure

```
isbn-validation-api/
├── app.py            # Main Flask application
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## License

For educational use only.
