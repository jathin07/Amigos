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
    # 1. Verify or create Admin role
    admin_role = Role.query.filter_by(code="admin").first()
    if not admin_role:
        admin_role = Role(
            id=uuid.uuid4(),
            name="Admin",
            code="admin",
            description="Administrative rights across all modules."
        )
        db.session.add(admin_role)
        db.session.flush()
        print("Created Admin role.")
    else:
        print("Admin role already exists.")

    # 2. Verify or create Team Member
    member = TeamMember.query.filter_by(official_email="test@example.com").first()
    if not member:
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
        print("Created Team Member: test@example.com")
    else:
        member.role = admin_role
        print("Linked existing Team Member to Admin role.")

    # 3. Verify or create User Account
    user = UserAccount.query.filter_by(username="testuser").first()
    if not user:
        user = UserAccount(
            id=uuid.uuid4(),
            username="testuser",
            team_member=member,
            password_hash=bcrypt.generate_password_hash("Password123").decode(),
            is_active=True
        )
        db.session.add(user)
        print("Created User Account: username=testuser, password=Password123")
    else:
        user.team_member = member
        user.password_hash = bcrypt.generate_password_hash("Password123").decode()
        print("Updated User Account password to Password123")

    db.session.commit()
    print("Database seeding verification complete! User account testuser (test@example.com / Password123) is ready.")
