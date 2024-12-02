# # app/models.py (or wherever your data models are defined)
from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ListField
from datetime import datetime

class VehicleSchedule(Document):
    vehicle_id = StringField(required=True, unique=True)
    entry_time = DateTimeField(required=True)
    trip_time = IntField(required=True)  # in hours
    congestion = IntField(default=0)
    speed = FloatField(default=0.0)  # Current speed in km/h
    location = ListField(FloatField())  # [latitude, longitude]

# from mongoengine import Document, StringField, IntField, FloatField, DateTimeField, ListField



# class VehicleSchedule(Document):
#     """
#     Model to store vehicle schedule details.
#     """
#     vehicle_id = StringField(required=True, unique=True)
#     entry_time = DateTimeField(required=True)
#     trip_time = IntField(required=True)  # in hours
#     congestion = IntField(default=0)  # Congestion level (e.g., scale of 0-5)
#     speed = FloatField(default=0.0)  # Current speed in km/h
#     location = ListField(FloatField())  # [latitude, longitude]
#     created_at = DateTimeField(default=datetime.now)  # Timestamp for record creation
#     updated_at = DateTimeField(default=datetime.now)  # Timestamp for record updates



class Driver(Document):
    driver_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    email = StringField(required=True)
    phone = StringField(required=True)
    vehicle_id = StringField(required=True)
    qr_code = StringField(required=True)
    qr_code_image = StringField()  # Add this field for storing the Base64 QR code image
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)


class Trip(Document):
    driver_id = StringField(required=True)
    vehicle_id = StringField(required=True)
    entry_time = DateTimeField(required=True)
    trip_time = IntField()
    congestion = IntField()
    speed = ListField(FloatField())
    locations = ListField(FloatField())
    status = StringField()
    end_time = DateTimeField()