import frappe
import json
from datetime import datetime

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat() 
    raise TypeError("Type not serializable")

@frappe.whitelist()
def execute(doc, method=None):
    leads = frappe.db.sql("""
        SELECT * FROM `tabCRM Lead`
        WHERE email IN (
            SELECT email
            FROM `tabCRM Lead`
            GROUP BY email
            HAVING COUNT(*) > 1
        )
        ORDER BY creation DESC;
    """, as_dict=1)
    
    if leads:
        leads_by_email = {}
        for lead in leads:
            email = lead['email']
            if email not in leads_by_email:
                leads_by_email[email] = []
            leads_by_email[email].append(lead)
        
        for email, leads in leads_by_email.items():
            latest_lead_name = leads[0]['name']
            latest_lead = frappe.get_doc("CRM Lead", latest_lead_name)
            
            for lead in leads:
                if lead['name'] != latest_lead_name:
                    serialized_lead = json.dumps(lead, default=serialize_datetime)
                    latest_lead.append("custom_leads", {
                        "lead_data_json": serialized_lead
                    })
                    
      
                    frappe.delete_doc("CRM Lead", lead['name'], ignore_missing=True)
            
            latest_lead.save()