import json
import logging
import os

import frappe
from frappe.utils import get_bench_path, now

REDACTED_FIELDS = {"pwd", "password", "new_password", "old_password"}


def get_audit_logger() -> logging.Logger:
	logger = logging.getLogger("mylibrary.audit")
	if not logger.handlers:
		directory = os.path.join(get_bench_path(), "logs", "audit")
		os.makedirs(directory, exist_ok=True)
		handler = logging.FileHandler(os.path.join(directory, "requests.log"))
		handler.setFormatter(logging.Formatter("%(message)s"))
		logger.addHandler(handler)
		logger.setLevel(logging.INFO)
		logger.propagate = False
	return logger


def is_enabled() -> bool:
	return bool(frappe.conf.get("library_audit_log"))


def write_entry(entry: dict):
	entry = {"ts": now(), "site": frappe.local.site, "user": frappe.session.user if frappe.session else None, **entry}
	get_audit_logger().info(json.dumps(entry, default=str))


def get_params() -> dict:
	return {key: "*****" if key in REDACTED_FIELDS else value for key, value in (frappe.form_dict or {}).items()}


def log_request(response=None, request=None):
	if not is_enabled() or request is None:
		return
	body = None
	if response is not None and not response.direct_passthrough:
		body = response.get_data(as_text=True)
	write_entry(
		{
			"type": "request",
			"ip": frappe.local.request_ip,
			"method": request.method,
			"path": request.path,
			"status": response.status_code if response is not None else None,
			"params": get_params(),
			"response": body,
		}
	)


def log_job(method=None, kwargs=None, result=None):
	if not is_enabled():
		return
	write_entry({"type": "job", "method": method, "kwargs": kwargs, "result": result})
