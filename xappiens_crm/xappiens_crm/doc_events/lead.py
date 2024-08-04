import frappe
import json
from datetime import datetime

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat() 
    raise TypeError("Type not serializable")

@frappe.whitelist()
def execute(doc, method=None):
    old_lead = frappe.db.sql("""
        SELECT * FROM `tabCRM Lead`
        WHERE email = '{}'
    """.format(doc.email),as_dict=1)
    
   
    
    if old_lead and old_lead[0]['name']!=doc.name:
        serialized_lead = json.dumps(old_lead, default=serialize_datetime)
        doc.append("custom_leads", {
                            "lead_data_json": serialized_lead
                        })
        lead_child =frappe.db.sql("""
        SELECT lc.lead_data_json FROM `tabLead Child` lc,`tabCRM Lead` l
        WHERE lc.parent = l.name and l.name = '{}'
    """.format(old_lead[0]['name']),as_dict=1)
        

        if lead_child:
            for lead in lead_child:
                doc.append("custom_leads", {
                                    "lead_data_json": lead.get('lead_data_json')
                                })
    
        frappe.delete_doc("CRM Lead", old_lead[0]['name'], ignore_missing=True)
        
    