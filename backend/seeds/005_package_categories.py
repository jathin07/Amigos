import logging
from app.core.extensions import db
from app.modules.master.package_category.models import PackageCategory

def seed_package_categories():
    items = [{'name': 'Adventure', 'code': 'ADVENTURE', 'display_order': 1}, {'name': 'Honeymoon', 'code': 'HONEYMOON', 'display_order': 2}, {'name': 'Family', 'code': 'FAMILY', 'display_order': 3}, {'name': 'Pilgrimage', 'code': 'PILGRIMAGE', 'display_order': 4}, {'name': 'Wildlife', 'code': 'WILDLIFE', 'display_order': 5}, {'name': 'Beach', 'code': 'BEACH', 'display_order': 6}, {'name': 'Cultural', 'code': 'CULTURAL', 'display_order': 7}, {'name': 'Luxury', 'code': 'LUXURY', 'display_order': 8}, {'name': 'Budget', 'code': 'BUDGET', 'display_order': 9}, {'name': 'Weekend Getaway', 'code': 'WEEKEND', 'display_order': 10}]
    added = 0
    for item in items:
        if not PackageCategory.query.filter_by(code=item["code"]).first():
            db.session.add(PackageCategory(**item))
            added += 1
    if added > 0:
        db.session.commit()
        logging.info(f"Seeded {added} package_categories.")
    else:
        logging.info("No new package_categories to seed.")
