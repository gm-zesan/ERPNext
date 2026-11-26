# Copyright (c) 2026, Zesan and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today


class IntegrationTestLibraryMembership(IntegrationTestCase):
	def test_membership_validations(self):
		# Create Member
		member = frappe.get_doc({
			"doctype": "Library Member",
			"first_name": "Rahim",
			"last_name": "Uddin",
			"email_address": "rahim@example.com"
		}).insert()

		# 1. Test invalid dates (from_date > to_date)
		invalid_membership = frappe.get_doc({
			"doctype": "Library Membership",
			"library_member": member.name,
			"from_date": today(),
			"to_date": add_days(today(), -5),
			"paid": 1
		})
		self.assertRaises(frappe.ValidationError, invalid_membership.insert)

		# 2. Test unpaid submission
		unpaid_membership = frappe.get_doc({
			"doctype": "Library Membership",
			"library_member": member.name,
			"from_date": today(),
			"to_date": add_days(today(), 30),
			"paid": 0
		}).insert()
		self.assertRaises(frappe.ValidationError, unpaid_membership.submit)

		# 3. Test valid paid submission
		valid_membership = frappe.get_doc({
			"doctype": "Library Membership",
			"library_member": member.name,
			"from_date": today(),
			"to_date": add_days(today(), 30),
			"paid": 1
		}).insert()
		valid_membership.submit()
		self.assertEqual(valid_membership.docstatus, 1)

		# 4. Test overlapping membership
		overlapping_membership = frappe.get_doc({
			"doctype": "Library Membership",
			"library_member": member.name,
			"from_date": add_days(today(), 10),
			"to_date": add_days(today(), 40),
			"paid": 1
		}).insert()
		self.assertRaises(frappe.ValidationError, overlapping_membership.submit)
