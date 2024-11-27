from app.config import db
from app.models import Trip
from app.genetic_algorithm import run_genetic_algorithm

# Fetch vehicle trip data from MongoDB (using PyMongo)
def get_vehicle_data_from_db():
    trips = db.trips.find({"status": "ongoing"})  # Filter for ongoing trips
    trip_list = list(trips)

    schedule = []
    for trip in trip_list:
        vehicle = {
            "entry_time": trip["entry_time"].hour,  # Ensure entry_time is datetime
            "trip_time": trip["trip_time"],         # Ensure trip_time exists
            "congestion": trip.get("congestion", 0), # Handle missing congestion
            "speed": trip.get("speed", 30),         # Handle missing speed
        }
        schedule.append(vehicle)
    
    trip_count = len(schedule)
    return schedule, trip_count

# Fetch vehicle trip data using MongoEngine
def get_ongoing_trips():
    trips = Trip.objects(status="ongoing")  # Query using MongoEngine
    schedule = [
        {
            "entry_time": trip.entry_time.hour,
            "trip_time": trip.trip_time,
            "congestion": trip.congestion,
            "speed": trip.speed,
        }
        for trip in trips
    ]
    trip_count = len(schedule)
    return schedule, trip_count

# Main function to fetch data and run the algorithm
def main():
    # Fetch data from MongoDB
    schedule, trip_count = get_vehicle_data_from_db()  # For PyMongo
    # OR
    # schedule, trip_count = get_ongoing_trips()       # For MongoEngine

    print(f"Fetched {trip_count} ongoing trips: {schedule}")

    # Run Genetic Algorithm
    if trip_count > 0:
        best_schedule = run_genetic_algorithm(schedule)
        print(f"Optimized Schedule: {best_schedule}")
    else:
        print("No ongoing trips to optimize.")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, threaded=False, port=5003)
