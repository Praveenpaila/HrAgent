from agents.hr_manager_agent import hr_manager_agent
from evaluation.evaluator import run_benchmark


def get_employee_details():

    print("\nEnter Employee Details")

    employee = {
        "name": input("Employee Name: ").strip(),
        "employee_id": input("Employee ID: ").strip(),
        "department": input("Department: ").strip(),
        "role": input("Job Role: ").strip()
    }

    return employee


def get_document_status():

    print("\nDocument Submission")

    documents = {}

    questions = {
        "identity_document": "Identity document submitted?",
        "educational_certificate": "Educational certificate submitted?",
        "signed_offer_letter": "Signed offer letter submitted?"
    }

    for document, question in questions.items():

        while True:

            answer = input(
                f"{question} (yes/no): "
            ).strip().lower()

            if answer in ("yes", "no"):
                documents[document] = answer == "yes"
                break

            print("Enter yes or no.")

    return documents


def display_final_report(report):

    employee = report["employee"]

    print("\n" + "=" * 45)
    print("EMPLOYEE ONBOARDING REPORT")
    print("=" * 45)

    print("Name:", employee["name"] or "Not provided")
    print("Employee ID:", employee["employee_id"] or "Not provided")
    print("Department:", employee["department"] or "Not provided")
    print("Job Role:", employee["role"] or "Not provided")

    print("\nInformation Status:")
    print(report["information"]["status"])

    print("\nDocument Status:")
    print(report["documents"]["status"])

    print("\nMissing Documents:")

    for document in report["documents"]["missing_documents"]:
        print("-", document.replace("_", " ").title())

    print("\nIT Setup:")

    for task, status in report["it_setup"]["tasks"].items():
        print(f"- {task}: {status}")

    print("\nOrientation:")

    for activity, status in report["orientation"]["activities"].items():
        print(f"- {activity}: {status}")

    print("\nOverall Status:")
    print(report["overall_status"])

    print("=" * 45)


def run_onboarding():

    employee = get_employee_details()
    documents = get_document_status()

    report = hr_manager_agent(employee, documents)

    display_final_report(report)


def main():

    while True:

        print("\n" + "=" * 45)
        print("HR EMPLOYEE ONBOARDING MULTI-AGENT SYSTEM")
        print("=" * 45)

        print("1. Run Employee Onboarding")
        print("2. Run Benchmark and Evaluation")
        print("3. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            run_onboarding()

        elif choice == "2":
            run_benchmark()

        elif choice == "3":
            print("Exiting application.")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()