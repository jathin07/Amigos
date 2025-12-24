from app import create_app, db
from app.models import Destination

app = create_app()
app.app_context().push()

# Add example destinations
dest1 = Destination(name="Ooty", description="A beautiful hill station.", image_url="ooty.jpg", tags="nature,hills")
dest2 = Destination(name="Kodaikanal", description="The princess of hill stations.", image_url="kodaikanal.jpg", tags="lake,green")
dest3 = Destination(name="Munnar", description="Lush tea gardens and cool weather.", image_url="munnar.jpg", tags="tea,kerala")

# Add to DB
db.session.add_all([dest1, dest2, dest3])
db.session.commit()

print("Seeded destinations successfully!")
