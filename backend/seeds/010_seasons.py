from app.core.extensions import db
from app.modules.master.season.models import Season
import uuid

def seed():
    data = [
        {'name':'Peak Season','code':'PEAK','display_order':1,'description':'Oct-Mar — Best weather, highest demand'},
        {'name':'Off Season','code':'OFF','display_order':2,'description':'Apr-Jun — Hot/humid, lowest rates'},
        {'name':'Shoulder Season','code':'SHOULDER','display_order':3,'description':'Jul-Sep — Monsoon, moderate rates'},
        {'name':'Festival Season','code':'FESTIVAL','display_order':4,'description':'Nov-Jan — Festive periods, special pricing'},
        {'name':'Summer Season','code':'SUMMER','display_order':5,'description':'Apr-Jun — School holidays peak'}
    ]
    for item in data:
        if not Season.query.filter_by(code=item['code']).first():
            entity = Season(
                id=uuid.uuid4(),
                **item,
                is_active=True,
                created_by=None,
                updated_by=None
            )
            db.session.add(entity)
    db.session.commit()
    print("Seasons seeded.")
