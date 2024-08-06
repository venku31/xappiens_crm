import frappe


@frappe.whitelist()
def execute():
    # Consulta para obtener los leads duplicados
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

    # Verifica si se han obtenido leads duplicados
    if not leads:
        return

    leads_by_email = {}
    
    # Agrupar leads por email
    for lead in leads:
        email = lead['email']
        if email not in leads_by_email:
            leads_by_email[email] = []
        leads_by_email[email].append(lead)

    # Procesar cada grupo de leads
    for email, leads in leads_by_email.items():
        # Obtener el lead más reciente
        latest_lead_name = leads[0]['name']
        latest_lead = frappe.get_doc("CRM Lead", latest_lead_name)
        
        for lead in leads:
            if lead['name'] != latest_lead_name:
                # Acceder a los campos del lead duplicado usando el diccionario
                lead_name = lead.get('lead_name', 'Unknown Name')
                lead_owner = lead.get('owner', 'Unassigned')

                # Verificar los valores antes de añadir
                if not lead_name or not lead_owner:
                    continue

                # Agregar datos del lead duplicado a la tabla hija
                latest_lead.append("custom_leads", {
                    "crm_lead": lead['name'],        # Enlace al CRM Lead duplicado
                    "lead_name": lead_name,          # Nombre del lead duplicado
                    "lead_owner": lead_owner         # Usuario al que está asignado
                })
                # Load the merging document
                original_doc = frappe.get_doc("CRM Lead", lead['name'])
                # Create a new merged Leads document instance
                new_doc = frappe.new_doc("Merged Leads")
                # Copy data from the merging document
                new_doc.update(original_doc.as_dict())
                # Set the custom data for the specified fields
                new_doc.set("docname", lead['name'])
                # Save the new document
                new_doc.insert()

                # Eliminar el lead duplicado
                frappe.delete_doc("CRM Lead", lead['name'], ignore_missing=True)
        
        # Guardar los cambios en el lead más reciente
        latest_lead.save()

    frappe.db.commit()  # Asegúrate de que todos los cambios se confirmen en la base de datos
