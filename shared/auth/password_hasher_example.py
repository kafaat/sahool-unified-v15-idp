"""
Password Hasher Integration Examples
أمثلة لدمج معالج كلمات المرور

This file contains complete, working examples of how to integrate
the new Argon2id password hasher into your application.

يحتوي هذا الملف على أمثلة كاملة وعاملة لكيفية دمج
معالج كلمات المرور Argon2id الجديد في تطبيقك.
"""

# ========================================
# Example 1: Basic Usage
# مثال 1: الاستخدام الأساسي
# ========================================

from shared.auth.password_hasher import hash_password, verify_password


def basic_usage_example():
    """Basic password hashing and verification"""

    # Hash a password
    password = "MySecurePassword123!"
    hashed = hash_password(password)
    print(f"Hashed password: {hashed[:50]}...")

    # Verify correct password
    is_valid, needs_rehash = verify_password(password, hashed)
    print(f"Password valid: {is_valid}")
    print(f"Needs rehash: {needs_rehash}")

    # Verify incorrect password
    is_valid, needs_rehash = verify_password("WrongPassword", hashed)
    print(f"Wrong password valid: {is_valid}")


# ========================================
# Example 2: User Registration
# مثال 2: تسجيل مستخدم جديد
# ========================================

from datetime import datetime


class UserRegistrationService:
    """Service for registering new users"""

    def __init__(self, db_session):
        self.db = db_session

    async def register_user(self, email: str, password: str, name: str) -> dict:
        """
        Register a new user with Argon2id password

        Args:
            email: User's email
            password: Plain text password
            name: User's name

        Returns:
            Created user data
        """
        # Validate password strength (implement your own validation)
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        # Hash password with Argon2id
        password_hash = hash_password(password)

        # Create user record
        user = {
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "password_algorithm": "argon2id",
            "password_needs_migration": False,
            "created_at": datetime.utcnow(),
            "is_active": True,
        }

        # Save to database (pseudo-code)
        # user_id = await self.db.users.insert(user)

        return user


# ========================================
# Example 3: User Login with Migration
# مثال 3: تسجيل دخول مع الترحيل
# ========================================

from shared.auth.password_migration_helper import (
    PasswordMigrationHelper,
)


class SQLAlchemyUserRepository:
    """Example repository implementation with SQLAlchemy"""

    def __init__(self, db_session):
        self.db = db_session

    def get_user_by_email(self, email: str) -> dict | None:
        """Get user by email"""
        # Pseudo-code - replace with actual SQLAlchemy query
        user = self.db.query(User).filter(User.email == email).first()

        if user:
            return {
                "id": str(user.id),
                "email": user.email,
                "password_hash": user.password_hash,
                "password_algorithm": getattr(user, "password_algorithm", "bcrypt"),
                "password_needs_migration": getattr(user, "password_needs_migration", True),
            }
        return None

    def update_password_hash(self, user_id: str, password_hash: str) -> bool:
        """Update user's password hash"""
        # Pseudo-code
        result = (
            self.db.query(User)
            .filter(User.id == user_id)
            .update(
                {
                    "password_hash": password_hash,
                    "password_algorithm": "argon2id",
                    "password_needs_migration": False,
                    "updated_at": datetime.utcnow(),
                }
            )
        )
        self.db.commit()
        return result > 0

    def mark_password_migrated(self, user_id: str) -> bool:
        """Mark user's password as migrated"""
        result = (
            self.db.query(User)
            .filter(User.id == user_id)
            .update({"password_needs_migration": False, "updated_at": datetime.utcnow()})
        )
        self.db.commit()
        return result > 0


class LoginService:
    """Service for user login with automatic password migration"""

    def __init__(self, db_session, jwt_service):
        self.db = db_session
        self.jwt_service = jwt_service
        self.user_repo = SQLAlchemyUserRepository(db_session)
        self.migration_helper = PasswordMigrationHelper(self.user_repo)

    async def login(self, email: str, password: str) -> dict:
        """
        Login user with automatic password migration

        Args:
            email: User's email
            password: Plain text password

        Returns:
            Access token and user info

        Raises:
            ValueError: If credentials are invalid
        """
        # Authenticate and check for migration
        result = await self.migration_helper.authenticate_and_migrate(email, password)

        if not result.success:
            raise ValueError(result.error_message or "Invalid credentials")

        # If password needs migration, update it
        if result.needs_password_update and result.new_password_hash:
            await self.migration_helper.complete_migration(result.user_id, result.new_password_hash)
            print(f"✓ Password migrated to Argon2id for user {result.user_id}")

        # Generate JWT token
        access_token = self.jwt_service.create_token(result.user_id)

        return {
            "access_token": access_token,
            "user_id": result.user_id,
            "token_type": "Bearer",
        }


# ========================================
# Example 4: FastAPI Integration
# مثال 4: دمج مع FastAPI
# ========================================

"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from shared.auth.password_hasher import hash_password
from shared.auth.password_migration_helper import PasswordMigrationHelper

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user_id: str


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    '''Register a new user'''

    # Check if user exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password with Argon2id
    password_hash = hash_password(request.password)

    # Create user
    user = User(
        email=request.email,
        name=request.name,
        password_hash=password_hash,
        password_algorithm='argon2id',
        password_needs_migration=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate token
    access_token = create_access_token(user.id)

    return LoginResponse(
        access_token=access_token,
        user_id=str(user.id)
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    '''Login with email and password'''

    # Create repository and helper
    user_repo = SQLAlchemyUserRepository(db)
    helper = PasswordMigrationHelper(user_repo)

    # Authenticate with migration
    result = await helper.authenticate_and_migrate(
        form_data.username,  # email
        form_data.password
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Complete migration if needed
    if result.needs_password_update and result.new_password_hash:
        await helper.complete_migration(
            result.user_id,
            result.new_password_hash
        )

    # Generate token
    access_token = create_access_token(result.user_id)

    return LoginResponse(
        access_token=access_token,
        user_id=result.user_id
    )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    '''Change user password'''

    # Verify current password
    is_valid, _ = verify_password(current_password, current_user.password_hash)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid current password"
        )

    # Hash new password with Argon2id
    new_hash = hash_password(new_password)

    # Update password
    current_user.password_hash = new_hash
    current_user.password_algorithm = 'argon2id'
    current_user.password_needs_migration = False
    current_user.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Password updated successfully"}
"""


# ========================================
# Example 5: Batch Migration Script
# مثال 5: سكريبت ترحيل دفعي
# ========================================


def run_batch_migration():
    """
    Example of running batch migration

    This flags all legacy passwords for migration.
    Actual rehashing happens on next login.
    """
    import sys

    sys.path.insert(0, "/home/user/sahool-unified-v15-idp")

    from database.migrations.migrate_passwords_to_argon2 import (
        PasswordMigrator,
        get_database_connection,
    )

    # Get database connection
    conn = get_database_connection()

    try:
        # Create migrator
        migrator = PasswordMigrator(
            conn,
            dry_run=False,  # Set to True for testing
            force=False,  # Set to True to rehash even Argon2id passwords
        )

        # Run migration
        migrator.migrate_all(batch_size=1000)

        print("\n✓ Migration complete!")
        print("Users with legacy passwords will be migrated on next login.")

    finally:
        conn.close()


# ========================================
# Example 6: Monitoring Migration Progress
# مثال 6: مراقبة تقدم الترحيل
# ========================================


def monitor_migration_progress(db_connection):
    """Monitor password migration progress"""

    cursor = db_connection.cursor()

    # Get migration statistics
    cursor.execute("SELECT * FROM password_migration_stats")
    stats = cursor.fetchall()

    print("\n" + "=" * 70)
    print("Password Migration Progress")
    print("=" * 70)

    for row in stats:
        algorithm, count, needs_migration, percentage = row
        print(f"{algorithm:20} | Total: {count:5} | Pending: {needs_migration:5} | {percentage}%")

    print("=" * 70)

    # Get total progress
    cursor.execute(
        """
        SELECT
            COUNT(*) as total_users,
            SUM(CASE WHEN password_needs_migration THEN 1 ELSE 0 END) as pending,
            ROUND(100.0 * SUM(CASE WHEN password_algorithm = 'argon2id' THEN 1 ELSE 0 END) / COUNT(*), 2) as argon2_percentage
        FROM users
        WHERE password_hash IS NOT NULL
    """
    )

    total, pending, argon2_pct = cursor.fetchone()

    print(f"\nTotal users:           {total}")
    print(f"Pending migration:     {pending}")
    print(f"Using Argon2id:        {argon2_pct}%")
    print()

    cursor.close()


# ========================================
# Example 7: Testing Password Algorithms
# مثال 7: اختبار خوارزميات كلمات المرور
# ========================================


def test_all_algorithms():
    """Test hashing and verification for all supported algorithms"""

    import hashlib
    import secrets

    from shared.auth.password_hasher import (
        ARGON2_AVAILABLE,
        BCRYPT_AVAILABLE,
        PasswordHasher,
    )

    hasher = PasswordHasher()
    test_password = "TestPassword123!"

    print("\n" + "=" * 70)
    print("Password Algorithm Tests")
    print("=" * 70)

    # Test Argon2id
    if ARGON2_AVAILABLE:
        print("\n1. Testing Argon2id...")
        argon2_hash = hasher.hash_password(test_password)
        is_valid, needs_rehash = hasher.verify_password(test_password, argon2_hash)
        print(f"   Hash: {argon2_hash[:50]}...")
        print(f"   Verification: {'✓ PASS' if is_valid else '✗ FAIL'}")
        print(f"   Needs rehash: {needs_rehash}")
    else:
        print("\n1. Argon2id: NOT AVAILABLE (install argon2-cffi)")

    # Test bcrypt compatibility
    if BCRYPT_AVAILABLE:
        print("\n2. Testing bcrypt (legacy)...")
        import bcrypt

        bcrypt_hash = bcrypt.hashpw(
            test_password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")
        is_valid, needs_rehash = hasher.verify_password(test_password, bcrypt_hash)
        print(f"   Hash: {bcrypt_hash[:50]}...")
        print(f"   Verification: {'✓ PASS' if is_valid else '✗ FAIL'}")
        print(f"   Needs rehash: {needs_rehash}")
    else:
        print("\n2. bcrypt: NOT AVAILABLE (install bcrypt)")

    # Test PBKDF2 compatibility
    print("\n3. Testing PBKDF2 (legacy)...")
    salt = secrets.token_bytes(32)
    hashed = hashlib.pbkdf2_hmac("sha256", test_password.encode("utf-8"), salt, 100_000, 32)
    pbkdf2_hash = f"{salt.hex()}${hashed.hex()}"
    is_valid, needs_rehash = hasher.verify_password(test_password, pbkdf2_hash)
    print(f"   Hash: {pbkdf2_hash[:50]}...")
    print(f"   Verification: {'✓ PASS' if is_valid else '✗ FAIL'}")
    print(f"   Needs rehash: {needs_rehash}")

    print("\n" + "=" * 70)


# ========================================
# Main Function
# الدالة الرئيسية
# ========================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SAHOOL Password Hasher - Integration Examples")
    print("=" * 70)

    # Run basic usage example
    print("\n--- Basic Usage ---")
    basic_usage_example()

    # Test all algorithms
    test_all_algorithms()

    print("\n" + "=" * 70)
    print("Examples completed!")
    print("\nFor more examples, see:")
    print("  - shared/auth/password_migration_helper.py")
    print("  - shared/auth/PASSWORD_MIGRATION_README.md")
    print("=" * 70 + "\n")
