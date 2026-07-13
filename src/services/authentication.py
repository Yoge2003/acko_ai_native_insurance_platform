"""
AuthenticationService wrapping password hashing, user login, lockout policy,
session validations, password verification and auditing systems.
"""

import re
import uuid
import bcrypt
import logging
import secrets
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Dict, Any, List

from src.models.user import User
from src.repositories.user import UserRepository
from src.services.exceptions import ValidationError, ResourceNotFoundError, BusinessRuleViolationError

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("auth_audit")

# Optional: Add file handler to audit_logger
os.makedirs("logs", exist_ok=True)
audit_handler = logging.FileHandler("logs/auth_audit.log", encoding="utf-8")
audit_handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)


class AuthenticationService:
    """
    Core authentication system verifying credentials, password strength,
    lockout policies, reset token configurations, and auditing.
    """

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes raw password string using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verifies raw password matches the bcrypt hash."""
        if not hashed:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validates password strength:
        - Must be at least 8 characters.
        - Must contain at least one uppercase letter.
        - Must contain at least one lowercase letter.
        - Must contain at least one number.
        - Must contain at least one special character.
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter."
        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character."
        return True, "Password is strong."

    def authenticate(self, email: str, password: str, client_ip: Optional[str] = "127.0.0.1") -> User:
        """
        Authenticates user, managing failed attempt locks and audit logs.
        """
        email = email.lower().strip()
        user = self.repository.get_by_email(email)
        
        if not user:
            audit_logger.info(f"FAILED LOGIN: Email '{email}' (User not found) | IP: {client_ip}")
            raise ResourceNotFoundError(f"User with email '{email}' does not exist.")

        if not user.is_active:
            audit_logger.info(f"FAILED LOGIN: Account inactive for '{email}' | Role: {user.role} | IP: {client_ip}")
            raise BusinessRuleViolationError("This user account is currently deactivated.")

        now = datetime.utcnow()
        if user.account_locked_until:
            lock_time = user.account_locked_until.replace(tzinfo=None)
            if now < lock_time:
                minutes_left = int((lock_time - now).total_seconds() / 60) + 1
                audit_logger.info(f"FAILED LOGIN (LOCKED): Account locked for '{email}' | Role: {user.role} | IP: {client_ip}")
                raise BusinessRuleViolationError(f"Account is locked. Try again in {minutes_left} minutes.")

        if self.verify_password(password, user.password_hash):
            updates = {
                "failed_login_attempts": 0,
                "account_locked_until": None,
                "last_login": datetime.utcnow()
            }
            self.repository.update(user, updates)
            audit_logger.info(f"SUCCESS LOGIN: '{email}' | Role: {user.role} | IP: {client_ip}")
            return user
        else:
            attempts = (user.failed_login_attempts or 0) + 1
            updates = {"failed_login_attempts": attempts}
            
            if attempts >= 5:
                lockout_end = datetime.utcnow() + timedelta(minutes=15)
                updates["account_locked_until"] = lockout_end
                audit_logger.info(f"ACCOUNT LOCKED: '{email}' due to 5 consecutive failures | Role: {user.role} | IP: {client_ip}")
                self.repository.update(user, updates)
                raise BusinessRuleViolationError("Too many failed attempts. Account locked for 15 minutes.")
            
            self.repository.update(user, updates)
            audit_logger.info(f"FAILED LOGIN: Invalid password for '{email}' (Attempt {attempts}/5) | Role: {user.role} | IP: {client_ip}")
            raise ValidationError("Invalid email or password.")

    def logout(self, email: str, role: str, client_ip: Optional[str] = "127.0.0.1") -> None:
        """Logs user logout event."""
        audit_logger.info(f"LOGOUT: '{email}' | Role: {role} | IP: {client_ip}")

    def change_password(self, user_id: uuid.UUID, old_password: str, new_password: str) -> None:
        """Verifies old credentials and changes password after validating complexity."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found.")

        if not self.verify_password(old_password, user.password_hash):
            raise ValidationError("Incorrect current password.")

        is_strong, reason = self.validate_password_strength(new_password)
        if not is_strong:
            raise ValidationError(reason)

        new_hash = self.hash_password(new_password)
        self.repository.update(user, {
            "password_hash": new_hash,
            "password_changed_at": datetime.utcnow(),
            "failed_login_attempts": 0,
            "account_locked_until": None
        })
        audit_logger.info(f"PASSWORD CHANGE SUCCESS: '{user.email}'")

    def generate_reset_token(self, email: str) -> str:
        """Generates a secure random verification token."""
        user = self.repository.get_by_email(email.lower().strip())
        if not user:
            raise ResourceNotFoundError(f"User with email '{email}' does not exist.")
        return secrets.token_urlsafe(32)

    def reset_password(self, email: str, new_password: str) -> None:
        """Sets new password without requiring old password (used during verified password recovery)."""
        user = self.repository.get_by_email(email.lower().strip())
        if not user:
            raise ResourceNotFoundError("User not found.")

        is_strong, reason = self.validate_password_strength(new_password)
        if not is_strong:
            raise ValidationError(reason)

        new_hash = self.hash_password(new_password)
        self.repository.update(user, {
            "password_hash": new_hash,
            "password_changed_at": datetime.utcnow(),
            "failed_login_attempts": 0,
            "account_locked_until": None
        })
        audit_logger.info(f"PASSWORD RESET SUCCESS (FORGOT PASSWORD Workflow): '{user.email}'")

    @staticmethod
    def verify_role_permission(role: str, action: str) -> bool:
        """
        Validates permission matrices for RBAC.
        """
        role = role.lower().strip()
        action = action.lower().strip()
        
        if role == "admin":
            role = "administrator"
            
        if role == "administrator":
            return True
            
        role_permissions = {
            "customer": {"quotation", "claims", "chatbot"},
            "claims_officer": {"claims", "dashboard", "manager_ai", "manager_ai_readonly"},
            "underwriter": {"quotation", "dashboard", "chatbot"},
            "manager": {"dashboard", "manager_ai", "reports"}
        }
        
        allowed = role_permissions.get(role, set())
        
        if action == "manager_ai_write" and role == "claims_officer":
            return False
            
        return action in allowed

    def seed_demo_accounts(self) -> None:
        """Sets up default accounts for evaluation."""
        accounts = [
            ("customer@acko.dev", "Customer User", "customer", "AckoCustomer123!"),
            ("claimsofficer@acko.dev", "Claims Officer", "claims_officer", "AckoClaims123!"),
            ("underwriter@acko.dev", "Underwriter User", "underwriter", "AckoUnderwriter123!"),
            ("manager@acko.dev", "Manager User", "manager", "AckoManager123!"),
            ("admin@acko.dev", "Administrator User", "administrator", "AckoAdmin123!")
        ]
        for email, name, role, raw_pwd in accounts:
            existing = self.repository.get_by_email(email)
            if not existing:
                hashed = self.hash_password(raw_pwd)
                new_user = User(
                    full_name=name,
                    email=email,
                    role=role,
                    password_hash=hashed,
                    is_active=True
                )
                self.repository.create(new_user)
                logger.info(f"Seeded demo account: {email} with role: {role}")
