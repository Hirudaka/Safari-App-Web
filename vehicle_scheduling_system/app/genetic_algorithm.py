import random
from pymongo import MongoClient

# Configuration
population_size = 10  
num_vehicles = 20 
generations = 100
mutation_rate = 0.01

# Fitness function: Adjusted to reflect the system goals better
def fitness(schedule):
    total_time = sum(vehicle["trip_time"] for vehicle in schedule)
    congestion_penalty = sum(vehicle.get("congestion", 0) for vehicle in schedule)
    speed_penalty = sum(max(0, 30 - vehicle.get("speed", 0)) for vehicle in schedule)
    return total_time + congestion_penalty + speed_penalty

# Initialize population with random schedules
def initialize_population():
    return [generate_random_schedule() for _ in range(population_size)]

# Select the best schedules based on fitness
def selection(population):
    return sorted(population, key=fitness)[:population_size // 2]

# Crossover: Combining two parents to generate two children
def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

# Mutation: Change vehicle entry time randomly
def mutate(schedule):
    for vehicle in schedule:
        if random.random() < mutation_rate:
            vehicle["entry_time"] += random.randint(-5, 5)  # Random change in entry time
            vehicle["entry_time"] = max(0, min(24, vehicle["entry_time"]))  # Keep within 0-24 hours
    return schedule

# Run genetic algorithm
def run_genetic_algorithm():
    population = initialize_population()
    for _ in range(generations):
        selected = selection(population)
        offspring = []
        while len(offspring) < population_size:
            parent1, parent2 = random.sample(selected, 2)
            child1, child2 = crossover(parent1, parent2)
            offspring.extend([mutate(child1), mutate(child2)])
        population = offspring
    return min(population, key=fitness)

# Generate random schedule for vehicles (more realistic distribution of times)
def generate_random_schedule():
    schedule = []
    for _ in range(num_vehicles):
        vehicle = {
            "entry_time": random.randint(0, 24),  # Random entry time between 0-24 hours
            "trip_time": random.randint(1, 3),     # Random trip time between 1-3 hours
            "congestion": random.randint(0, 5),    # Random congestion level (0-5)
            "speed": random.randint(20, 60)        # Random speed (between 20-60 km/h)
        }
        schedule.append(vehicle)
    return schedule

# MongoDB connection
def connect_to_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['vehicle_scheduling']
    return db

# Fetch vehicle data from MongoDB (optional for actual data-driven scheduling)
def get_vehicle_data_from_db(db, num_vehicles):
    vehicles = db.vehicles.find().limit(num_vehicles)
    return [{"entry_time": vehicle["entry_time"],
             "trip_time": vehicle["trip_time"],
             "congestion": vehicle["congestion"],
             "speed": vehicle["speed"]} for vehicle in vehicles]

# Example MongoDB usage: fetch and use data
def fetch_and_schedule_from_db():
    db = connect_to_db()
    vehicles_data = get_vehicle_data_from_db(db, num_vehicles)
    print(f"Fetched vehicle data: {vehicles_data}")
    best_schedule = run_genetic_algorithm()
    print(f"Best schedule: {best_schedule}")

# Run the algorithm
fetch_and_schedule_from_db()
