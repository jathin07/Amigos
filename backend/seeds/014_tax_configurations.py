from app.core.extensions import db
from app.modules.master.tax_configuration.models import TaxConfiguration
import uuid

def seed():
    data = [
        {'name':'GST 5%','code':'GST_5','tax_rate':5.00,'tax_type':'GST','is_inclusive':False},
        {'name':'GST 12%','code':'GST_12','tax_rate':12.00,'tax_type':'GST','is_inclusive':False},
        {'name':'GST 18%','code':'GST_18','tax_rate':18.00,'tax_type':'GST','is_inclusive':False,'is_default':True},
        {'name':'GST 28%','code':'GST_28','tax_rate':28.00,'tax_type':'GST'},
        {'name':'VAT 5%','code':'VAT_5','tax_rate':5.00,'tax_type':'VAT'},
        {'name':'Service Tax 15%','code':'SVC_TAX','tax_rate':15.00,'tax_type':'SERVICE_TAX'}
    ]
    for item in data:
        if not TaxConfiguration.query.filter_by(code=item['code']).first():
            entity = TaxConfiguration(
                id=uuid.uuid4(),
                **item,
                is_active=True,
                created_by=None,
                updated_by=None
            )
            db.session.add(entity)
    db.session.commit()
    print("Tax Configurations seeded.")
