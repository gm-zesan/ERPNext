// Copyright (c) 2026, Zesan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Library Member", {
	refresh(frm) {
		// শুধুমাত্র সেভ করা ডকুমেন্টে (New ছাড়া) বাটন দুটি সরাসরি টপবারে দেখাবে
		if (!frm.is_new()) {
			// বাটন ১: Create Membership
			frm.add_custom_button(__("Create Membership"), () => {
				frappe.new_doc("Library Membership", {
					library_member: frm.doc.name
				});
			});

			// বাটন ২: Issue Book
			frm.add_custom_button(__("Issue Book"), () => {
				frappe.new_doc("Library Transaction", {
					library_member: frm.doc.name,
					type: "Issue"
				});
			});
		}
	}
});
