#!/usr/bin/python3
"""Defines the Place class and the place_amenity association table."""
from os import getenv
from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel

place_amenity = Table(
    "place_amenity", Base.metadata,
    Column("place_id", String(60), ForeignKey("places.id"),
           primary_key=True, nullable=False),
    Column("amenity_id", String(60), ForeignKey("amenities.id"),
           primary_key=True, nullable=False))


class Place(BaseModel, Base):
    """Represent a place to rent."""

    __tablename__ = "places"
    city_id = Column(String(60), ForeignKey("cities.id"), nullable=False)
    user_id = Column(String(60), ForeignKey("users.id"), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(String(1024), nullable=True)
    number_rooms = Column(Integer, nullable=False, default=0)
    number_bathrooms = Column(Integer, nullable=False, default=0)
    max_guest = Column(Integer, nullable=False, default=0)
    price_by_night = Column(Integer, nullable=False, default=0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    if getenv("HBNB_TYPE_STORAGE") == "db":
        reviews = relationship("Review", backref="place",
                               cascade="all, delete")
        amenities = relationship("Amenity", secondary=place_amenity,
                                 viewonly=False,
                                 back_populates="place_amenities")
    else:
        amenity_ids = []

        @property
        def reviews(self):
            """Return the list of Review instances linked to this Place."""
            import models
            from models.review import Review
            return [review for review in models.storage.all(Review).values()
                    if review.place_id == self.id]

        @property
        def amenities(self):
            """Return the list of Amenity instances in amenity_ids."""
            import models
            from models.amenity import Amenity
            found = models.storage.all(Amenity)
            return [found["Amenity.{}".format(i)] for i in self.amenity_ids
                    if "Amenity.{}".format(i) in found]

        @amenities.setter
        def amenities(self, obj):
            """Add the id of an Amenity to amenity_ids, ignore other types."""
            from models.amenity import Amenity
            if isinstance(obj, Amenity):
                if "amenity_ids" not in self.__dict__:
                    self.amenity_ids = []
                if obj.id not in self.amenity_ids:
                    self.amenity_ids.append(obj.id)
