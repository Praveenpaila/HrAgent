def document_verification_agent(documents):
    print("\n[Document Verification Agent]")

    required_documents = [
        "identity_document",
        "educational_certificate",
        "signed_offer_letter"
    ]

    submitted = []
    missing = []

    for document in required_documents:
        if documents.get(document, False):
            submitted.append(document)
        else:
            missing.append(document)

    if missing:
        status = "INCOMPLETE"
    else:
        status = "READY"

    result = {
        "agent": "Document Verification Agent",
        "status": status,
        "submitted_documents": submitted,
        "missing_documents": missing
    }

    print("Status:", status)
    print("Submitted documents:", submitted)
    print("Missing documents:", missing)

    return result