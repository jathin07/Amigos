from app.core.extensions import db
from app.modules.master.currency.models import Currency
import uuid

def seed():
    data = [
        {'name':'Indian Rupee','code':'INR','symbol':'₹','is_default':True,'display_order':1},
        {'name':'US Dollar','code':'USD','symbol':'$','display_order':2},
        {'name':'Euro','code':'EUR','symbol':'€','display_order':3},
        {'name':'UAE Dirham','code':'AED','symbol':'AED','display_order':4},
        {'name':'Singapore Dollar','code':'SGD','symbol':'S$','display_order':5},
        {'name':'British Pound','code':'GBP','symbol':'£','display_order':6},
        {'name':'Thai Baht','code':'THB','symbol':'฿','display_order':7}
    ]
    for item in data:
        if not Currency.query.filter_by(code=item['code']).first():
            entity = Currency(
                id=uuid.uuid4(),
                **item,
                is_active=True,
                created_by=None,
                updated_by=None
            )
            db.session.add(entity)
    db.session.commit()
    print("Currencies seeded.")
