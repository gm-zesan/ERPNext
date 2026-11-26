frappe.query_reports["Overdue Articles"] = {
	"filters": [
		{
			"fieldname": "member",
			"label": __("Library Member"),
			"fieldtype": "Link",
			"options": "Library Member",
		},
		{
			"fieldname": "article",
			"label": __("Article"),
			"fieldtype": "Link",
			"options": "Article",
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "\nOn Loan\nOverdue",
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "status" && data) {
			if (data.status === "Overdue") {
				value = `<span class="indicator-pill red">${__("Overdue")}</span>`;
			} else if (data.status === "On Loan") {
				value = `<span class="indicator-pill green">${__("On Loan")}</span>`;
			}
		}
		return value;
	},
};
