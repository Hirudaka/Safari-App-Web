# app/routes.py
import random
import uuid
from flask import Blueprint, jsonify, current_app, request
from flask_cors import cross_origin
import qrcode
from io import BytesIO
from base64 import b64encode
from app.models import Driver
from .genetic_algorithm import run_genetic_algorithm
from datetime import datetime
from bson import ObjectId

main = Blueprint('main', __name__)




# @main.route('/api/schedule', methods=['GET'])
# def get_schedule():
#     # Fetch driver and vehicle data from the database
#     drivers = current_app.mongo_db['drivers'].find()
#     vehicles = current_app.mongo_db['vehicles'].find()
    
#     # Now run the genetic algorithm with the fetched data
#     schedule = run_genetic_algorithm(drivers, vehicles)
    
#     # Save the optimized schedule to MongoDB
#     current_app.mongo_db.optimized_schedule.insert_one({"schedule": schedule})  
#     return jsonify({'schedule': schedule}), 200


@main.route('/api/schedule', methods=['GET'])
def get_schedule():
    # Run the genetic algorithm
    schedule = run_genetic_algorithm()
    current_app.mongo_db.optimized_schedule.insert_one({"schedule": schedule})  # Save to MongoDB
    return jsonify({'schedule': schedule}), 200

@main.route('/end_trip', methods=['POST'])
def end_trip():
    data = request.get_json()
    driver_id = data.get("driver_id")
    end_time = datetime.now()

    trip = current_app.mongo_db['trips'].find_one({"driver_id": driver_id, "status": "ongoing"})
    if not trip:
        return jsonify({"error": "No ongoing trip found for this driver"}), 400

    current_app.mongo_db['trips'].update_one(
        {"_id": trip["_id"]},
        {"$set": {"status": "completed", "end_time": end_time}}
    )

    return jsonify({"message": "Trip ended", "end_time": end_time}), 200


# @main.route('/start_trip', methods=['POST'])
# def start_trip():
#     data = request.get_json()
#     driver_id = data.get("driver_id")
#     start_time = datetime.now()

#     # Save entry time and initiate tracking in the database
#     current_app.mongo_db['trips'].insert_one({
#         "driver_id": driver_id,
#         "start_time": start_time,
#         "status": "ongoing",
#     })

#     return jsonify({"message": "Trip started", "start_time": start_time}), 200

# @main.route('/end_trip', methods=['POST'])
# def end_trip():
#     data = request.get_json()
#     driver_id = data.get("driver_id")
#     end_time = datetime.now()

#     current_app.mongo_db['trips'].update_one(
#         {"driver_id": driver_id, "status": "ongoing"},
#         {"$set": {"status": "completed", "end_time": end_time}}
#     )

#     return jsonify({"message": "Trip ended", "end_time": end_time}), 200

@main.route('/api/start_trip', methods=['POST'])
def start_trip():
    data = request.get_json()

    # Validate required fields
    driver_id = data.get("driver_id")
    vehicle_id = data.get("vehicle_id")
    if not driver_id or not vehicle_id:
        return jsonify({"error": "Driver ID and Vehicle ID are required"}), 400

    # Default values
    entry_time = datetime.now()  # Current time when the trip starts
    trip_time = data.get("trip_time", 1)  # Default to 1 hour if not provided
    congestion = data.get("congestion", 0)  # Default to 0
    speed = data.get("speed", 0.0)  # Default to 0.0 km/h
    location = data.get("location", [0.0, 0.0])  # Default to [0.0, 0.0]

    # Insert trip details into the MongoDB collection
    trip_data = {
        "driver_id": driver_id,
        "vehicle_id": vehicle_id,
        "entry_time": entry_time,
        "trip_time": trip_time,
        "congestion": congestion,
        "speed": speed,
        "location": location,
        "status": "ongoing"  # Set status to 'ongoing' when trip starts
    }

    # Save to the database
    db = current_app.mongo_db['trips']
    inserted_trip = db.insert_one(trip_data)

    # Add the inserted document ID (convert ObjectId to string for JSON compatibility)
    trip_data["_id"] = str(inserted_trip.inserted_id)

    return jsonify({
        "message": "Trip started successfully.",
        "trip_details": trip_data
    }), 201
 
@main.route('/api/trips', methods=['GET'])
def get_trips():
    """
    Fetch trip details. Optionally filter by driver_id or vehicle_id.
    """
    db = current_app.mongo_db['trips']
    
    # Optional filters
    driver_id = request.args.get('driver_id')
    vehicle_id = request.args.get('vehicle_id')

    # Build the query dynamically based on available filters
    query = {}
    if driver_id:
        query["driver_id"] = driver_id
    if vehicle_id:
        query["vehicle_id"] = vehicle_id

    # Fetch trips matching the query
    trips = list(db.find(query))

    # Convert ObjectId to string for JSON serialization
    for trip in trips:
        trip["_id"] = str(trip["_id"])
        trip["entry_time"] = trip["entry_time"].isoformat()  # Convert datetime to ISO format

    return jsonify({
        "message": "Trips fetched successfully.",
        "trips": trips
    }), 200
   
    # Insert into the database and get the inserted document ID
    inserted_trip = current_app.mongo_db['trips'].insert_one(trip_data)
    trip_data["_id"] = str(inserted_trip.inserted_id)  # Convert ObjectId to string

    return jsonify({
        "message": "Trip started",
        "trip_details": trip_data
    }), 200




@main.route('/register_driver', methods=['POST'])
def register_driver():
    data = request.get_json()

    # Generate a unique driver ID
    driver_id = str(uuid.uuid4())
    qr_code = f"QR-{driver_id}"

    # Generate QR code image
    qr = qrcode.make(qr_code)
    img_byte_arr = BytesIO()
    qr.save(img_byte_arr)
    img_byte_arr = b64encode(img_byte_arr.getvalue()).decode('utf-8')

    try:
        # Save driver details
        new_driver = Driver(
            driver_id=driver_id,
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            vehicle_id=data["vehicle_id"], 
            qr_code=qr_code,
            qr_code_image=img_byte_arr,  # Save the QR code image (Base64 encoded)
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        new_driver.save()

        return jsonify({
            "message": "Driver registered successfully!",
            "driver_id": driver_id,
            "qr_code": qr_code,
            "qr_code_image": img_byte_arr  # Send Base64-encoded image in response
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    
    
@main.route('/get_drivers', methods=['GET'])
def get_drivers():
    drivers = Driver.objects.all()  # Fetch all drivers from the database
    drivers_list = []

    for driver in drivers:
        drivers_list.append({
            "driver_id": driver.driver_id,
            "name": driver.name,
            "email": driver.email,
            "phone": driver.phone,
            "vehicle_id": driver.vehicle_id,
            "qr_code": driver.qr_code,
            "qr_code_image": driver.qr_code_image,  # This can be a base64 or URL depending on your setup
        })
    
    return jsonify({"drivers": drivers_list}), 200



@main.route('/get_qr_code/<driver_id>', methods=['GET'])
def get_qr_code(driver_id):
    # Retrieve driver information from the database
    driver = Driver.objects(driver_id=driver_id).first()

    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    # Retrieve the Base64-encoded QR code image
    qr_code_image = driver.qr_code_image

    # Return the image as part of the response
    return jsonify({
        "driver_id": driver.driver_id,
        "qr_code_image": qr_code_image  # Send the Base64 image
    }), 200
