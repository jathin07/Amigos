from app.core.extensions import db
from app.modules.master.payment_method.models import PaymentMethod
import uuid

def seed():
    data = [
        {'name':'Cash','code':'CASH','display_order':1},
        {'name':'UPI','code':'UPI','display_order':2},
        {'name':'Credit Card','code':'CREDIT_CARD','display_order':3},
        {'name':'Debit Card','code':'DEBIT_CARD','display_order':4},
        {'name':'Bank Transfer','code':'BANK_TRANSFER','display_order':5},
        {'name':'Cheque','code':'CHEQUE','display_order':6},
        {'name':'Wallet','code':'WALLET','display_order':7}
    ]
    for item in data:
        if not PaymentMethod.query.filter_by(code=item['code']).first():
            entity = PaymentMethod(
                id=uuid.uuid4(),
                **item,
                is_active=True,
                created_by=None,
                updated_by=None
            )
            db.session.add(entity)
    db.session.commit()
    print("Payment Methods seeded.")
