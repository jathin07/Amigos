"""
Seed 001 - Countries

Run: python manage.py seed
  or directly: python seeds/001_countries.py
"""

COUNTRIES = [
    {"name": "India",        "code": "IN",  "phone_code": "+91",  "display_order": 1},
    {"name": "Sri Lanka",    "code": "LK",  "phone_code": "+94",  "display_order": 2},
    {"name": "Nepal",        "code": "NP",  "phone_code": "+977", "display_order": 3},
    {"name": "Bhutan",       "code": "BT",  "phone_code": "+975", "display_order": 4},
    {"name": "Maldives",     "code": "MV",  "phone_code": "+960", "display_order": 5},
    {"name": "Singapore",    "code": "SG",  "phone_code": "+65",  "display_order": 6},
    {"name": "Thailand",     "code": "TH",  "phone_code": "+66",  "display_order": 7},
    {"name": "Malaysia",     "code": "MY",  "phone_code": "+60",  "display_order": 8},
    {"name": "UAE",          "code": "AE",  "phone_code": "+971", "display_order": 9},
    {"name": "United Kingdom","code": "GB", "phone_code": "+44",  "display_order": 10},
    {"name": "USA",          "code": "US",  "phone_code": "+1",   "display_order": 11},
    {"name": "Australia",    "code": "AU",  "phone_code": "+61",  "display_order": 12},
]


def run(db):
    from app.modules.master.country.models import Country

    created = 0
    skipped = 0

    for data in COUNTRIES:
        existing = db.session.query(Country).filter_by(code=data["code"]).first()
        if existing:
            skipped += 1
            continue

        country = Country(
            name          = data["name"],
            code          = data["code"],
            phone_code    = data["phone_code"],
            display_order = data["display_order"],
            is_active     = True,
        )
        db.session.add(country)
        created += 1

    db.session.commit()
    print(f"[001_countries] created={created} skipped={skipped}")


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.core.startup import create_app
    from app.core.extensions import db as _db
    app = create_app("development")
    with app.app_context():
        run(_db)
