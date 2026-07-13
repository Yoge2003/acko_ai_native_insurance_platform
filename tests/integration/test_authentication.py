"""
Integration test suite for the Enterprise Authentication and RBAC layer.
"""

import unittest
from datetime import datetime, timedelta

from src.database.session import SessionLocal
from src.database.base import Base
from src.repositories.user import UserRepository
from src.services.authentication import AuthenticationService
from src.services.exceptions import ValidationError, ResourceNotFoundError, BusinessRuleViolationError
from src.models.user import User


class TestAuthenticationIntegration(unittest.TestCase):
    def setUp(self) -> None:
        import src.database.database as db_module
        if db_module.engine is not None:
            SessionLocal.configure(bind=db_module.engine)
            Base.metadata.create_all(bind=db_module.engine)
        self.session = SessionLocal()
        self.repo = UserRepository(self.session)
        self.service = AuthenticationService(self.repo)
        self.cleanup_records()

    def tearDown(self) -> None:
        self.cleanup_records()
        self.session.close()

    def cleanup_records(self) -> None:
        try:
            self.session.query(User).filter(User.email.like("%test_auth_%")).delete(synchronize_session=False)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Cleanup warning: {e}")

    def test_password_hashing_and_verification(self) -> None:
        """Verifies manual and correct password hashing verification lifecycle."""
        pwd = "SecurePassword123!"
        hashed = AuthenticationService.hash_password(pwd)
        self.assertTrue(AuthenticationService.verify_password(pwd, hashed))
        self.assertFalse(AuthenticationService.verify_password("wrong", hashed))

    def test_password_strength_constraints(self) -> None:
        """Validates all complexity requirements (length, case, numbers, special characters)."""
        # Weak passwords
        self.assertFalse(AuthenticationService.validate_password_strength("weak")[0])
        self.assertFalse(AuthenticationService.validate_password_strength("weak123!")[0])
        self.assertFalse(AuthenticationService.validate_password_strength("WEAK123!")[0])
        self.assertFalse(AuthenticationService.validate_password_strength("Weakpassword!")[0])
        self.assertFalse(AuthenticationService.validate_password_strength("Weakpassword123")[0])
        
        # Strong password
        is_strong, msg = AuthenticationService.validate_password_strength("SecurePassword123!")
        self.assertTrue(is_strong)

    def test_authentication_workflow(self) -> None:
        """Verifies login lifecycle, failed count, last login, and lockouts."""
        email = "test_auth_log@acko.com"
        pwd = "SecurePassword123!"
        hashed = AuthenticationService.hash_password(pwd)
        
        # Create user
        user = User(
            full_name="Auth Tester",
            email=email,
            role="customer",
            password_hash=hashed,
            is_active=True
        )
        self.repo.create(user)
        
        # Test success login
        authed_user = self.service.authenticate(email, pwd)
        self.assertEqual(authed_user.email, email)
        self.assertEqual(authed_user.failed_login_attempts, 0)
        self.assertIsNotNone(authed_user.last_login)
        
        # Test incorrect password fail increments
        with self.assertRaises(ValidationError):
            self.service.authenticate(email, "WrongPassword@123")
            
        updated_user = self.repo.get_by_email(email)
        self.assertEqual(updated_user.failed_login_attempts, 1)

    def test_account_lockout(self) -> None:
        """Verifies account gets locked for 15 minutes after 5 consecutive failures."""
        email = "test_auth_lock@acko.com"
        pwd = "SecurePassword123!"
        hashed = AuthenticationService.hash_password(pwd)
        
        user = User(
            full_name="Lockout Tester",
            email=email,
            role="customer",
            password_hash=hashed,
            is_active=True,
            failed_login_attempts=4
        )
        self.repo.create(user)
        
        # Fifth failed attempt should trigger lockout
        with self.assertRaises(BusinessRuleViolationError) as ctx:
            self.service.authenticate(email, "WrongPassword@123")
        self.assertIn("locked", str(ctx.exception).lower())
        
        # Retrieve user and check field state
        updated_user = self.repo.get_by_email(email)
        self.assertIsNotNone(updated_user.account_locked_until)
        
        # Test that authenticate raises lock error instantly now
        with self.assertRaises(BusinessRuleViolationError) as ctx_locked:
            self.service.authenticate(email, "AnyPassword")
        self.assertIn("locked", str(ctx_locked.exception).lower())

    def test_role_permissions_rbac_matrix(self) -> None:
        """Verifies RBAC rules against the official matrix."""
        # Customer permissions
        self.assertTrue(AuthenticationService.verify_role_permission("customer", "quotation"))
        self.assertTrue(AuthenticationService.verify_role_permission("customer", "claims"))
        self.assertTrue(AuthenticationService.verify_role_permission("customer", "chatbot"))
        self.assertFalse(AuthenticationService.verify_role_permission("customer", "dashboard"))
        
        # Claims Officer permissions
        self.assertTrue(AuthenticationService.verify_role_permission("claims_officer", "claims"))
        self.assertTrue(AuthenticationService.verify_role_permission("claims_officer", "dashboard"))
        self.assertTrue(AuthenticationService.verify_role_permission("claims_officer", "manager_ai_readonly"))
        self.assertFalse(AuthenticationService.verify_role_permission("claims_officer", "manager_ai_write"))
        self.assertFalse(AuthenticationService.verify_role_permission("claims_officer", "quotation"))

        # Underwriter permissions
        self.assertTrue(AuthenticationService.verify_role_permission("underwriter", "quotation"))
        self.assertTrue(AuthenticationService.verify_role_permission("underwriter", "dashboard"))
        self.assertTrue(AuthenticationService.verify_role_permission("underwriter", "chatbot"))
        self.assertFalse(AuthenticationService.verify_role_permission("underwriter", "claims"))

        # Manager permissions
        self.assertTrue(AuthenticationService.verify_role_permission("manager", "dashboard"))
        self.assertTrue(AuthenticationService.verify_role_permission("manager", "manager_ai"))
        self.assertTrue(AuthenticationService.verify_role_permission("manager", "reports"))
        self.assertFalse(AuthenticationService.verify_role_permission("manager", "claims"))

        # Admin / Administrator permissions (always allowed)
        self.assertTrue(AuthenticationService.verify_role_permission("admin", "claims"))
        self.assertTrue(AuthenticationService.verify_role_permission("administrator", "dashboard"))
