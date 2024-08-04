frappe.listview_settings['CRM Lead'] = {
    onload: function(listview) {
        // Add Merge Leads button to the list view toolbar
        listview.page.add_inner_button(__('Merge Leads'), function() {
           
            frappe.confirm("Are you sure you want to merge Leads?", function() {
                  frappe.call({
                    method: "xappiens_crm.patches.add_lead_data.execute",
                    args: {
                       
                    },
                    callback: function(response) {
                        listview.refresh();
                    }
                });
            });
        });
    }
};