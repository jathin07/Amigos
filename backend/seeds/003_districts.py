"""
Seed 003 - Districts

Run: python manage.py seed
  or directly: python seeds/003_districts.py
"""

DISTRICTS_DATA = {
    # India - Kerala
    "KL": [
        {"name": "Thiruvananthapuram", "code": "TVM", "display_order": 1},
        {"name": "Ernakulam",          "code": "EKM", "display_order": 2},
        {"name": "Kozhikode",          "code": "CCJ", "display_order": 3},
        {"name": "Idukki",             "code": "IDK", "display_order": 4},
        {"name": "Alappuzha",          "code": "ALP", "display_order": 5},
        {"name": "Thrissur",           "code": "TCR", "display_order": 6},
        {"name": "Wayanad",            "code": "WYD", "display_order": 7},
        {"name": "Palakkad",           "code": "PKD", "display_order": 8},
        {"name": "Kollam",             "code": "KLM", "display_order": 9},
        {"name": "Kannur",             "code": "CNN", "display_order": 10},
    ],
    # India - Tamil Nadu
    "TN": [
        {"name": "Chennai",            "code": "MAA", "display_order": 1},
        {"name": "Coimbatore",         "code": "CBE", "display_order": 2},
        {"name": "Madurai",            "code": "IXM", "display_order": 3},
        {"name": "Ooty (Nilgiris)",    "code": "NLG", "display_order": 4},
    ],
    # India - Maharashtra
    "MH": [
        {"name": "Mumbai City",        "code": "MUM", "display_order": 1},
        {"name": "Pune",               "code": "PNQ", "display_order": 2},
        {"name": "Nashik",             "code": "NSK", "display_order": 3},
        {"name": "Aurangabad",         "code": "IXU", "display_order": 4},
    ],
    # India - Goa
    "GA": [
        {"name": "North Goa",          "code": "NGO", "display_order": 1},
        {"name": "South Goa",          "code": "SGO", "display_order": 2},
    ],
    # India - Rajasthan
    "RJ": [
        {"name": "Jaipur",             "code": "JAI", "display_order": 1},
        {"name": "Udaipur",            "code": "UDR", "display_order": 2},
        {"name": "Jodhpur",            "code": "JDH", "display_order": 3},
        {"name": "Jaisalmer",          "code": "JSM", "display_order": 4},
    ],
    # Sri Lanka - Western Province
    "WP": [
        {"name": "Colombo",            "code": "CMB", "display_order": 1},
        {"name": "Gampaha",            "code": "GMP", "display_order": 2},
        {"name": "Kalutara",           "code": "KLT", "display_order": 3},
    ],
    # USA - New York
    "NY": [
        {"name": "New York County",    "code": "NYC", "display_order": 1},
        {"name": "Kings County",       "code": "KGS", "display_order": 2},
    ],
}


def run(db):
    from app.modules.master.country.models import Country
    from app.modules.master.state.models import State
    from app.modules.master.district.models import District

    created = 0
    skipped = 0
    state_not_found = 0

    for state_code, districts in DISTRICTS_DATA.items():
        state = db.session.query(State).filter_by(code=state_code).first()
        if not state:
            state_not_found += len(districts)
            continue

        for data in districts:
            existing = db.session.query(District).filter_by(
                code=data["code"], state_id=state.id
            ).first()
            if existing:
                skipped += 1
                continue

            district = District(
                name=data["name"],
                code=data["code"],
                state_id=state.id,
                display_order=data.get("display_order", 0),
                is_active=True,
            )
            db.session.add(district)
            created += 1

    db.session.commit()
    print(f"[003_districts] created={created} skipped={skipped} state_not_found={state_not_found}")


if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.core.startup import create_app
    from app.core.extensions import db as _db
    app = create_app("development")
    with app.app_context():
        run(_db)
