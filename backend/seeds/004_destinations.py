"""
Seed 004 - Destinations

Hierarchy: Country → State → District → Destination

Run: python manage.py seed
  or directly: python seeds/004_destinations.py
"""

# fmt: {country_code: {state_code: {district_code: [destinations]}}}
DESTINATIONS_DATA = {
    "IN": {
        "KL": {
            "IDK": [
                {"name": "Munnar",    "code": "MUN",  "slug": "munnar",    "display_order": 1,
                 "description": "Scenic hill station famous for tea plantations and misty valleys."},
                {"name": "Thekkady", "code": "THK",  "slug": "thekkady",  "display_order": 2,
                 "description": "Gateway to Periyar Wildlife Sanctuary."},
                {"name": "Vagamon",  "code": "VGM",  "slug": "vagamon",   "display_order": 3,
                 "description": "Serene meadows and pine forests."},
            ],
            "EKM": [
                {"name": "Kochi",     "code": "KOCHI", "slug": "kochi",     "display_order": 1,
                 "description": "Historical port city, Queen of the Arabian Sea."},
                {"name": "Fort Kochi","code": "FTKOC", "slug": "fort-kochi","display_order": 2,
                 "description": "Heritage quarter with colonial architecture and Chinese fishing nets."},
            ],
            "ALP": [
                {"name": "Alleppey",  "code": "ALP",   "slug": "alleppey",  "display_order": 1,
                 "description": "Venice of the East — backwaters, houseboats, and coir villages."},
                {"name": "Kumarakom","code": "KMK",   "slug": "kumarakom", "display_order": 2,
                 "description": "Lake-side bird sanctuary and luxury backwater resort zone."},
            ],
            "WYD": [
                {"name": "Wayanad",   "code": "WYD-D", "slug": "wayanad",   "display_order": 1,
                 "description": "Coffee-clad hills, tribal heritage, and wildlife reserves."},
            ],
            "CCJ": [
                {"name": "Kozhikode","code": "CCJ-D", "slug": "kozhikode", "display_order": 1,
                 "description": "Calicut — ancient spice trading port on the Malabar coast."},
            ],
        },
        "TN": {
            "MAA": [
                {"name": "Chennai",   "code": "CHN",  "slug": "chennai",   "display_order": 1,
                 "description": "Capital city, gateway to Tamil Nadu."},
                {"name": "Mahabalipuram", "code": "MBP", "slug": "mahabalipuram", "display_order": 2,
                 "description": "UNESCO Shore Temple and rock-cut sculptures."},
            ],
            "NLG": [
                {"name": "Ooty",      "code": "OOT",  "slug": "ooty",      "display_order": 1,
                 "description": "Queen of Hill Stations in the Nilgiris."},
                {"name": "Coonoor",   "code": "CON",  "slug": "coonoor",   "display_order": 2,
                 "description": "Tea estates and colonial-era bungalows near Ooty."},
            ],
        },
        "MH": {
            "MUM": [
                {"name": "Mumbai",    "code": "BOM",  "slug": "mumbai",    "display_order": 1,
                 "description": "City of Dreams, financial capital of India."},
            ],
            "PNQ": [
                {"name": "Pune",      "code": "PNE",  "slug": "pune",      "display_order": 1,
                 "description": "Oxford of the East and IT hub of Maharashtra."},
            ],
        },
        "RJ": {
            "JAI": [
                {"name": "Jaipur",    "code": "JAI-D","slug": "jaipur",    "display_order": 1,
                 "description": "Pink City — forts, palaces, and vibrant bazaars."},
            ],
            "UDR": [
                {"name": "Udaipur",   "code": "UDR-D","slug": "udaipur",   "display_order": 1,
                 "description": "City of Lakes and romantic palaces."},
            ],
            "JSM": [
                {"name": "Jaisalmer", "code": "JSM-D","slug": "jaisalmer", "display_order": 1,
                 "description": "Golden City — desert forts and camel safaris."},
            ],
        },
    },
    "LK": {
        "WP": {
            "CMB": [
                {"name": "Colombo",   "code": "CLMB", "slug": "colombo",   "display_order": 1,
                 "description": "Capital and largest city of Sri Lanka."},
            ],
        },
    },
}


def run(db):
    from app.modules.master.country.models import Country
    from app.modules.master.state.models import State
    from app.modules.master.district.models import District
    from app.modules.master.destination.models import Destination

    created = 0
    skipped = 0
    not_found = 0

    for country_code, states in DESTINATIONS_DATA.items():
        country = db.session.query(Country).filter_by(code=country_code).first()
        if not country:
            count = sum(len(d) for districts in states.values() for d in districts.values())
            not_found += count
            continue

        for state_code, districts in states.items():
            state = db.session.query(State).filter_by(code=state_code, country_id=country.id).first()
            if not state:
                count = sum(len(d) for d in districts.values())
                not_found += count
                continue

            for district_code, destinations in districts.items():
                district = db.session.query(District).filter_by(code=district_code, state_id=state.id).first()
                if not district:
                    not_found += len(destinations)
                    continue

                for data in destinations:
                    existing = db.session.query(Destination).filter_by(code=data["code"]).first()
                    if existing:
                        skipped += 1
                        continue

                    dest = Destination(
                        name          = data["name"],
                        code          = data["code"],
                        slug          = data["slug"],
                        description   = data.get("description"),
                        country_id    = country.id,
                        state_id      = state.id,
                        district_id   = district.id,
                        display_order = data.get("display_order", 0),
                        is_active     = True,
                    )
                    db.session.add(dest)
                    created += 1

    db.session.commit()
    print(f"[004_destinations] created={created} skipped={skipped} not_found={not_found}")


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.core.startup import create_app
    from app.core.extensions import db as _db
    app = create_app("development")
    with app.app_context():
        run(_db)
