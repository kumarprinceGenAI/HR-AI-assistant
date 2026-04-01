from langchain_core.tools import tool
from data.mock_db import MOCK_HR_DB

@tool
def get_pto_balance(username: str) -> str:
    """Fetch the real-time PTO (Paid Time Off) balance for an employee from the HR Database."""
    user_record = MOCK_HR_DB.get(username.lower())
    if not user_record:
         return f"Error: No HR record found for user {username}."
    return f"{user_record['name']} has {user_record['pto_balance']} days of PTO remaining."

@tool
def get_employee_profile(username: str) -> str:
    """Fetch the full HR profile for an employee including salary, hire date, performance rating, and job title from the HR Database."""
    user_record = MOCK_HR_DB.get(username.lower())
    if not user_record:
         return f"Error: No HR record found for user {username}."
    
    return f"""
Name: {user_record['name']}
Title: {user_record['title']}
Department: {user_record['department']}
Hire Date: {user_record['hire_date']}
Salary: {user_record['salary']}
Performance (Latest): {user_record['performance_rating']}
"""

@tool
def get_benefits_enrollment(username: str) -> str:
    """Fetch the health and benefits enrollment tier for a specific employee."""
    user_record = MOCK_HR_DB.get(username.lower())
    if not user_record:
         return f"Error: No HR record found for user {username}."
    return f"{user_record['name']} is currently enrolled in the following benefits program: {user_record['benefits_plan']}."

@tool
def get_assigned_equipment(username: str) -> str:
    """Fetch the IT hardware and equipment currently assigned to the given employee."""
    user_record = MOCK_HR_DB.get(username.lower())
    if not user_record:
         return f"Error: No HR record found for user {username}."
    return f"Equipment Registry for {user_record['name']}: {user_record['equipment']}."

HR_TOOLS = [get_pto_balance, get_employee_profile, get_benefits_enrollment, get_assigned_equipment]
