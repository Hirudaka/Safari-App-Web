import random
import datetime
from pymongo import MongoClient
from app.config import db
from app.models import Trip

# Configuration
population_size = 10
num_vehicles = 20
generations = 100
mutation_rate = 0.01

# Fitness function: Adjusted to reflect the system goals better
def fitness(schedule):
    total_time = sum(vehicle["trip_time"] for vehicle in schedule)
    congestion_penalty = sum(vehicle.get("congestion", 0) for vehicle in schedule)
    # Calculate speed penalty (average speed of each vehicle in the schedule)
    speed_penalty = sum(max(0, 30 - sum(vehicle.get("speed", [0])) / len(vehicle["speed"])) for vehicle in schedule)
    return total_time + congestion_penalty + speed_penalty

# Initialize population with real schedule data
def initialize_population(schedule):
    return [schedule for _ in range(population_size)]  # Initialize population with real schedule data

# Select the best schedules based on fitness
def selection(population):
    # Sort by fitness and return the top 50% of the population
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
        if isinstance(vehicle["entry_time"], int):  # Check if entry_time is an integer
            if random.random() < mutation_rate:
                vehicle["entry_time"] += random.randint(-5, 5)  # Random change in entry time
                vehicle["entry_time"] = max(0, min(24, vehicle["entry_time"]))  # Keep within 0-24 hours
        else:
            print(f"Unexpected entry_time type: {type(vehicle['entry_time'])}")  # Debugging log
    return schedule

def run_genetic_algorithm(schedule):
    population = initialize_population(schedule)  # Initialize with real trip data
    for _ in range(generations):
        selected = selection(population)
        offspring = []
        while len(offspring) < population_size:
            parent1, parent2 = random.sample(selected, 2)
            child1, child2 = crossover(parent1, parent2)
            offspring.extend([mutate(child1), mutate(child2)])
        population = offspring
    
    # Select the top 10 best schedules based on fitness
    top_10_schedules = sorted(population, key=fitness)[:10]  # Get the top 10 best schedules
    return top_10_schedules  # Return the best 10 schedules




# Fetch vehicle trip data from MongoDB
def get_vehicle_data_from_db(db):
    trips = db.trips.find({"status": "ongoing"})  # Filter for ongoing trips
    trip_list = list(trips)  # Convert cursor to a list
    print("Matching trips:", trip_list)  # Debugging log

    schedule = []
    for trip in trip_list:
        vehicle = {
            # If entry_time is a datetime object, extract the hour
            "entry_time": trip["entry_time"].hour if isinstance(trip["entry_time"], datetime.datetime) else trip["entry_time"],
            "trip_time": trip["trip_time"],
            "congestion": trip.get("congestion", 0),
            "speed": trip.get("speed", [0]),  # Ensure speed is always a list
        }
        schedule.append(vehicle)

    trip_count = len(schedule)
    return schedule, trip_count

# Fetch and schedule from the database
def fetch_and_schedule_for_next_10_drivers():
    schedule, _ = get_vehicle_data_from_db(db)
    print(f"Fetched vehicle data: {schedule}")
    
    # Pass the fetched schedule to the genetic algorithm
    best_10_schedules = run_genetic_algorithm(schedule)
    print(f"----Best 10 schedules for next drivers: {best_10_schedules}")

# Run the algorithm and print the best 10 schedules for next drivers
fetch_and_schedule_for_next_10_drivers()

# # Test fetching trips
# def get_ongoing_trips():
#     cursor = db.trips.find({"status": "ongoing"})  # Filter for ongoing trips
#     for trip in cursor:
#         print(trip)  # This will print each trip document

# # Test the function
# get_ongoing_trips()
