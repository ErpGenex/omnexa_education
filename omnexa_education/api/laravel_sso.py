# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""JWT SSO handoff from ErpGenEx portals to Laravel TLMS."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

import frappe
from frappe import _

from omnexa_education.api import laravel_client


def _base64url(data: bytes) -> str:
	return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _encode_jwt(payload: dict, secret: str) -> str:
	header = {"typ": "JWT", "alg": "HS256"}
	segments = [
		_base64url(json.dumps(header, separators=(",", ":")).encode()),
		_base64url(json.dumps(payload, separators=(",", ":")).encode()),
	]
	signing_input = ".".join(segments)
	signature = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
	segments.append(_base64url(signature))
	return ".".join(segments)


def _portal_identity(user: str) -> dict | None:
	student = frappe.db.get_value(
		"Education Student",
		{"user": user},
		["name", "laravel_user_id", "financial_hold", "account_access_status", "institution"],
		as_dict=True,
	)
	if student:
		return {
			"role": "student",
			"laravel_user_id": student.laravel_user_id,
			"financial_hold": bool(student.financial_hold),
			"account_status": (student.account_access_status or "Active").lower().replace(" ", "_"),
			"external_id": student.name,
			"institution": student.institution,
		}
	parent_students = frappe.get_all(
		"Education Student",
		filters={"guardian_email": user, "status": "Active"},
		fields=["name", "guardian_laravel_user_id", "guardian_user", "institution"],
		limit=1,
	)
	if parent_students:
		row = parent_students[0]
		laravel_id = row.guardian_laravel_user_id
		if not laravel_id and row.guardian_user:
			laravel_id = frappe.db.get_value("User", row.guardian_user, "name")
		return {
			"role": "parent",
			"laravel_user_id": laravel_id,
			"financial_hold": False,
			"account_status": "active",
			"external_id": row.name,
			"institution": row.institution,
		}
	return None


@frappe.whitelist()
def get_laravel_sso_handoff(target: str = "dashboard") -> dict:
	settings = frappe.get_single("Education Settings")
	if not settings.enable_laravel_tlms or not settings.laravel_sso_enabled:
		frappe.throw(_("Laravel SSO is not enabled in Education Settings."))
	secret = settings.get_password("laravel_jwt_secret") if settings.laravel_jwt_secret else ""
	if not secret:
		frappe.throw(_("Laravel JWT secret is not configured."))

	user = frappe.session.user
	if user in ("Guest", "Administrator"):
		frappe.throw(_("SSO is only available for portal users."))

	identity = _portal_identity(user)
	if not identity or not identity.get("laravel_user_id"):
		frappe.throw(_("No Laravel account linked to your portal profile. Ask the registrar to provision access."))

	if identity.get("financial_hold"):
		frappe.throw(_("Account access is restricted. Contact the finance office."))
	status = (identity.get("account_status") or "active").lower().replace(" ", "_")
	if status not in ("active",):
		frappe.throw(_("Account access is restricted. Contact the registrar."))

	now = int(time.time())
	claims = {
		"sub": str(identity["laravel_user_id"]),
		"email": user,
		"role": identity["role"],
		"external_id": identity.get("external_id"),
		"financial_hold": identity.get("financial_hold", False),
		"account_status": "active",
		"iat": now,
		"exp": now + 3600,
	}
	token = _encode_jwt(claims, secret)
	base = (settings.laravel_base_url or "").rstrip("/")
	login_url = f"{base}/api/v1/sso/login"
	redirect_url = f"{base}/sso/erpgenex?token={token}&target={target}"
	return {
		"token": token,
		"login_url": login_url,
		"redirect_url": redirect_url,
		"expires_in": 3600,
		"laravel_enabled": laravel_client.is_laravel_enabled(),
	}

