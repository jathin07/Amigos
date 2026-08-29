import os
import sys
import uuid

# Ensure backend root is in search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.startup import create_app
from app.core.extensions import db, bcrypt
from app.models import Role, TeamMember, UserAccount

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    
    print("Creating all tables from scratch...")
    db.create_all()
    
    # Create Admin role
    admin_role = Role(
        id=uuid.uuid4(),
        name="Admin",
        code="admin",
        description="Administrative rights across all modules."
    )
    db.session.add(admin_role)
    db.session.flush()
    print("Seeded Admin role.")

    # Create Team Member
    member = TeamMember(
        id=uuid.uuid4(),
        first_name="Test",
        last_name="User",
        display_name="Test User",
        employee_code="TM999",
        official_email="test@example.com",
        designation="Tester",
        phone="1234567890",
        role=admin_role,
        is_active=True
    )
    db.session.add(member)
    db.session.flush()
    print("Seeded Team Member: test@example.com")

    # Create User Account
    user = UserAccount(
        id=uuid.uuid4(),
        username="testuser",
        team_member=member,
        password_hash=bcrypt.generate_password_hash("Password123").decode(),
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    print("Database reset completed successfully! User testuser (test@example.com / Password123) is ready.")
