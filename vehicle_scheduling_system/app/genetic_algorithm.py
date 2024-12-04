import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from app.config import db

# Configuration
num_vehicles = 20
generations = 500
mutation_rate = 0.01
max_vehicles_in_safari = 100 


# Dynamic Weights Function
def dynamic_weights(generation):
    return {
        "time": 5.0,
        "congestion": 2.0 * (1 + generation / generations),
        "speed": 1.5 * (1 - generation / generations),
        "violations": 15.0,
    }
def remove_duplicates(population):
    unique_population = []
    seen = set()

    for individual in population:
        individual_tuple = tuple(
            (vehicle["entry_time"], vehicle["trip_time"], tuple(vehicle["speed"]))
            for vehicle in individual
        )
        if individual_tuple not in seen:
            seen.add(individual_tuple)
            unique_population.append(individual)

    return unique_population

# Fitness Function
def fitness(schedule, generation=0):
    weights = dynamic_weights(generation)
    total_time = sum(vehicle["trip_time"] for vehicle in schedule)
    congestion_penalty = sum(vehicle.get("congestion", 0) for vehicle in schedule)
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


# Calculate Safari Violations
def calculate_safari_violations(schedule):
    timeline = []  # Track vehicle entry and exit times
    for vehicle in schedule:
        entry = vehicle["entry_time"]
        exit = entry + vehicle["trip_time"]
        timeline.append((entry, 1))  # Entry event
        timeline.append((exit, -1))  # Exit event

    timeline.sort()
    active_vehicles = 0
    max_active_vehicles = 0

    for _, event in timeline:
        active_vehicles += event
        max_active_vehicles = max(max_active_vehicles, active_vehicles)

    return max(0, max_active_vehicles - max_vehicles_in_safari)

# Initialize population
def initialize_population(schedule):
    population_size = 50
    population = []

    for _ in range(population_size):
        used_times = set()
        new_schedule = []

        for trip in schedule:
            entry_time = trip["entry_time"] + random.uniform(-0.20, 0.20)
            entry_time = max(5.5, min(16.5, entry_time))

            while round(entry_time, 1) in used_times:
                entry_time += 0.5
                if entry_time > 16.5:
                    entry_time = 5.5

            used_times.add(round(entry_time, 1))
            new_trp = dict(trip, entry_time=round(entry_time, 1))
            new_schedule.append(new_trp)

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
    child1 = []
    child2 = []
    for i in range(len(parent1)):
        if random.random() < 0.5:
            child1.append(parent1[i])
            child2.append(parent2[i])
        else:
            child1.append(parent2[i])
            child2.append(parent1[i])
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
    # print("gen-pop",population)
    population = sorted(population, key=lambda ind: fitness(ind))
   

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

        population = sorted(offspring , key=fitness)
        population = remove_duplicates(population)
      

    return sorted(population, key=lambda ind: fitness(ind))

# Fetch vehicle data from database
def get_vehicle_data_from_db(db):
    trips = db.trips.find()
    schedule = [
        {
            "entry_time": trip["entry_time"].hour + (0.5 if trip["entry_time"].minute >= 30 else 0),
            "trip_time": trip["trip_time"],
            "congestion": trip.get("congestion", 0),
            "speed": trip.get("speed", [0]),
            "locations": trip.get("locations", []),
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
    schedule = db_schedule 

    print(f"Fetched vehicle data: {schedule}")
    best_10_schedules = run_genetic_algorithm(schedule)
    print(f"----Best 10 schedules for next drivers: {best_10_schedules}")
    return best_10_schedules


# Sample schedule to initialize population
sample_schedule = [
    {
        "entry_time": 8.0,  
        "trip_time": 2.0,  
        "congestion": 0, 
        "speed": [50, 55, 60],  
    },
    {
        "entry_time": 10.0,  
        "trip_time": 1.5,  
        "congestion": 1,  
        "speed": [45, 50, 55],  
    },
]

# Initialize population
population = initialize_population(sample_schedule)
print(f"Initial Population: {population}")

# Sample schedule with overlapping vehicles
test_schedule_with_overlap = [
    {"entry_time": 8.0, "trip_time": 2.0, "congestion": 0, "speed": [50, 55, 60]},
    {"entry_time": 9.0, "trip_time": 2.5, "congestion": 1, "speed": [45, 50, 55]},
    {"entry_time": 9.5, "trip_time": 1.5, "congestion": 2, "speed": [40, 45, 50]},
]

# Calculate safari violations
test_schedule_violation = [
    {"entry_time": 8.0, "trip_time": 2.0, "congestion": 0, "speed": [50, 55, 60]},
    {"entry_time": 8.5, "trip_time": 2.5, "congestion": 2, "speed": [45, 50, 55]},
    {"entry_time": 8.8, "trip_time": 1.5, "congestion": 3, "speed": [40, 45, 50]},
    {"entry_time": 9.0, "trip_time": 3.0, "congestion": 1, "speed": [48, 52, 57]},
]

violations = calculate_safari_violations(test_schedule_violation)
print(f"Calculated Safari Violations: {violations}")
print(f"Fitness Penalty: {fitness(test_schedule_violation)}")



# Test mutation on a schedule
test_schedule_for_mutation = [
    {"entry_time": 8.0, "trip_time": 2.0, "congestion": 0, "speed": [50, 55, 60]},
    {"entry_time": 10.0, "trip_time": 1.5, "congestion": 1, "speed": [45, 50, 55]},
]

# Apply mutation
mutated_schedule = mutate(test_schedule_for_mutation, mutation_rate=0.1)
print(f"Mutated Schedule: {mutated_schedule}")



# # Test fetching trips
# def get_ongoing_trips():
#     cursor = db.trips.find({"status": "ongoing"})  # Filter for ongoing trips
#     for trip in cursor:
#         print(trip)  # This will print each trip document

# # Test the function
# get_ongoing_trips()
