

from app.database import Base, engine
from app.models import Product, SearchQuery


Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")
