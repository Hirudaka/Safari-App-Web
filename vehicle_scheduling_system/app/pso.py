import random
import math
from app.config import db

# PSO Parameters
num_particles = 50
max_iterations = 500
inertia_weight = 0.5
cognitive_weight = 1.5
social_weight = 1.5
generations = 500

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
    congestion_penalty = sum(
    sum(vehicle["congestion"]) if isinstance(vehicle.get("congestion"), list) else vehicle.get("congestion", 0)
    for vehicle in schedule)
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
    max_vehicles_in_safari = 0

    for _, event in timeline:
        active_vehicles += event
        max_active_vehicles = max(max_active_vehicles, active_vehicles)

    return max(0, max_active_vehicles - max_vehicles_in_safari)

# Particle Representation
class Particle:
    def __init__(self, schedule):
        self.position = schedule.copy()  # Current schedule
        self.velocity = self._initialize_velocity(schedule)  # Velocity for each vehicle
        self.best_position = schedule.copy()  # Personal best schedule
        self.best_fitness = fitness(schedule)  # Personal best fitness

    def _initialize_velocity(self, schedule):
        # Initialize velocity as small random changes to entry times
        return [random.uniform(-0.5, 0.5) for _ in range(len(schedule))]

    def update_velocity(self, global_best_position):
        for i in range(len(self.position)):
            r1 = random.random()
            r2 = random.random()

            # Update velocity components
            cognitive_component = cognitive_weight * r1 * (self.best_position[i]["entry_time"] - self.position[i]["entry_time"])
            social_component = social_weight * r2 * (global_best_position[i]["entry_time"] - self.position[i]["entry_time"])

            self.velocity[i] = inertia_weight * self.velocity[i] + cognitive_component + social_component

    def update_position(self):
        for i in range(len(self.position)):
            # Update entry time based on velocity
            new_entry_time = self.position[i]["entry_time"] + self.velocity[i]
            new_entry_time = max(5.5, min(16.5, new_entry_time))  # Clamp to valid range
            self.position[i]["entry_time"] = new_entry_time

        # Update personal best if current position is better
        current_fitness = fitness(self.position)
        if current_fitness < self.best_fitness:
            self.best_position = self.position.copy()
            self.best_fitness = current_fitness

# PSO Algorithm
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

# Main function to run PSO
def fetch_and_schedule_for_next_10_drivers_pso():
    db_schedule, _ = get_vehicle_data_from_db(db)
    simulated_trips = generate_random_trips(10)
    schedule = db_schedule + simulated_trips

    print(f"Fetched vehicle data: {schedule}")
    best_schedule = run_pso(schedule)
    print(f"----Best schedule for next drivers using PSO: {best_schedule}")
    return best_schedule

# Test the PSO function
best_schedule_pso = fetch_and_schedule_for_next_10_drivers_pso()
print(f"Best Schedule (PSO): {best_schedule_pso}")