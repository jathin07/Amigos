from app.core.extensions import db
from app.modules.master.cancellation_policy.models import CancellationPolicy
import uuid

def seed():
    data = [
        {'name':'No Refund','code':'NO_REFUND','refund_percentage':0,'days_before_travel':0,'description':'Cancelled on day of travel - no refund'},
        {'name':'25% Refund','code':'REFUND_25','refund_percentage':25,'days_before_travel':3,'description':'Cancelled 3-6 days before - 25% refund'},
        {'name':'50% Refund','code':'REFUND_50','refund_percentage':50,'days_before_travel':7,'description':'Cancelled 7-14 days before - 50% refund'},
        {'name':'75% Refund','code':'REFUND_75','refund_percentage':75,'days_before_travel':15,'description':'Cancelled 15-29 days before - 75% refund'},
        {'name':'Full Refund','code':'FULL_REFUND','refund_percentage':100,'days_before_travel':30,'description':'Cancelled 30+ days before - full refund'}
    ]
    for item in data:
        if not CancellationPolicy.query.filter_by(code=item['code']).first():
            entity = CancellationPolicy(
                id=uuid.uuid4(),
                **item,
                is_active=True,
                created_by=None,
                updated_by=None
            )
            db.session.add(entity)
    db.session.commit()
    print("Cancellation Policies seeded.")
