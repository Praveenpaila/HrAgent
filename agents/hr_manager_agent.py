import time

from agents.employee_information_agent import (
    employee_information_agent
)

from agents.document_verification_agent import (
    document_verification_agent
)

from agents.it_setup_agent import it_setup_agent

from agents.orientation_agent import orientation_agent


def hr_manager_agent(employee, documents):

    print("\nHR MANAGER AGENT STARTED")

    agent_timings = {}

    # Employee Information Agent
    start = time.perf_counter()

    information_result = employee_information_agent(employee)

    agent_timings["employee_information_agent_ms"] = (
        time.perf_counter() - start
    ) * 1000

    # Document Verification Agent
    start = time.perf_counter()

    document_result = document_verification_agent(documents)

    agent_timings["document_verification_agent_ms"] = (
        time.perf_counter() - start
    ) * 1000

    # IT Setup Agent
    start = time.perf_counter()

    it_result = it_setup_agent(employee)

    agent_timings["it_setup_agent_ms"] = (
        time.perf_counter() - start
    ) * 1000

    # Orientation Agent
    start = time.perf_counter()

    orientation_result = orientation_agent(employee)

    agent_timings["orientation_agent_ms"] = (
        time.perf_counter() - start
    ) * 1000

    # Determine overall onboarding status.
    if (
        information_result["status"] != "VALID"
        or document_result["status"] != "READY"
    ):
        overall_status = "INCOMPLETE"
    else:
        overall_status = "READY FOR ONBOARDING"

    report = {
        "employee": employee,
        "information": information_result,
        "documents": document_result,
        "it_setup": it_result,
        "orientation": orientation_result,
        "overall_status": overall_status,
        "agent_timings_ms": agent_timings
    }

    print("\nHR MANAGER AGENT FINISHED")

    return report