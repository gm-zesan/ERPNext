// Copyright (c) 2026, Zesan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Library Transaction", {
	setup(frm) {
		// Article ড্রপডাউন ফিল্টারিং:
		// Issue করার সময় শুধু Available বই দেখাবে
		// Return করার সময় শুধু Issued বই দেখাবে
		frm.set_query("article", () => {
			if (frm.doc.type === "Issue") {
				return {
					filters: {
						status: "Available"
					}
				};
			} else if (frm.doc.type === "Return") {
				return {
					filters: {
						status: "Issued"
					}
				};
			}
		});
	},

	type(frm) {
		// যখন ব্যবহারকারী Type পরিবর্তন করবেন (যেমন Issue থেকে Return),
		// আগের সিলেক্ট করা বইটি রিসেট করে দেওয়া যাতে ভুল বই সেভ না হয়
		frm.set_value("article", "");
	}
});
