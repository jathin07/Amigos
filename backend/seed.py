from app.core.startup import create_app
from app.core.extensions import db
from app.models import Package, PackageDestination, Destination




def seed_destinations():

    places_to_seed = [

        # -------------------------
        # Tamil Nadu
        # -------------------------

        {
            "name": "Ooty",
            "state": "Tamil Nadu",
            "description": "A beautiful hill station in the Nilgiris.",
            "image_url": "ooty.jpg",
            "tags": "hills,nature,tea"
        },
        {
            "name": "Kodaikanal",
            "state": "Tamil Nadu",
            "description": "The princess of hill stations.",
            "image_url": "kodaikanal.jpg",
            "tags": "hills,lake,nature"
        },
        {
            "name": "Valparai",
            "state": "Tamil Nadu",
            "description": "Tea estates and wildlife in the Western Ghats.",
            "image_url": "valparai.jpg",
            "tags": "tea,wildlife,hills"
        },
        {
            "name": "Pondicherry",
            "state": "Tamil Nadu",
            "description": "French colonial town with beaches.",
            "image_url": "pondicherry.jpg",
            "tags": "beach,heritage"
        },

        # -------------------------
        # Karnataka
        # -------------------------

        {
            "name": "Coorg",
            "state": "Karnataka",
            "description": "Coffee plantations and misty hills.",
            "image_url": "coorg.jpg",
            "tags": "coffee,hills"
        },
        {
            "name": "Gokarna",
            "state": "Karnataka",
            "description": "Pristine beaches and temple town.",
            "image_url": "gokarna.jpg",
            "tags": "beach,trek"
        },
        {
            "name": "Dandeli",
            "state": "Karnataka",
            "description": "River rafting and jungle adventure.",
            "image_url": "dandeli.jpg",
            "tags": "rafting,adventure"
        },
        {
            "name": "Chikmagalur",
            "state": "Karnataka",
            "description": "Coffee hills and scenic viewpoints.",
            "image_url": "chikmagalur.jpg",
            "tags": "coffee,hills"
        },
        {
            "name": "Murudeshwar",
            "state": "Karnataka",
            "description": "Famous Shiva statue near Arabian Sea.",
            "image_url": "murudeshwar.jpg",
            "tags": "temple,beach"
        },

        # -------------------------
        # Kerala
        # -------------------------

        {
            "name": "Munnar",
            "state": "Kerala",
            "description": "Tea plantations and cool climate.",
            "image_url": "munnar.jpg",
            "tags": "tea,hills"
        },
        {
            "name": "Alleppey",
            "state": "Kerala",
            "description": "Backwaters and houseboat stays.",
            "image_url": "allepey.jpg",
            "tags": "backwaters,houseboat"
        },
        {
            "name": "Wayanad",
            "state": "Kerala",
            "description": "Waterfalls, forests and wildlife.",
            "image_url": "wayanad.jpg",
            "tags": "forest,wildlife"
        },
        {
            "name": "Idukki",
            "state": "Kerala",
            "description": "Mountains and the famous arch dam.",
            "image_url": "idukki.jpg",
            "tags": "dam,hills"
        },
        {
            "name": "Kollukumalai",
            "state": "Kerala",
            "description": "Highest tea plantation in the world.",
            "image_url": "kollukumalai.jpg",
            "tags": "tea,sunrise"
        },
        {
            "name": "Athirappilly",
            "state": "Kerala",
            "description": "The Niagara of India waterfall.",
            "image_url": "athirappily.jpg",
            "tags": "waterfall,nature"
        }
    ]

    # Clear previous data (dev only)
    Destination.query.delete()

    for item in places_to_seed:

        destination = Destination(
            name=item["name"],
            state=item["state"],
            description=item["description"],
            image_url=item["image_url"],
            tags=item["tags"]
        )

        db.session.add(destination)

    db.session.commit()

    print("✅ Destinations seeded successfully")

def seed_packages():

    Package.query.delete()

    pkg1 = Package(
        title="Dandeli & Gokarna Combo",
        description="Beach trekking in Gokarna and river rafting in Dandeli.",
        duration_days=3,
        duration_nights=2,
        price_per_person=4800,
        thumbnail_url="/images/places/dandeli.jpg",
        highlights="""
Rain Dance with DJ Music
3 Water activities (Kayaking, Boating, Zorbing)
5km Gokarna Beach Trekking
Night Fire Camp with Music
"""
    )

    db.session.add(pkg1)
    db.session.commit()

    # link destinations
    dandeli = Destination.query.filter_by(name="Dandeli").first()
    gokarna = Destination.query.filter_by(name="Gokarna").first()

    links = [
        PackageDestination(package_id=pkg1.id, destination_id=dandeli.id),
        PackageDestination(package_id=pkg1.id, destination_id=gokarna.id),
    ]

    db.session.add_all(links)
    db.session.commit()

    print("✅ Packages seeded")


def run_seed():

    seed_destinations()
    seed_packages()

    print("🌱 Database seeding complete")

# Run Seeder
app = create_app()

with app.app_context():
    run_seed()