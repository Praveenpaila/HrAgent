def employee_information_agent(employee):
    print("\n[Employee Information Agent]")

    required_fields = [
        "name",
        "employee_id",
        "department",
        "role"
    ]

    missing_fields = []

    for field in required_fields:
        if not employee.get(field, "").strip():
            missing_fields.append(field)

    if missing_fields:
        status = "INCOMPLETE"
    else:
        status = "VALID"

    result = {
        "agent": "Employee Information Agent",
        "status": status,
        "missing_fields": missing_fields
    }

    print("Status:", status)

    if missing_fields:
        print("Missing fields:", ", ".join(missing_fields))
    else:
        print("Employee information is available.")

    return result