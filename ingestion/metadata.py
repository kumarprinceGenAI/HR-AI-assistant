import re

def extract_metadata(chunk: str, source: str):
    """
    Extract metadata from a chunk of text
    """

    # Extract policy ID
    policy_match = re.search(r"\[ID:\s*(.*?)\]", chunk)
    policy_id = policy_match.group(1) if policy_match else None

    # Extract section name
    section_match = re.search(r"\d+\.\s*(.*?)\s*\[ID:", chunk)
    section = section_match.group(1) if section_match else None

    # Extract document name from file path
    doc_name = source.split("\\")[-1].replace(".pdf", "")
    
    # RBAC Logic Simulation
    # By default, all public roles (including guests) can see general documents
    allowed_roles = ["guest", "employee", "manager", "executive"]
    
    if section:
        s = section.lower()
        # Restrict internal employee policies from guest view
        if "onboarding" in s or "internal" in s:
            allowed_roles = ["employee", "manager", "executive"]
        # Create restricted sections to mock high-tier RBAC
        elif "performance" in s or "manager" in s:
            allowed_roles = ["manager", "executive"]
        elif "executive" in s or "compensation" in s or "finance" in s:
            allowed_roles = ["executive"]

    return {
        "policy_id": policy_id,
        "section": section,
        "document": doc_name,
        "allowed_roles": allowed_roles
    }