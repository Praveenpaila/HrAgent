def it_setup_agent(employee):
    print("\n[IT Setup Agent]")

    tasks = {
        "Company email account": "PENDING",
        "System access": "PENDING",
        "Laptop allocation": "PENDING"
    }

    result = {
        "agent": "IT Setup Agent",
        "employee": employee.get("name", ""),
        "tasks": tasks,
        "status": "PENDING"
    }

    print("IT setup checklist:")

    for task, status in tasks.items():
        print(f"- {task}: {status}")

    return result