from app.pso import fetch_and_schedule_for_next_10_drivers_pso
from app.simulated_annealing import fetch_and_schedule_for_next_10_drivers_sa
from .genetic_algorithm import get_vehicle_data_from_db,fetch_and_schedule_for_next_10_drivers
from app.hybrid import fetch_and_schedule_for_next_10_drivers_hybrid

def run_all_algorithms(schedule):
    """
    Run all optimization algorithms (GA, SA, PSO, Hybrid) and return their results.

    Args:
        schedule (list): The initial schedule of vehicles.

    Returns:
        dict: A dictionary containing the results of each algorithm.
              Format: {"AlgorithmName": {"schedule": optimized_schedule, "fitness": fitness_value}}

    """


    # Run Genetic Algorithm
    ga_schedule = fetch_and_schedule_for_next_10_drivers()
    print("schedule1","\n")
    print(ga_schedule)
    ga_fitness = fitness(ga_schedule)

    # Run Simulated Annealing
    sa_schedule = fetch_and_schedule_for_next_10_drivers_sa()
    sa_fitness = fitness(sa_schedule)

    # Run PSO
    pso_schedule = fetch_and_schedule_for_next_10_drivers_pso()
    pso_fitness = fitness(pso_schedule)

    # Run Hybrid Algorithm
    hybrid_schedule = fetch_and_schedule_for_next_10_drivers_hybrid()
    hybrid_fitness = fitness(hybrid_schedule)
    mo_schedule = run_multi_objective_optimization(schedule)


    # Store results
    results = {
        "GA": {"schedule": ga_schedule, "fitness": ga_fitness},
        "SA": {"schedule": sa_schedule, "fitness": sa_fitness},
        "PSO": {"schedule": pso_schedule, "fitness": pso_fitness},
        "Hybrid": {"schedule": hybrid_schedule, "fitness": hybrid_fitness},
        "MO": {"schedule": mo_schedule, "fitness": fitness(mo_schedule)},
    }

    print("results","\n",results)
    return results

def compare_results(results):
    """
    Compare the results of all algorithms and return the best one.

    Args:
        results (dict): A dictionary containing the results of all algorithms.

    Returns:
        dict: A dictionary containing the best algorithm, schedule, and fitness value.
    """
    # Find the algorithm with the best (lowest) fitness value
    best_algorithm = min(results.keys(), key=lambda k: results[k]["fitness"])
    best_schedule = results[best_algorithm]["schedule"]
    best_fitness = results[best_algorithm]["fitness"]

    return {
        "best_algorithm": best_algorithm,
        "best_schedule": best_schedule,
        "best_fitness": best_fitness,
    }

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

from pymoo.core.problem import Problem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
import numpy as np

class SafariSchedulingProblem(Problem):
    def __init__(self, schedule):
        super().__init__(n_var=len(schedule), n_obj=3, n_constr=0)
        self.schedule = schedule

    def _evaluate(self, X, out, *args, **kwargs):
        F = []
        for x in X:
            fitness = fitness(x)
            F.append([fitness["time"], fitness["congestion"], fitness["violations"]])
        out["F"] = np.array(F)

def run_multi_objective_optimization(schedule):
    problem = SafariSchedulingProblem(schedule)
    algorithm = NSGA2(pop_size=100)
    res = minimize(problem, algorithm, ('n_gen', 200), verbose=True)
    return res.X