from frappe import _


def get_data():
	return {
		"fieldname": "library_member",
		"transactions": [
			{"label": _("Memberships"), "items": ["Library Membership"]},
			{"label": _("Transactions"), "items": ["Library Transaction"]},
		],
	}
