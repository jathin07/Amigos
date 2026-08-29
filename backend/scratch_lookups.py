from app.core.startup import create_app
from app.models import PaymentType, PaymentMethod
from sqlalchemy import select
from app.core.extensions import db

app = create_app()
with app.app_context():
    pts = db.session.scalars(select(PaymentType)).all()
    pms = db.session.scalars(select(PaymentMethod)).all()
    print("Payment Types:")
    for pt in pts:
        print(f"  id: {pt.id}, code: {pt.code}, name: {pt.name}")
    print("Payment Methods:")
    for pm in pms:
        print(f"  id: {pm.id}, code: {pm.code}, name: {pm.name}")
