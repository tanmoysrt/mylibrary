import logging
import smtplib
from email.message import EmailMessage

import frappe
from frappe.utils import formatdate

DEFAULT_RELAY = "127.0.0.1:2525"
SMTP_TIMEOUT = 10


def get_logger() -> logging.Logger:
	logger = frappe.logger("mylibrary.notifications")
	logger.setLevel(logging.INFO)
	return logger


def get_mail_relay() -> tuple[str, int]:
	host, _, port = (frappe.conf.get("library_mail_relay") or DEFAULT_RELAY).partition(":")
	return host, int(port or 25)


def build_issue_message(register) -> EmailMessage:
	message = EmailMessage()
	message["From"] = frappe.conf.get("library_mail_sender") or f"library@{frappe.local.site}"
	message["To"] = register.member_email
	message["Subject"] = f"Issued: {register.book_title}"
	message.set_content(
		f"Hello {register.member_name or register.member},\n\n"
		f"'{register.book_title}' by {register.author} has been issued to you.\n"
		f"Please return it by {formatdate(register.due_date)}.\n\n"
		f"Reference: {register.name}\n"
	)
	return message


def send_issue_email(register):
	logger = get_logger()
	host, port = get_mail_relay()
	try:
		with smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT) as smtp:
			smtp.send_message(build_issue_message(register))
	except (OSError, smtplib.SMTPException) as error:
		logger.warning(f"{register.name}: delivery to {host}:{port} failed: {error!r}")
		register.db_set("email_status", "Failed")
		return
	logger.info(f"{register.name}: issue email sent to {register.member_email}")
	register.db_set("email_status", "Sent")
