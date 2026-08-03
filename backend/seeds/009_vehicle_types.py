import logging
from app.core.extensions import db
from app.modules.master.vehicle_type.models import VehicleType

def seed_vehicle_types():
    items = [{'name': 'Sedan', 'code': 'SEDAN', 'display_order': 1}, {'name': 'SUV', 'code': 'SUV', 'display_order': 2}, {'name': 'Tempo Traveller', 'code': 'TEMPO', 'display_order': 3}, {'name': 'Mini Bus', 'code': 'MINI_BUS', 'display_order': 4}, {'name': 'Bus', 'code': 'BUS', 'display_order': 5}, {'name': 'Luxury Coach', 'code': 'LUX_COACH', 'display_order': 6}, {'name': 'Bike', 'code': 'BIKE', 'display_order': 7}, {'name': 'Boat', 'code': 'BOAT', 'display_order': 8}, {'name': 'Auto Rickshaw', 'code': 'AUTO', 'display_order': 9}]
    added = 0
    for item in items:
        if not VehicleType.query.filter_by(code=item["code"]).first():
            db.session.add(VehicleType(**item))
            added += 1
    if added > 0:
        db.session.commit()
        logging.info(f"Seeded {added} vehicle_types.")
    else:
        logging.info("No new vehicle_types to seed.")
