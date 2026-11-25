import json
import os
import uuid
import logging
from datetime import date, datetime, timezone

import boto3
from botocore.exceptions import ClientError


# AWS Configuration
s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]
PREFIX = "loans/"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

VALID_STATUSES = {
    "Pending",
    "Borrowed",
    "Returned",
    "Rejected"
}


# HTTP Response
def response(status_code, data=None):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(data) if data is not None else ""
    }


def current_time():
    return datetime.now(timezone.utc).isoformat()


def object_key(loan_id):
    return f"{PREFIX}{loan_id}.json"


def parse_body(event):
    body = json.loads(event.get("body") or "{}")

    if not isinstance(body, dict):
        raise ValueError("Request body must be an object")

    return body


# Validate Loan Data
def validate_loan(data):
    required_fields = [
        "borrower_name",
        "borrower_id",
        "equipment_name",
        "quantity",
        "purpose",
        "loan_date",
        "due_date"
    ]

    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValueError(f"{field} is required")

        if isinstance(data[field], str) and not data[field].strip():
            raise ValueError(f"{field} cannot be empty")

    for field in [
        "borrower_name",
        "borrower_id",
        "equipment_name",
        "purpose"
    ]:
        if not isinstance(data[field], str):
            raise ValueError(f"{field} must be a string")

    if type(data["quantity"]) is not int or data["quantity"] <= 0:
        raise ValueError("Quantity must be a positive integer")

    loan_date = date.fromisoformat(data["loan_date"])
    due_date = date.fromisoformat(data["due_date"])

    if due_date < loan_date:
        raise ValueError("Due date cannot be before loan date")

    if data["status"] not in VALID_STATUSES:
        raise ValueError("Invalid loan status")

    if data["status"] == "Returned":
        if not data.get("return_date"):
            raise ValueError("Return date is required")

        return_date = date.fromisoformat(data["return_date"])

        if return_date < loan_date:
            raise ValueError("Invalid return date")


# Read One S3 Object
def read_loan(loan_id):
    try:
        result = s3.get_object(
            Bucket=BUCKET_NAME,
            Key=object_key(loan_id)
        )

        return json.loads(
            result["Body"].read().decode("utf-8")
        )

    except ClientError as error:
        code = error.response["Error"]["Code"]

        if code in ("NoSuchKey", "404", "NotFound"):
            return None

        raise


# CREATE - POST /loans
def create_loan(event):
    body = parse_body(event)

    loan_id = str(uuid.uuid4())

    loan = {
        "loan_id": loan_id,
        "borrower_name": body.get("borrower_name"),
        "borrower_id": body.get("borrower_id"),
        "equipment_name": body.get("equipment_name"),
        "quantity": body.get("quantity"),
        "purpose": body.get("purpose"),
        "loan_date": body.get("loan_date"),
        "due_date": body.get("due_date"),
        "return_date": None,
        "status": "Pending",
        "created_at": current_time(),
        "updated_at": current_time()
    }

    validate_loan(loan)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=object_key(loan_id),
        Body=json.dumps(loan, indent=2),
        ContentType="application/json"
    )

    return response(201, {
        "message": "Loan created successfully",
        "data": loan
    })


# READ - GET /loans
def get_loans():
    loans = []

    paginator = s3.get_paginator("list_objects_v2")

    pages = paginator.paginate(
        Bucket=BUCKET_NAME,
        Prefix=PREFIX
    )

    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]

            if not key.endswith(".json"):
                continue

            result = s3.get_object(
                Bucket=BUCKET_NAME,
                Key=key
            )

            loan = json.loads(
                result["Body"].read().decode("utf-8")
            )

            loans.append(loan)

    loans.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True
    )

    return response(200, {
        "message": "Loans retrieved successfully",
        "total": len(loans),
        "data": loans
    })


# UPDATE - PUT /loans/{id}
def update_loan(event, loan_id):
    loan = read_loan(loan_id)

    if loan is None:
        return response(404, {
            "message": "Loan not found"
        })

    body = parse_body(event)

    allowed_fields = [
        "borrower_name",
        "borrower_id",
        "equipment_name",
        "quantity",
        "purpose",
        "loan_date",
        "due_date",
        "return_date",
        "status"
    ]

    transitions = {
        "Pending": {"Pending", "Borrowed", "Rejected"},
        "Borrowed": {"Borrowed", "Returned"},
        "Returned": {"Returned"},
        "Rejected": {"Rejected"}
    }

    new_status = body.get("status", loan["status"])

    if new_status not in transitions[loan["status"]]:
        return response(400, {
            "message": "Invalid status transition"
        })

    for field in allowed_fields:
        if field in body:
            loan[field] = body[field]

    if loan["status"] == "Returned":
        if not loan.get("return_date"):
            loan["return_date"] = date.today().isoformat()
    else:
        loan["return_date"] = None

    loan["updated_at"] = current_time()

    validate_loan(loan)

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=object_key(loan_id),
        Body=json.dumps(loan, indent=2),
        ContentType="application/json"
    )

    return response(200, {
        "message": "Loan updated successfully",
        "data": loan
    })


# DELETE - DELETE /loans/{id}
def delete_loan(loan_id):
    loan = read_loan(loan_id)

    if loan is None:
        return response(404, {
            "message": "Loan not found"
        })

    if loan["status"] == "Borrowed":
        return response(400, {
            "message": "Active loans cannot be deleted"
        })

    s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=object_key(loan_id)
    )

    return response(204)


# Main Lambda Handler
def lambda_handler(event, context):
    try:
        method = event.get(
            "requestContext", {}
        ).get(
            "http", {}
        ).get("method")

        path = event.get("rawPath", "").rstrip("/")

        # Extract loan ID from URL
        params = event.get("pathParameters") or {}
        loan_id = params.get("id")

        parts = path.strip("/").split("/")

        if not loan_id:
            if len(parts) == 2 and parts[0] == "loans":
                loan_id = parts[1]

        logger.info(
            "Processing request: %s %s",
            method,
            path
        )

        if method == "POST" and path == "/loans":
            return create_loan(event)

        if method == "GET" and path == "/loans":
            return get_loans()

        if method == "PUT" and loan_id:
            return update_loan(event, loan_id)

        if method == "DELETE" and loan_id:
            return delete_loan(loan_id)

        return response(404, {
            "message": "Route not found"
        })

    except (ValueError, TypeError) as error:
        return response(400, {
            "message": str(error)
        })

    except ClientError:
        logger.exception("AWS service error")

        return response(500, {
            "message": "Storage operation failed"
        })

    except Exception:
        logger.exception("Unexpected error")

        return response(500, {
            "message": "Internal server error"
        })