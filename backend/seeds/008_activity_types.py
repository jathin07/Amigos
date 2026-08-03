import logging
from app.core.extensions import db
from app.modules.master.activity_type.models import ActivityType

def seed_activity_types():
    items = [{'name': 'Trekking', 'code': 'TREKKING', 'display_order': 1}, {'name': 'Water Sports', 'code': 'WATER_SPORTS', 'display_order': 2}, {'name': 'Wildlife Safari', 'code': 'WILDLIFE_SAFARI', 'display_order': 3}, {'name': 'Cultural Tour', 'code': 'CULTURAL_TOUR', 'display_order': 4}, {'name': 'Adventure Sports', 'code': 'ADVENTURE_SPORTS', 'display_order': 5}, {'name': 'Sightseeing', 'code': 'SIGHTSEEING', 'display_order': 6}, {'name': 'Cruise', 'code': 'CRUISE', 'display_order': 7}, {'name': 'Spa & Wellness', 'code': 'SPA_WELLNESS', 'display_order': 8}, {'name': 'Photography Tour', 'code': 'PHOTO_TOUR', 'display_order': 9}, {'name': 'Cooking Class', 'code': 'COOKING_CLASS', 'display_order': 10}]
    added = 0
    for item in items:
        if not ActivityType.query.filter_by(code=item["code"]).first():
            db.session.add(ActivityType(**item))
            added += 1
    if added > 0:
        db.session.commit()
        logging.info(f"Seeded {added} activity_types.")
    else:
        logging.info("No new activity_types to seed.")
