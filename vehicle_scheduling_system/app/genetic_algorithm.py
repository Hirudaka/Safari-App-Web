import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from app.config import db

# Configuration
num_vehicles = 100
generations = 300
mutation_rate = 0.01
max_vehicles_in_safari = 4  # New constraint

# Fitness function
def fitness(schedule):
    weight_time = 5.0
    weight_congestion = 1.0
    weight_speed = 1.0

    total_time = sum(vehicle["trip_time"] for vehicle in schedule)
    congestion_penalty = sum(vehicle.get("congestion", 0) for vehicle in schedule)
    speed_penalty = sum(
        max(0, 30 - sum(vehicle.get("speed", [0])) / len(vehicle["speed"]))
        for vehicle in schedule
    )

    # Additional penalty for exceeding max vehicles in the safari
    safari_violations = calculate_safari_violations(schedule)
    penalty_violations = safari_violations * 10  # High penalty for violations

    return (
        weight_time * total_time
        + weight_congestion * congestion_penalty
        + weight_speed * speed_penalty
        + penalty_violations
    )

# Calculate safari violations
def calculate_safari_violations(schedule):
    """
    Checks if more than the allowed number of vehicles are in the safari area simultaneously.
    """
    timeline = []  # Track vehicle entry and exit times
    for vehicle in schedule:
        entry = vehicle["entry_time"]
        exit = entry + vehicle["trip_time"]
        timeline.append((entry, 1))  # Entry event
        timeline.append((exit, -1))  # Exit event

    timeline.sort()  # Sort events by time
    active_vehicles = 0
    max_active_vehicles = 0

    for time, event in timeline:
        active_vehicles += event
        max_active_vehicles = max(max_active_vehicles, active_vehicles)

    # Return the number of vehicles exceeding the limit
    return max(0, max_active_vehicles - max_vehicles_in_safari)

# Initialize population
def initialize_population(schedule):
    population_size = max(10, len(schedule) * 2)
    population = []

    for _ in range(population_size):
        used_times = set()
        new_schedule = []

        for vehicle in schedule:
            entry_time = vehicle["entry_time"] + random.uniform(-0.5, 0.5)
            entry_time = max(5.5, min(16.5, entry_time))

            while round(entry_time, 1) in used_times:
                entry_time += 0.5
                if entry_time > 16.5:
                    entry_time = 5.5

            used_times.add(round(entry_time, 1))
            new_vehicle = dict(vehicle, entry_time=round(entry_time, 1))
            new_schedule.append(new_vehicle)

        population.append(new_schedule)
    return population

# Selection
def selection(population):
    total_fitness = sum(1 / (1 + fitness(ind)) for ind in population)
    probabilities = [(1 / (1 + fitness(ind))) / total_fitness for ind in population]
    num_to_select = max(2, len(population) // 2)
    return random.choices(population, probabilities, k=num_to_select)

# Crossover
def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

# Mutation
def mutate(schedule, mutation_rate):
    used_times = {round(vehicle["entry_time"], 1) for vehicle in schedule}

    for vehicle in schedule:
        if random.random() < mutation_rate:
            original_time = round(vehicle["entry_time"], 1)
            new_time = original_time + random.uniform(-1, 1)
            new_time = max(5.5, min(16.5, new_time))

            while round(new_time, 1) in used_times:
                new_time += 0.5
                if new_time > 16.5:
                    new_time = 5.5
            used_times.add(round(new_time, 1))

            vehicle["congestion"] = max(0, min(5, vehicle["congestion"] + random.randint(-1, 1)))
            vehicle["speed"] = [
                max(30, min(60, speed + random.randint(-5, 5)))
                for speed in vehicle["speed"]
            ]
            vehicle["entry_time"] = round(new_time, 1)
    return schedule

# Genetic Algorithm
def run_genetic_algorithm(schedule):
    population = initialize_population(schedule)
    population = sorted(population, key=fitness)
    elites = population[:2]

    for generation in range(generations):
        mutation_rate = max(0.01, 0.1 * (1 - generation / generations))
        selected = selection(population)

        offspring = []
        while len(offspring) < len(population):
            if len(selected) < 2:
                selected = population

            parent1, parent2 = random.sample(selected, 2)
            child1, child2 = crossover(parent1, parent2)
            offspring.extend([mutate(child1, mutation_rate), mutate(child2, mutation_rate)])

        population = sorted(offspring + elites, key=fitness)
        elites = population[:2]

    return sorted(population, key=fitness)[:1]

# Fetch vehicle data from database
def get_vehicle_data_from_db(db):
    trips = db.trips.find()
    schedule = [
        {
            "entry_time": trip["entry_time"].hour + (0.5 if trip["entry_time"].minute >= 30 else 0),
            "trip_time": trip["trip_time"],
            "congestion": trip.get("congestion", 0),
            "speed": trip.get("speed", [0]),
        }
        for trip in trips
    ]
    return schedule, len(schedule)

# Simulate random trips
def generate_random_trips(num_trips):
    return [
        {
            "entry_time": round(random.uniform(5.5, 16.5), 1),
            "trip_time": round(random.uniform(1.0, 3.0), 1),
            "congestion": random.randint(0, 5),
            "speed": [random.randint(30, 60) for _ in range(5)],
        }
        for _ in range(num_trips)
    ]

# Main function to run the algorithm
def fetch_and_schedule_for_next_10_drivers():
    db_schedule, _ = get_vehicle_data_from_db(db)
    simulated_trips = generate_random_trips(10)
    schedule = db_schedule + simulated_trips

    print(f"Fetched vehicle data: {schedule}")
    best_10_schedules = run_genetic_algorithm(schedule)
    print(f"----Best 10 schedules for next drivers: {best_10_schedules}")

# Run the function
fetch_and_schedule_for_next_10_drivers()





# # Test fetching trips
# def get_ongoing_trips():
#     cursor = db.trips.find({"status": "ongoing"})  # Filter for ongoing trips
#     for trip in cursor:
#         print(trip)  # This will print each trip document

# # Test the function
# get_ongoing_trips()
