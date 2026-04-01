import uuid
from datetime import datetime
import json
import logging
import os

logger = logging.getLogger(__name__)

TICKETS_FILE = "data/tickets_db.json"

def create_ticket(username: str, issue: str) -> str:
    """Simulate creating an empathetic and secure HR Support Ticket."""
    ticket_id = f"HR-{str(uuid.uuid4())[:6].upper()}"
    
    ticket = {
        "ticket_id": ticket_id,
        "username": username,
        "issue": issue,
        "status": "OPEN_ESCALATED",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    tickets = []
    if os.path.exists(TICKETS_FILE):
        try:
            with open(TICKETS_FILE, "r") as f:
                tickets = json.load(f)
        except Exception:
            pass
            
    tickets.append(ticket)
    
    with open(TICKETS_FILE, "w") as f:
        json.dump(tickets, f, indent=4)
        
    logger.warning(f"URGENT: Escalation Ticket {ticket_id} created for {username}. Reason: Sensitive Payload.")
    
    return ticket_id
