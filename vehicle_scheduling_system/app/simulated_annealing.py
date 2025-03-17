import random
import math
from app.config import db
from datetime import datetime, timedelta


# Simulated Annealing Parameters
initial_temperature = 1000
cooling_rate = 0.99
min_temperature = 1
generations = 500
max_vehicles_in_safari = 100 
MUTATION_RATE = 0.1


def dynamic_weights(generation):
    return {
        "time": 5.0,
        "congestion": 2.0 * (1 + generation / generations),
        "speed": 1.5 * (1 - generation / generations),
        "violations": 15.0,
    }

def calculate_safari_violations(schedule):
    timeline = []  # Track vehicle entry and exit times
    for vehicle in schedule:
        entry = vehicle["entry_time"]
        # Convert trip_time (in hours) to a timedelta object
        exit = entry + timedelta(hours=vehicle["trip_time"])
        timeline.append((entry, 1))  # Entry event
        timeline.append((exit, -1))  # Exit event

    timeline.sort()
    active_vehicles = 0
    max_active_vehicles = 0
    max_vehicles_in_safari = 100

    for _, event in timeline:
        active_vehicles += event
        max_active_vehicles = max(max_active_vehicles, active_vehicles)

    return max(0, max_active_vehicles - max_vehicles_in_safari)

def fitness(schedule, generation=0):
    weights = dynamic_weights(generation)
    total_time = sum(vehicle["trip_time"] for vehicle in schedule)
    congestion_penalty = sum(
    sum(vehicle["congestion"]) if isinstance(vehicle.get("congestion"), list) else vehicle.get("congestion", 0)
    for vehicle in schedule
    )
    speed_penalty = sum(
        (max(0, 30 - sum(vehicle["speed"]) / len(vehicle["speed"])) ** 2)
        for vehicle in schedule
    )
    safari_violations = calculate_safari_violations(schedule)
    penalty_violations = safari_violations * weights["violations"]

    return (
        weights["time"] * total_time
        + weights["congestion"] * congestion_penalty
        + weights["speed"] * speed_penalty
        + penalty_violations
    )

def mutate(schedule, mutation_rate):
    used_times = {vehicle["entry_time"] for vehicle in schedule}

    for vehicle in schedule:
        if random.random() < mutation_rate:
            original_time = vehicle["entry_time"]
            # Add a random timedelta to the entry_time
            new_time = original_time + timedelta(hours=random.uniform(-1, 1))
            new_time = max(original_time - timedelta(hours=0.20), min(original_time + timedelta(hours=0.20), new_time))

            while new_time in used_times:
                new_time += timedelta(hours=0.5)
                if new_time > original_time + timedelta(hours=16.5):
                    new_time = original_time - timedelta(hours=16.5)

            used_times.add(new_time)

            vehicle["congestion"] = [max(0, min(5, c + random.randint(-1, 1))) for c in vehicle["congestion"]]
            vehicle["speed"] = [
                max(30, min(60, speed + random.randint(-5, 5)))
                for speed in vehicle["speed"]
            ]
            vehicle["entry_time"] = new_time
    return schedule

# Simulated Annealing Function
def simulated_annealing(schedule):
    # Initialize the current solution
    current_schedule = schedule.copy()
    current_fitness = fitness(current_schedule)

    # Initialize the best solution
    best_schedule = current_schedule.copy()
    best_fitness = current_fitness

    temperature = initial_temperature

    while temperature > min_temperature:
        # Generate a neighbor solution by perturbing the current schedule
        neighbor_schedule = mutate(current_schedule.copy(), mutation_rate=0.1)
        neighbor_fitness = fitness(neighbor_schedule)

        # Calculate the change in fitness
        delta_fitness = neighbor_fitness - current_fitness

        # Accept the neighbor solution if it's better or with a certain probability
        if delta_fitness < 0 or random.random() < math.exp(-delta_fitness / temperature):
            current_schedule = neighbor_schedule
            current_fitness = neighbor_fitness

            # Update the best solution if the current one is better
            if current_fitness < best_fitness:
                best_schedule = current_schedule.copy()
                best_fitness = current_fitness

        # Cool down the temperature
        temperature *= cooling_rate

    return best_schedule

def get_vehicle_data_from_db(db):
    trips = db.trips.find()
    schedule = [
        {
            "entry_time": trip["entry_time"],  # Ensure this is a datetime object
            "trip_time": float(trip["trip_time"]),  # Ensure trip_time is a float
            "congestion": [int(c) for c in trip.get("congestion", [0])],  # Ensure congestion is a list of integers
            "speed": [float(s) for s in trip.get("speed", [0])],  # Ensure speed is a list of floats
            "locations": trip.get("locations", []),  # Ensure locations is a list of [lat, lon] pairs
        }
        for trip in trips
    ]
    return schedule, len(schedule)

def generate_random_trips(num_trips):
    now = datetime.now()
    return [
        {
            "entry_time": now + timedelta(hours=random.uniform(0, 24)),  # Random datetime within the next 24 hours
            "trip_time": round(random.uniform(1.0, 3.0), 1),  # Ensure trip_time is a float
            "congestion": [random.randint(0, 5) for _ in range(5)],  # Ensure congestion is a list of integers
            "speed": [float(random.randint(30, 60)) for _ in range(5)],  # Ensure speed is a list of floats
            "locations": [[random.uniform(0, 100), random.uniform(0, 100)] for _ in range(2)],  # Ensure locations is a list of [lat, lon] pairs
        }
        for _ in range(num_trips)
    ]

# Main function to run Simulated Annealing
def fetch_and_schedule_for_next_10_drivers_sa():
    db_schedule, _ = get_vehicle_data_from_db(db)
    simulated_trips = generate_random_trips(10)
    schedule = db_schedule + simulated_trips

    print(f"Fetched vehicle data: {schedule}")
    best_schedule = simulated_annealing(schedule)
    print(f"----Best schedule for next drivers using Simulated Annealing: {best_schedule}")
    return best_schedule

# Test the Simulated Annealing function
best_schedule_sa = fetch_and_schedule_for_next_10_drivers_sa()
print(f"Best Schedule (SA): {best_schedule_sa}")