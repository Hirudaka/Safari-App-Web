# app/routes.py
import random
import uuid
from flask import Blueprint, jsonify, current_app, request
from flask_cors import cross_origin
import qrcode
from io import BytesIO
from base64 import b64encode
from app.models import Driver
from app.models import Trip
from .genetic_algorithm import get_vehicle_data_from_db,fetch_and_schedule_for_next_10_drivers
# from app.hybrid import fetch_and_schedule_for_next_10_drivers_hybrid,compare_and_select_best_schedule
from app.hybrid import fetch_and_schedule_for_next_10_drivers_hybrid
from app.algorithmHandler import run_all_algorithms,run_multi_objective_optimization
from app.genetic_algorithm import run_genetic_algorithm
from datetime import datetime
from bson import ObjectId
import json 
import uuid
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from app.test_nsga2 import SafariSchedulingProblem


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

def convert_objectid(obj):
    """ Recursively convert ObjectId to string in a dictionary or list. """
    if isinstance(obj, dict):
        return {k: convert_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(i) for i in obj]
    elif isinstance(obj, ObjectId):  
        return str(obj)  # Convert ObjectId to string
    return obj

@main.route('/api/schedule', methods=['GET'])
def get_schedule():
    # Fetch vehicle data (schedule) from the database
    schedule, _ = get_vehicle_data_from_db(current_app.mongo_db)  
    print("schedule","\n",schedule)
    optimized_schedule = run_genetic_algorithm(schedule)  # Pass the fetched schedule to the algorithm
    optimized_schedule = fetch_and_schedule_for_next_10_drivers()
    #hybrid_schedule = compare_and_select_best_schedule()
    hybrid_schedule = fetch_and_schedule_for_next_10_drivers_hybrid()
    # problem = SafariSchedulingProblem(schedule)

    # # Define the NSGA-II algorithm
    # algorithm = NSGA2(pop_size=100)

    # # Run the optimization
    # res = minimize(problem, algorithm, ('n_gen', 200), verbose=True)

    # # Print the results
    # print("Best Solutions (X):\n", res.X)
    # print("Objective Values (F):\n", res.F)


    print("hi",hybrid_schedule)
    # Add a `booked` field to each schedule item
    for item in hybrid_schedule:
        item["id"]=str(uuid.uuid4())
        item["booked"] = False
        item["diverId"]=None
        current_app.mongo_db.optimized_schedule.insert_one(item)  # Save the optimized schedule to MongoDB

    # results = run_all_algorithms(schedule)
    # best_result = compare_results(results)

    # print("\n")
    # print("Compared results")
    # print("\n")  # Corrected newline
    # (best_result)

    return jsonify({'schedule': convert_objectid(hybrid_schedule)}), 200

@main.route('/end_trip/<trip_id>', methods=['PUT'])
def end_trip(trip_id):  
    end_time = datetime.now()

    try:
        trip_id_obj = ObjectId(trip_id)
    except Exception as e:
        return jsonify({"error": "Invalid ObjectId format"}), 400

    trip = current_app.mongo_db['trips'].find_one({"_id": trip_id_obj})
    
    if not trip:
        return jsonify({"error": "No ongoing trip found with this ID"}), 400

    # Get the entry_time from the trip
    entry_time = trip.get("entry_time")
    
    if not entry_time:
        return jsonify({"error": "Entry time is missing for this trip"}), 400

    # Convert entry_time to a datetime object if it's stored as a string
    if isinstance(entry_time, str):
        entry_time = datetime.fromisoformat(entry_time)

    # Calculate trip duration
    trip_duration = (end_time - entry_time).total_seconds()  # Duration in seconds

    # Update the trip status, end_time, and trip_duration
    current_app.mongo_db['trips'].update_one(
        {"_id": trip_id_obj},
        {"$set": {"status": "completed", "end_time": end_time, "trip_time": trip_duration}}
    )

    return jsonify({"message": "Trip ended", "end_time": end_time, "trip_time": trip_duration}), 200

@main.route('/api/optimized_schedule', methods=['GET'])
def get_optimized_schedule():
    """
    Fetch the latest optimized schedule from the database.
    """
    # Retrieve the latest optimized schedule from MongoDB
    optimized_schedules = list(current_app.mongo_db.optimized_schedule.find().sort("_id", -1))

    if not optimized_schedules:
        # If no optimized schedule exists
        return jsonify({'message': 'No optimized schedule found.'}), 404

    # Remove the MongoDB-specific "_id" field for cleaner output
    optimized_schedules = convert_objectid(optimized_schedules)

    print("Retrieved from DB:", json.dumps(optimized_schedules, indent=2, default=str))  # Debug output

    return jsonify({'optimized_schedule': optimized_schedules}), 200



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


# @main.route('/api/start_trip', methods=['POST'])
# def start_trip():
#     data = request.get_json()

   
#     driver_id = data.get("driver_id")
#     vehicle_id = data.get("vehicle_id")
#     if not driver_id or not vehicle_id:
#         return jsonify({"error": "Driver ID and Vehicle ID are required"}), 400

   
#     entry_time = datetime.now() 
#     trip_time = data.get("trip_time", 1)
#     congestion = data.get("congestion", 0) 
#     speed = data.get("speed", []) 
#     locations = data.get("locations", []) 

#     if not all(isinstance(loc, list) and len(loc) == 2 for loc in locations):
#         return jsonify({"error": "Locations must be a list of [latitude, longitude] pairs"}), 400

    
#     trip_data = {
#         "driver_id": driver_id,
#         "vehicle_id": vehicle_id,
#         "entry_time": entry_time,
#         "trip_time": trip_time,
#         "congestion": congestion,
#         "speed": speed,
#         "locations": locations,
#         "status": "ongoing"  
#     }

   
#     db = current_app.mongo_db['trips']
#     inserted_trip = db.insert_one(trip_data)

   
#     trip_data["_id"] = str(inserted_trip.inserted_id)

#     return jsonify({
#         "message": "Trip started successfully.",
#         "trip_details": trip_data
#     }), 201
@main.route('/api/start_trip', methods=['POST'])
def start_trip():
    data = request.get_json()

    driver_id = data.get("driver_id")
    vehicle_id = data.get("vehicle_id")
    if not driver_id or not vehicle_id:
        return jsonify({"error": "Driver ID and Vehicle ID are required"}), 400

    entry_time = datetime.now()
    trip_time = datetime.now() - entry_time
    trip_time_seconds = trip_time.total_seconds()  # Convert to seconds

    speed = data.get("speed", [])
    locations = data.get("locations", [])

    if not all(isinstance(loc, list) and len(loc) == 2 for loc in locations):
        return jsonify({"error": "Locations must be a list of [latitude, longitude] pairs"}), 400

    trip_data = {
        "driver_id": driver_id,
        "vehicle_id": vehicle_id,
        "entry_time": entry_time,
        "trip_time": trip_time_seconds,  # Store as seconds
        "speed": speed,
        "locations": locations,
        "congestion": [0],
        "status": "ongoing"
    }

    db = current_app.mongo_db['trips']
    inserted_trip = db.insert_one(trip_data)

    trip_data["_id"] = str(inserted_trip.inserted_id)

    return jsonify({
        "message": "Trip started successfully.",
        "trip_details": trip_data
    }), 201

# @main.route('/api/trips/<trip_id>/add_locations', methods=['PUT'])
# def append_locations(trip_id):
#     data = request.get_json()
#     new_locations = data.get("locations", [])

   
#     if not all(isinstance(loc, list) and len(loc) == 2 for loc in new_locations):
#         return jsonify({"error": "Locations must be a list of [latitude, longitude] pairs"}), 400

   
#     try:
#         trip_id_obj = ObjectId(trip_id)
#     except Exception as e:
#         return jsonify({"error": "Invalid ObjectId format"}), 400

#     # Find the trip
#     trip = current_app.mongo_db['trips'].find_one({"_id": trip_id_obj})
#     if not trip:
#         return jsonify({"error": "Trip not found"}), 404

#     # Append new locations to the existing ones
#     current_locations = trip.get("locations", [])
#     updated_locations = current_locations + new_locations

   
#     current_app.mongo_db['trips'].update_one(
#         {"_id": trip_id_obj},
#         {"$set": {"locations": updated_locations}}
#     )

#     return jsonify({"message": "Locations added successfully", "updated_locations": updated_locations}), 200

@main.route('/api/trips/<trip_id>/updateStatus', methods=['PUT'])
def update_trip_status(trip_id):
    data = request.get_json()
    new_locations = data.get("locations", [])
    new_speed = data.get("speed", [])
    new_congestion = data.get("congestion", [])  # Ensure it's a list
    if not isinstance(new_congestion, list):  
        new_congestion = [new_congestion] 


    # Validate new locations
    if not all(isinstance(loc, list) and len(loc) == 2 for loc in new_locations):
        return jsonify({"error": "Locations must be a list of [latitude, longitude] pairs"}), 400

    # Validate new speed array
    if not all(isinstance(s, (int, float)) for s in new_speed):
        return jsonify({"error": "Speed must be a list of numbers"}), 400

    # Validate new trip time

    # Convert trip_id string to ObjectId
    try:
        trip_id_obj = ObjectId(trip_id)
    except Exception as e:
        return jsonify({"error": "Invalid ObjectId format"}), 400

    # Find the trip
    trip = current_app.mongo_db['trips'].find_one({"_id": trip_id_obj})
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    
    entry_time = trip.get("entry_time")
    
    if not entry_time:
        return jsonify({"error": "Entry time is missing for this trip"}), 400

    # Convert entry_time to a datetime object if it's stored as a string
    if isinstance(entry_time, str):
        entry_time = datetime.fromisoformat(entry_time)

    end_time = datetime.now()
    # Calculate trip duration
    trip_duration = (end_time - entry_time).total_seconds()  # Duration in seconds

    # Append new locations and speed to the existing ones
    current_locations = trip.get("locations", [])
    current_speed = trip.get("speed", [])
    current_congestion = trip.get("congestion", [])
    if not isinstance(current_congestion, list):
        current_congestion = [current_congestion]  # Convert to list if it's not

    updated_congestion = current_congestion + new_congestion

    updated_locations = current_locations + new_locations
    updated_speed = current_speed + new_speed

    # Check the last speed to determine the status
    last_speed = updated_speed[-1] if updated_speed else None
    new_status = "idle" if last_speed < 1 else "ongoing"

    # Update the trip in the database
    current_app.mongo_db['trips'].update_one(
        {"_id": trip_id_obj},
        {
            "$set": {
                "locations": updated_locations,
                "speed": updated_speed,
                "trip_time": trip_duration,
                "status": new_status,
                "congestion": updated_congestion
            }
        }
    )

    return jsonify({
        "message": "Trip updated successfully",
        "updated_locations": updated_locations,
        "updated_speed": updated_speed,
        "updated_trip_time": trip_duration,
        "new_status": new_status
    }), 200


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
        trip["entry_time"] = trip["entry_time"].isoformat()  

    return jsonify({
        "message": "Trips fetched successfully.",
        "trips": trips
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
            qr_code_image=img_byte_arr,  
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        new_driver.save()

        return jsonify({
            "message": "Driver registered successfully!",
            "driver_id": driver_id,
            "qr_code": qr_code,
            "qr_code_image": img_byte_arr  
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    
    
@main.route('/get_drivers', methods=['GET'])
def get_drivers():
    drivers = Driver.objects.all() 
    drivers_list = []

    for driver in drivers:
        drivers_list.append({
            "driver_id": driver.driver_id,
            "name": driver.name,
            "email": driver.email,
            "phone": driver.phone,
            "vehicle_id": driver.vehicle_id,
            "qr_code": driver.qr_code,
            "qr_code_image": driver.qr_code_image, 
        })
    
    return jsonify({"drivers": drivers_list}), 200



@main.route('/get_driver/<driver_id>', methods=['GET'])
def get_driver_details(driver_id):
    
    driver = Driver.objects(driver_id=driver_id).first()

    if not driver:
        return jsonify({"error": "Driver not found"}), 404
    
    return jsonify({
        "driver_id": driver.driver_id,
            "name": driver.name,
            "email": driver.email,
            "phone": driver.phone,
            "vehicle_id": driver.vehicle_id,
            "qr_code": driver.qr_code,
            "qr_code_image": driver.qr_code_image, 
    }), 200


@main.route('/api/trips/<trip_id>', methods=['GET'])
def get_trip_by_id(trip_id):
    try:
        
        trip_id_obj = ObjectId(trip_id)
        print(f"Looking for trip with ID: {trip_id_obj}")  # Debug log
        
        # Query the trips collection directly
        db = current_app.mongo_db['trips']
        trip = db.find_one({"_id": trip_id_obj})
        
        if trip:
            
            trip["_id"] = str(trip["_id"])
            if "entry_time" in trip:
                trip["entry_time"] = trip["entry_time"].isoformat()
            if "end_time" in trip:
                trip["end_time"] = trip["end_time"].isoformat()

            print(f"Found trip: {trip}") 
            return jsonify(trip), 200
        else:
            print("Trip not found") 
            return jsonify({'error': 'Trip not found'}), 404

    except Exception as e:
        print(f"Error occurred: {str(e)}")  
        return jsonify({'error': str(e)}), 500
    
@main.route('/api/book_schedule', methods=['POST'])
def book_schedule():
    try:
        data = request.get_json()
        mainSchedule_id = data.get("mainSchedule_id")  # Main schedule document ID
        driver_id = data.get("driver_id")  # Driver ID (likely a UUID)

        # Validate required fields
        if not mainSchedule_id or not driver_id:
            return jsonify({"error": "Schedule ID and Driver ID are required"}), 400

        print(f"Booking schedule {mainSchedule_id} for driver {driver_id}")  # Debug log

        # Convert mainSchedule_id to ObjectId
        try:
            mainSchedule_obj_id = ObjectId(mainSchedule_id)
        except Exception as e:
            return jsonify({"error": "Invalid mainSchedule_id format"}), 400

        # Get database reference
        db = current_app.mongo_db
        schedule_collection = db['optimized_schedule']
        driver_collection = db['drivers']  # Ensure drivers are stored in a separate collection

        # Find the main schedule document
        schedule = schedule_collection.find_one({"_id": mainSchedule_obj_id})
        if not schedule:
            return jsonify({"error": "Schedule not found"}), 404

        # Find the driver details
        driver = Driver.objects(driver_id=driver_id).first()
        print(f"Driver found: {driver}")  # Debug log
        driver_name = driver.name  # Get the driver's name

        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        print(f"Driver found: {driver_name}")

        # Check if the schedule is already booked
        if schedule.get("booked", False):
            print("Schedule is already booked")
            return jsonify({"error": "Schedule is already booked"}), 400

        # Update the schedule to mark it as booked and associate the driver ID
        result = schedule_collection.update_one(
            {"_id": mainSchedule_obj_id},
            {
                "$set": {
                    "booked": True,
                    "driverId": driver_id,
                    "driverName": driver_name
                }
            }
        )
        if result.modified_count == 0:
            return jsonify({"error": "Failed to book schedule"}), 500
        return jsonify({"message": "Schedule booked successfully"}), 200
    except Exception as e:
        print(f"Error in book_schedule: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    
@main.route('/api/trips/driver/<driver_id>', methods=['GET'])
def get_trips_by_driver(driver_id):
    try:
        print(f"Fetching trips for driver ID: {driver_id}")  # Debug log

        db = current_app.mongo_db['trips']

        # Query trips where driver_id matches and status is either "idle" or "ongoing"
        trips = list(db.find({"driver_id": driver_id, "status": {"$in": ["idle", "ongoing"]}}))

        if trips:
            for trip in trips:
                trip["_id"] = str(trip["_id"])
                if "entry_time" in trip:
                    trip["entry_time"] = trip["entry_time"].isoformat()
                if "end_time" in trip:
                    trip["end_time"] = trip["end_time"].isoformat()

            print(f"Found trips: {trips}")  # Debug log
            return jsonify(trips), 200
        else:
            print("No trips found")  # Debug log
            return jsonify({'message': 'No trips found'}), 404
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500