import logging
from app.core.extensions import db
from app.modules.master.meal_plan.models import MealPlan

def seed_meal_plans():
    items = [{'name': 'Room Only (EP)', 'code': 'EP', 'display_order': 1, 'description': 'European Plan - No meals included'}, {'name': 'Breakfast Only (CP)', 'code': 'CP', 'display_order': 2, 'description': 'Continental Plan - Breakfast included'}, {'name': 'Half Board (MAP)', 'code': 'MAP', 'display_order': 3, 'description': 'Modified American Plan - Breakfast and Dinner'}, {'name': 'Full Board (AP)', 'code': 'AP', 'display_order': 4, 'description': 'American Plan - All three meals'}, {'name': 'All Inclusive (AI)', 'code': 'AI', 'display_order': 5, 'description': 'All meals and selected beverages'}]
    added = 0
    for item in items:
        if not MealPlan.query.filter_by(code=item["code"]).first():
            db.session.add(MealPlan(**item))
            added += 1
    if added > 0:
        db.session.commit()
        logging.info(f"Seeded {added} meal_plans.")
    else:
        logging.info("No new meal_plans to seed.")
