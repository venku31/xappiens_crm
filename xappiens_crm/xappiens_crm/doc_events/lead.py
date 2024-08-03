import frappe
import json
from datetime import datetime

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat() 
    raise TypeError("Type not serializable")

@frappe.whitelist()
def execute(doc, method=None):
    lead = frappe.db.sql("""
        SELECT * FROM `tabCRM Lead`
        WHERE email = '{}'
    """.format(doc.email),as_dict=1)
    
    if lead and lead[0]['name']!=doc.name:
        serialized_lead = json.dumps(lead, default=serialize_datetime)
        doc.append("custom_leads", {
                            "lead_data_json": serialized_lead
                        })
    
        frappe.delete_doc("CRM Lead", lead[0]['name'], ignore_missing=True)
        
    