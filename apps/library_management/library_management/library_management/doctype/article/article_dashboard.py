from frappe import _


def get_data():
	return {
		"fieldname": "article",
		"transactions": [
			{"label": _("Transactions"), "items": ["Library Transaction"]},
		],
	}
