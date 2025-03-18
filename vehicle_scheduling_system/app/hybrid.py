import random
import math
from app.config import db
from app.simulated_annealing import simulated_annealing
import numpy as np
from datetime import datetime, timedelta

# Common Parameters
generations = 500
num_particles = 50
max_iterations = 500
inertia_weight = 0.5
cognitive_weight = 1.5
social_weight = 1.5

def adjust_entry_time(entry_time):
    """
    Adjusts the entry_time to fall within the 5 AM to 6 PM window for tomorrow.
    """
    # Get tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    # Set the start time to 5 AM tomorrow
    start_time = tomorrow.replace(hour=5, minute=0, second=0, microsecond=0)
    # Set the end time to 6 PM tomorrow
    end_time = tomorrow.replace(hour=18, minute=0, second=0, microsecond=0)

    # If the entry_time is before 5 AM, set it to 5 AM
    if entry_time < start_time:
        return start_time
    # If the entry_time is after 6 PM, set it to 5 AM the next day
    elif entry_time > end_time:
        return start_time + timedelta(days=1)
    # Otherwise, keep the entry_time as is
    else:
        return entry_time

# Common Functions
def calculate_diversity(population):
    # Extract entry times and convert them to timestamps (seconds since epoch)
    entry_times = [vehicle["entry_time"].timestamp() for schedule in population for vehicle in schedule]
    
    # Calculate the standard deviation of the timestamps
    return np.std(entry_times)

def adaptive_mutation_rate(generation, diversity):
    base_rate = 0.01
    if diversity < 0.1:  # Threshold for low diversity
        return min(0.1, base_rate * (1 + generation / generations))
    return base_rate

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
        exit = entry + timedelta(hours=vehicle["trip_time"])  # Use timedelta for exit time
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

def fitness(schedule, generation=0):
    weights = dynamic_weights(generation)
    total_time = sum(vehicle["trip_time"] for vehicle in schedule)
    
    # Ensure congestion is always an integer
    congestion_penalty = sum(
        sum(vehicle.get("congestion", [0])) if isinstance(vehicle.get("congestion"), list) else vehicle.get("congestion", 0)
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

# Hybrid Algorithm Functions
def selection(population):
    total_fitness = sum(1 / (1 + fitness(ind)) for ind in population)
    probabilities = [(1 / (1 + fitness(ind))) / total_fitness for ind in population]
    num_to_select = max(2, len(population) // 2)
    return random.choices(population, probabilities, k=num_to_select)

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

def mutate(schedule, mutation_rate):
    for vehicle in schedule:
        if random.random() < mutation_rate:
            # Ensure congestion is a list of integers
            if isinstance(vehicle["congestion"], list):
                vehicle["congestion"] = [max(0, min(5, c + random.randint(-1, 1))) for c in vehicle["congestion"]]
            else:
                vehicle["congestion"] = [max(0, min(5, vehicle["congestion"] + random.randint(-1, 1)))]

            # Mutate speed (ensure it's a list of floats)
            vehicle["speed"] = [
                max(30, min(60, speed + random.randint(-5, 5)))
                for speed in vehicle["speed"]
            ]

            # Mutate entry_time using timedelta, ensuring it stays within 5 AM to 6 PM
            new_entry_time = vehicle["entry_time"] + timedelta(hours=random.uniform(-0.20, 0.20))
            new_entry_time = adjust_entry_time(new_entry_time)  # Ensure it's within the window
            vehicle["entry_time"] = new_entry_time
    return schedule

def run_hybrid_algorithm(schedule):
    population = initialize_population(schedule)
    population = sorted(population, key=lambda ind: fitness(ind))

    for generation in range(generations):
        diversity = calculate_diversity(population)
        mutation_rate = adaptive_mutation_rate(generation, diversity)
        selected = selection(population)
        offspring = []

        while len(offspring) < len(population):
            parent1, parent2 = random.sample(selected, 2)
            child1, child2 = crossover(parent1, parent2)
            offspring.extend([mutate(child1, mutation_rate), mutate(child2, mutation_rate)])

        population = sorted(offspring, key=fitness)
        population = remove_duplicates(population)

    best_solution_ga = population[0]
    best_solution_hybrid = simulated_annealing(best_solution_ga)
    print(f"Best solution from GA: {best_solution_ga}")
    return best_solution_hybrid

# PSO Algorithm Functions
class Particle:
    def __init__(self, schedule):
        self.position = schedule.copy()  # Current schedule
        self.velocity = self._initialize_velocity(schedule)  # Velocity for each vehicle
        self.best_position = schedule.copy()  # Personal best schedule
        self.best_fitness = fitness(schedule)  # Personal best fitness

    def _initialize_velocity(self, schedule):
        # Initialize velocity as small random changes to entry times (as timedelta)
        return [timedelta(hours=random.uniform(-0.5, 0.5)) for _ in range(len(schedule))]

    def update_velocity(self, global_best_position):
        for i in range(len(self.position)):
            r1 = random.random()
            r2 = random.random()

            # Calculate cognitive and social components as timedelta
            cognitive_component = timedelta(hours=cognitive_weight * r1 * (self.best_position[i]["entry_time"] - self.position[i]["entry_time"]).total_seconds() / 3600)
            social_component = timedelta(hours=social_weight * r2 * (global_best_position[i]["entry_time"] - self.position[i]["entry_time"]).total_seconds() / 3600)

            # Update velocity (all components are timedelta)
            self.velocity[i] = timedelta(hours=inertia_weight * self.velocity[i].total_seconds() / 3600) + cognitive_component + social_component

    def update_position(self):
        for i in range(len(self.position)):
            # Update entry_time using timedelta
            new_entry_time = self.position[i]["entry_time"] + self.velocity[i]
            new_entry_time = max(self.position[i]["entry_time"] - timedelta(hours=0.20), min(self.position[i]["entry_time"] + timedelta(hours=0.20), new_entry_time))
            self.position[i]["entry_time"] = new_entry_time

        # Update personal best if current position is better
        current_fitness = fitness(self.position)
        if current_fitness < self.best_fitness:
            self.best_position = self.position.copy()
            self.best_fitness = current_fitness

def run_pso(schedule):
    # Initialize particles
    particles = [Particle(schedule) for _ in range(num_particles)]
    global_best_position = schedule.copy()
    global_best_fitness = fitness(schedule)

    for iteration in range(max_iterations):
        for particle in particles:
            # Update velocity and position
            particle.update_velocity(global_best_position)
            particle.update_position()

            # Update global best
            if particle.best_fitness < global_best_fitness:
                global_best_position = particle.best_position.copy()
                global_best_fitness = particle.best_fitness

        # Print progress
        if iteration % 50 == 0:
            print(f"Iteration {iteration}: Best Fitness = {global_best_fitness}")

    return global_best_position

# Common Utility Functions
def get_vehicle_data_from_db(db):
    trips = db.trips.find()
    schedule = [
        {
            "entry_time": adjust_entry_time(trip["entry_time"]),  # Adjust entry_time for tomorrow
            "trip_time": float(trip["trip_time"]),  # Ensure trip_time is a float
            "congestion": [int(c) for c in trip.get("congestion", [0])],  # Ensure congestion is a list of integers
            "speed": [float(s) for s in trip.get("speed", [0])],  # Ensure speed is a list of floats
            "locations": trip.get("locations", []),  # Ensure locations is a list of [lat, lon] pairs
        }
        for trip in trips
    ]
    return schedule, len(schedule)

def get_optimizedSchedule_data_from_db(db):
    optimized_schedules = db.optimized_schedule.find()
    schedule = [
        {
            "entry_time": adjust_entry_time(trip["entry_time"]),  # Adjust entry_time for tomorrow
            "trip_time": float(trip["trip_time"]),  # Ensure trip_time is a float
            "congestion": [int(c) for c in trip.get("congestion", [0])],  # Ensure congestion is a list of integers
            "speed": [float(s) for s in trip.get("speed", [0])],  # Ensure speed is a list of floats
            "locations": trip.get("locations", []),  # Ensure locations is a list of [lat, lon] pairs
        }
        for trip in optimized_schedules
    ]
    return schedule, len(schedule)

def get_optimized_entry_times(db):
    """
    Fetch all entry times from the optimized_schedule table.
    """
    optimized_schedules = db.optimized_schedule.find()
    return {schedule["entry_time"] for schedule in optimized_schedules}


def generate_random_trips(num_trips):
    return [
        {
            "entry_time": adjust_entry_time(datetime.now() + timedelta(hours=random.uniform(0, 24))),  # Generate entry_time for tomorrow
            "trip_time": round(random.uniform(1.0, 3.0), 1),  # Ensure trip_time is a float
            "congestion": [random.randint(0, 5) for _ in range(5)],  # Ensure congestion is a list of integers
            "speed": [float(random.randint(30, 60)) for _ in range(5)],  # Ensure speed is a list of floats
            "locations": [[random.uniform(0, 100), random.uniform(0, 100)] for _ in range(2)],  # Ensure locations is a list of [lat, lon] pairs
        }
        for _ in range(num_trips)
    ]

def filter_new_schedules(new_schedules, optimized_entry_times):
    """
    Filter out new schedules that have entry times already present in the optimized_schedule table.
    """
    filtered_schedules = []
    for schedule in new_schedules:
        if schedule["entry_time"] not in optimized_entry_times:
            filtered_schedules.append(schedule)
    return filtered_schedules


def initialize_population(schedule):
    population_size = 50
    population = []

    for _ in range(population_size):
        used_times = set()
        new_schedule = []

        for trip in schedule:
            # Adjust entry_time using timedelta, ensuring it stays within 5 AM to 6 PM
            entry_time = trip["entry_time"] + timedelta(hours=random.uniform(-0.20, 0.20))
            entry_time = max(trip["entry_time"].replace(hour=5, minute=0, second=0, microsecond=0), 
                             min(trip["entry_time"].replace(hour=18, minute=0, second=0, microsecond=0), entry_time))

            while entry_time in used_times:
                entry_time += timedelta(hours=0.5)
                if entry_time > trip["entry_time"].replace(hour=18, minute=0, second=0, microsecond=0):
                    entry_time = trip["entry_time"].replace(hour=5, minute=0, second=0, microsecond=0)

            used_times.add(entry_time)
            new_trp = dict(trip, entry_time=entry_time)
            new_schedule.append(new_trp)

        population.append(new_schedule)
    return population

# Main Functions
def fetch_and_schedule_for_next_10_drivers_hybrid(db):
    # Fetch existing schedules from the database
    db_schedule, _ = get_vehicle_data_from_db(db)

    # Fetch entry times from optimized_schedule table
    optimized_entry_times = get_optimized_entry_times(db)

    # Generate random trips (old schedules)
    simulated_trips = generate_random_trips(10)

    # Combine existing schedules and simulated trips
    schedule = db_schedule + simulated_trips

    # Run the hybrid algorithm to generate new schedules
    new_schedules = run_hybrid_algorithm(schedule)

    # Filter out schedules with duplicate entry times
    filtered_schedules = filter_new_schedules(new_schedules, optimized_entry_times)

    print(f"Filtered schedules (no duplicates): {filtered_schedules}")
    return filtered_schedules

def fetch_and_schedule_for_next_10_drivers_pso(db):
    db_schedule, _ = get_vehicle_data_from_db(db)
    simulated_trips = generate_random_trips(10)
    optimized_entry_times = get_optimized_entry_times(db)
    # schedule = db_schedule + simulated_trips
    schedule = simulated_trips

    print(f"Fetched vehicle data: {schedule}")
    best_schedule = run_pso(schedule)
    print(f"----Best schedule for next drivers using PSO: {best_schedule}")
    filtered_schedules = filter_new_schedules(best_schedule, optimized_entry_times)
    return best_schedule

def compare_and_select_best_schedule():
    # Run Hybrid Algorithm
    best_schedule_hybrid = fetch_and_schedule_for_next_10_drivers_hybrid(db)
    hybrid_fitness = fitness(best_schedule_hybrid)

    # Run PSO Algorithm
    best_schedule_pso = fetch_and_schedule_for_next_10_drivers_pso(db)
    pso_fitness = fitness(best_schedule_pso)

    # Compare fitness values
    if hybrid_fitness < pso_fitness:
        print("Hybrid Algorithm produced a better schedule.")
        return best_schedule_hybrid
    else:
        print("PSO Algorithm produced a better schedule.")
        return best_schedule_pso

def fetch_and_schedule_for_next_10_drivers():
    db_schedule, _ = get_vehicle_data_from_db(db)
    simulated_trips = generate_random_trips(10)
    # schedule = db_schedule + simulated_trips
    schedule = simulated_trips

    print(f"Fetched vehicle data: {schedule}")
    best_schedule = compare_and_select_best_schedule()
    print(f"----Best overall schedule: {best_schedule}")
    return best_schedule

# Test the function
best_schedule = fetch_and_schedule_for_next_10_drivers()
print(f"Best Schedule (Overall): {best_schedule}")
