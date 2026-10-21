def create_benchmark_dataset():

    all_documents = {
        "identity_document": True,
        "educational_certificate": True,
        "signed_offer_letter": True
    }

    employee = {
        "name": "Rahul",
        "employee_id": "EMP101",
        "department": "IT",
        "role": "Software Developer"
    }

    cases = [
        {
            "id": "TC01",
            "description": "Complete employee information",
            "employee": employee.copy(),
            "documents": all_documents.copy(),
            "expected_status": "READY FOR ONBOARDING"
        },
        {
            "id": "TC02",
            "description": "Missing employee name",
            "employee": {**employee, "name": ""},
            "documents": all_documents.copy(),
            "expected_status": "INCOMPLETE"
        },
        {
            "id": "TC03",
            "description": "Missing employee ID",
            "employee": {**employee, "employee_id": ""},
            "documents": all_documents.copy(),
            "expected_status": "INCOMPLETE"
        },
        {
            "id": "TC04",
            "description": "Missing department",
            "employee": {**employee, "department": ""},
            "documents": all_documents.copy(),
            "expected_status": "INCOMPLETE"
        },
        {
            "id": "TC05",
            "description": "Missing job role",
            "employee": {**employee, "role": ""},
            "documents": all_documents.copy(),
            "expected_status": "INCOMPLETE"
        },
        {
            "id": "TC06",
            "description": "Missing identity document",
            "employee": employee.copy(),
            "documents": {
                **all_documents,
                "identity_document": False
            },
            "expected_status": "INCOMPLETE"
        },
        {
            "id": "TC07",
            "description": "Missing educational certificate",
            "employee": employee.copy(),
            "documents": {
                **all_documents,
                "educational_certificate": False
            },
            "expected_status": "INCOMPLETE"
        },
        {
            "id": "TC08",
            "description": "Missing signed offer letter",
            "employee": employee.copy(),
            "documents": {
                **all_documents,
                "signed_offer_letter": False
            },
            "expected_status": "INCOMPLETE"
        },
        {
            "id": "TC09",
            "description": "Multiple missing employee fields",
            "employee": {
                **employee,
                "name": "",
                "department": ""
            },
            "documents": all_documents.copy(),
            "expected_status": "INCOMPLETE"
        },
        {
            "id": "TC10",
            "description": "Multiple missing documents",
            "employee": employee.copy(),
            "documents": {
                "identity_document": False,
                "educational_certificate": False,
                "signed_offer_letter": True
            },
            "expected_status": "INCOMPLETE"
        }
    ]

    return cases