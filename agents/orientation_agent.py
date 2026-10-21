def orientation_agent(employee):
    print("\n[Orientation Agent]")

    activities = {
        "Company introduction": "PLANNED",
        "HR policy explanation": "PLANNED",
        "Team introduction": "PLANNED",
        "Workplace guidelines": "PLANNED"
    }

    result = {
        "agent": "Orientation Agent",
        "employee": employee.get("name", ""),
        "activities": activities,
        "status": "PLANNED"
    }

    print("Orientation checklist:")

    for activity, status in activities.items():
        print(f"- {activity}: {status}")

    return result