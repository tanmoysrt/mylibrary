from unittest.mock import MagicMock, patch

import frappe
from frappe.tests import IntegrationTestCase

from mylibrary import audit


class TestAudit(IntegrationTestCase):
	@patch("mylibrary.audit.write_entry")
	def test_disabled_by_default(self, write_entry):
		with patch.dict(frappe.conf, {"library_audit_log": 0}):
			audit.log_request(response=MagicMock(), request=MagicMock())
		write_entry.assert_not_called()

	@patch("mylibrary.audit.write_entry")
	def test_redacts_passwords(self, write_entry):
		frappe.local.form_dict = frappe._dict(usr="librarian@example.test", pwd="secret")
		response = MagicMock(direct_passthrough=False, status_code=200)
		response.get_data.return_value = "{}"
		with patch.dict(frappe.conf, {"library_audit_log": 1}):
			audit.log_request(response=response, request=MagicMock(method="POST", path="/api/method/login"))
		self.assertEqual(write_entry.call_args.args[0]["params"]["pwd"], "*****")
