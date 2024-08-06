import frappe

@frappe.whitelist()
def execute(doc, method=None):

    old_lead = frappe.db.sql("""
        SELECT * FROM `tabCRM Lead`
        WHERE email = %s AND name != %s
    """, (doc.email, doc.name), as_dict=1)

    if old_lead:
        old_lead_name = old_lead[0]['name']

        # Load the merging document
        original_doc = frappe.get_doc("CRM Lead", old_lead_name)
        # Create a new merged Leads document instance
        new_doc = frappe.new_doc("Merged Leads")
        # Copy data from the merging document
        new_doc.update(original_doc.as_dict())
         # Set the custom data for the specified fields
        new_doc.set("docname", old_lead_name)
        # Save the new document
        new_doc.insert()


        doc.append("custom_leads", {
            "crm_lead": old_lead[0]['name'],
            "lead_name": old_lead[0]['lead_name'],
            "lead_owner": old_lead[0]['lead_owner']
        })

        lead_child = frappe.db.sql("""
            SELECT crm_lead, lead_name, lead_owner FROM `tabLead Child`
            WHERE parent = %s
        """, old_lead_name, as_dict=1)

        if lead_child:
            for lead in lead_child:
                doc.append("custom_leads", {
                    "crm_lead": lead['crm_lead'],
                    "lead_name": lead['lead_name'],
                    "lead_owner": lead['lead_owner']
                })

        # Eliminar el lead duplicado
        frappe.delete_doc("CRM Lead", old_lead_name, ignore_missing=True)

    frappe.db.commit()  # Asegúrate de que todos los cambios se confirmen en la base de datos
