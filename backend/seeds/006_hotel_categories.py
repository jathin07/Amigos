import logging
from app.core.extensions import db
from app.modules.master.hotel_category.models import HotelCategory

def seed_hotel_categories():
    items = [{'name': 'Budget', 'code': 'BUDGET_H', 'display_order': 1}, {'name': 'Standard', 'code': 'STANDARD', 'display_order': 2}, {'name': 'Deluxe', 'code': 'DELUXE', 'display_order': 3}, {'name': 'Luxury', 'code': 'LUXURY_H', 'display_order': 4}, {'name': 'Boutique', 'code': 'BOUTIQUE', 'display_order': 5}, {'name': 'Resort', 'code': 'RESORT', 'display_order': 6}, {'name': 'Homestay', 'code': 'HOMESTAY', 'display_order': 7}, {'name': 'Hostel', 'code': 'HOSTEL', 'display_order': 8}]
    added = 0
    for item in items:
        if not HotelCategory.query.filter_by(code=item["code"]).first():
            db.session.add(HotelCategory(**item))
            added += 1
    if added > 0:
        db.session.commit()
        logging.info(f"Seeded {added} hotel_categories.")
    else:
        logging.info("No new hotel_categories to seed.")
