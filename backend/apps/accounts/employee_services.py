import csv
import os

from django.db import transaction

from .models import EmployeeRecord, EmployeeUploadBatch


class EmployeeRosterProcessingError(Exception):
    pass


REQUIRED_COLUMNS = ["employee_id"]


def normalize_value(value):
    return str(value or "").strip()


def normalize_employee_id(value):
    return normalize_value(value).upper()


def validate_csv_headers(headers):
    normalized_headers = [item.strip().lower() for item in headers]

    for column in REQUIRED_COLUMNS:
        if column not in normalized_headers:
            raise EmployeeRosterProcessingError(
                f"Missing required column: {column}"
            )

    return normalized_headers


def read_employee_csv(file_path):
    records = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        headers = validate_csv_headers(reader.fieldnames or [])

        for row in reader:
            normalized_row = {
                key.strip().lower(): normalize_value(value)
                for key, value in row.items()
                if key
            }

            employee_id = normalize_employee_id(
                normalized_row.get("employee_id")
            )

            if not employee_id:
                continue

            records.append(
                {
                    "employee_id": employee_id,
                    "full_name": normalize_value(
                        normalized_row.get("full_name")
                    ),
                    "email": normalize_value(
                        normalized_row.get("email")
                    ).lower(),
                    "department": normalize_value(
                        normalized_row.get("department")
                    ),
                    "role_type": normalize_value(
                        normalized_row.get("role_type")
                    ).upper()
                    or EmployeeRecord.RoleType.USER,
                }
            )

    return records


def validate_role_type(role_type):
    allowed = {
        EmployeeRecord.RoleType.USER,
        EmployeeRecord.RoleType.AGENT,
        EmployeeRecord.RoleType.ADMIN,
    }

    if role_type not in allowed:
        return EmployeeRecord.RoleType.USER

    return role_type


def process_employee_roster(batch: EmployeeUploadBatch):
    try:
        file_path = batch.file.path
        ext = os.path.splitext(batch.file.name)[1].lower()

        batch.status = EmployeeUploadBatch.Status.PROCESSING
        batch.error_message = ""
        batch.save(update_fields=["status", "error_message", "updated_at"])

        if ext != ".csv":
            raise EmployeeRosterProcessingError(
                "Only CSV employee roster upload is supported in Phase 18 Step 1."
            )

        records = read_employee_csv(file_path)

        if not records:
            raise EmployeeRosterProcessingError(
                "No valid employee records found in uploaded file."
            )

        uploaded_employee_ids = set()

        with transaction.atomic():
            # Mark all old employee IDs inactive first.
            EmployeeRecord.objects.update(is_active=False)

            for item in records:
                employee_id = item["employee_id"]
                uploaded_employee_ids.add(employee_id)

                record, created = EmployeeRecord.objects.update_or_create(
                    employee_id=employee_id,
                    defaults={
                        "full_name": item.get("full_name", ""),
                        "email": item.get("email", ""),
                        "department": item.get("department", ""),
                        "role_type": validate_role_type(
                            item.get("role_type", EmployeeRecord.RoleType.USER)
                        ),
                        "is_active": True,
                        "upload_batch": batch,
                    },
                )

            active_count = EmployeeRecord.objects.filter(is_active=True).count()
            inactive_count = EmployeeRecord.objects.filter(is_active=False).count()

            batch.status = EmployeeUploadBatch.Status.COMPLETED
            batch.total_records = len(records)
            batch.active_records = active_count
            batch.inactive_records = inactive_count
            batch.error_message = ""
            batch.save(
                update_fields=[
                    "status",
                    "total_records",
                    "active_records",
                    "inactive_records",
                    "error_message",
                    "updated_at",
                ]
            )

        return batch

    except Exception as exc:
        batch.status = EmployeeUploadBatch.Status.FAILED
        batch.error_message = str(exc)
        batch.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )
        return batch


def validate_employee_can_register(employee_id, email):
    employee_id = normalize_employee_id(employee_id)
    email = normalize_value(email).lower()

    if not employee_id:
        raise EmployeeRosterProcessingError("Employee ID is required.")

    try:
        record = EmployeeRecord.objects.get(employee_id=employee_id)
    except EmployeeRecord.DoesNotExist:
        raise EmployeeRosterProcessingError(
            "This employee ID is not allowed to register."
        )

    if not record.is_active:
        raise EmployeeRosterProcessingError(
            "This employee ID is inactive. Please contact admin."
        )

    if record.registered_user_id:
        raise EmployeeRosterProcessingError(
            "This employee ID is already registered."
        )

    if record.email and email and record.email.lower() != email:
        raise EmployeeRosterProcessingError(
            "Email does not match the company employee record."
        )

    return record


def validate_employee_can_login(user):
    employee_id = normalize_employee_id(getattr(user, "employee_id", ""))

    # Admin accounts can be allowed even if manually created.
    if getattr(user, "role", "") == "ADMIN" and not employee_id:
        return True

    if not employee_id:
        raise EmployeeRosterProcessingError(
            "Employee ID is missing for this account. Please contact admin."
        )

    try:
        record = EmployeeRecord.objects.get(employee_id=employee_id)
    except EmployeeRecord.DoesNotExist:
        raise EmployeeRosterProcessingError(
            "Your employee ID is not in the active company roster."
        )

    if not record.is_active:
        raise EmployeeRosterProcessingError(
            "Your employee ID is inactive. Login is blocked."
        )

    return True