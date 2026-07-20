import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.startup import create_app
from app.infrastructure.persistence.uow import UnitOfWork

try:
    print("Booting App...")
    app = create_app('testing')
    print("App Booted Successfully!")

    with app.app_context():
        print("Testing UoW...")
        uow = UnitOfWork()
        with uow:
            print("Inside UoW Context Manager")
            # We don't have db models bound to this test db yet, but we can verify it doesn't crash
            uow.commit()
        print("UoW Test Passed!")
        
        # Test health route
        print("Testing Health Route...")
        client = app.test_client()
        response = client.get('/api/v1/health')
        print(f"Health Response Status: {response.status_code}")
        print(f"Health Response JSON: {response.get_json()}")
        
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
