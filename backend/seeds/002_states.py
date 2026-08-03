"""
Seed 002 - States

Run: python manage.py seed
  or directly: python seeds/002_states.py
"""

STATES_DATA = {
    "IN": [
        {"name": "Kerala",         "code": "KL", "display_order": 1},
        {"name": "Tamil Nadu",     "code": "TN", "display_order": 2},
        {"name": "Karnataka",      "code": "KA", "display_order": 3},
        {"name": "Maharashtra",    "code": "MH", "display_order": 4},
        {"name": "Delhi",          "code": "DL", "display_order": 5},
        {"name": "Goa",            "code": "GA", "display_order": 6},
        {"name": "Rajasthan",      "code": "RJ", "display_order": 7},
        {"name": "Gujarat",        "code": "GJ", "display_order": 8},
        {"name": "Uttar Pradesh",  "code": "UP", "display_order": 9},
        {"name": "West Bengal",    "code": "WB", "display_order": 10},
    ],
    "US": [
        {"name": "California",     "code": "CA", "display_order": 1},
        {"name": "New York",       "code": "NY", "display_order": 2},
        {"name": "Texas",          "code": "TX", "display_order": 3},
        {"name": "Florida",        "code": "FL", "display_order": 4},
    ],
    "LK": [
        {"name": "Western Province", "code": "WP", "display_order": 1},
        {"name": "Central Province", "code": "CP", "display_order": 2},
        {"name": "Southern Province","code": "SP", "display_order": 3},
    ]
}


def run(db):
    from app.modules.master.country.models import Country
    from app.modules.master.state.models import State

    created = 0
    skipped = 0
    not_found = 0

    for country_code, states in STATES_DATA.items():
        country = db.session.query(Country).filter_by(code=country_code).first()
        if not country:
            not_found += len(states)
            continue
            
        for data in states:
            existing = db.session.query(State).filter_by(code=data["code"], country_id=country.id).first()
            if existing:
                skipped += 1
                continue

            state = State(
                name          = data["name"],
                code          = data["code"],
                country_id    = country.id,
                display_order = data["display_order"],
                is_active     = True,
            )
            db.session.add(state)
            created += 1

    db.session.commit()
    print(f"[002_states] created={created} skipped={skipped} country_not_found={not_found}")


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.core.startup import create_app
    from app.core.extensions import db as _db
    app = create_app("development")
    with app.app_context():
        run(_db)
