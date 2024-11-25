# app/routes.py
import random
import uuid
from flask import Blueprint, jsonify, current_app, request
from flask_cors import cross_origin

from app.models import Driver
from .genetic_algorithm import run_genetic_algorithm
from datetime import datetime
import qrcode

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

@main.route('/start_trip', methods=['POST'])
def start_trip():
    data = request.get_json()

    # Check if driver_id is provided
    driver_id = data.get("driver_id")
    if not driver_id:
        return jsonify({"error": "Driver ID is required"}), 400

    start_time = datetime.now()
    current_app.mongo_db['trips'].insert_one({
        "driver_id": driver_id,
        "start_time": start_time,
        "status": "ongoing",
    })

    return jsonify({"message": "Trip started", "start_time": start_time}), 200


import qrcode
from io import BytesIO
from base64 import b64encode

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
