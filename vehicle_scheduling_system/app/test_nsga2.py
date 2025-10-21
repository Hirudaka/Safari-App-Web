from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
import numpy as np
from .genetic_algorithm import get_vehicle_data_from_db

class SafariSchedulingProblem(Problem):
    def __init__(self, schedule):
        # Define lower and upper bounds for the decision variables
        # Example: x[0] = start time, x[1] = speed, x[2] = route choice
        xl = np.array([8.0, 40.0, 0])  # Lower bounds
        xu = np.array([18.0, 100.0, 2])  # Upper bounds

        super().__init__(n_var=3, n_obj=3, n_constr=0, xl=xl, xu=xu)
        self.schedule = schedule

    def _evaluate(self, X, out, *args, **kwargs):
        F = []
        for x in X:
            fitness_value = self.fitness(x)
            F.append([fitness_value["time"], fitness_value["congestion"], fitness_value["violations"]])
        out["F"] = np.array(F)

    def fitness(self, x):
        # Extract decision variables
        start_time = x[0]  # Start time of the trip
        speed = x[1]  # Speed of the vehicle
        route_choice = int(x[2])  # Route choice (0, 1, or 2)

        # Calculate objectives based on the schedule and decision variables
        time = self.calculate_time(start_time, speed, route_choice)
        congestion = self.calculate_congestion(start_time, route_choice)
        violations = self.calculate_violations(start_time, speed, route_choice)

        return {
            "time": time,
            "congestion": congestion,
            "violations": violations,
        }

    def calculate_time(self, start_time, speed, route_choice):
        # Example: Calculate total trip time based on speed and route choice
        trip_time = self.schedule[route_choice]["trip_time"]
        return trip_time * (60 / speed)  # Convert to minutes

    def calculate_congestion(self, start_time, route_choice):
        # Example: Calculate congestion based on the schedule
        congestion_level = self.schedule[route_choice]["congestion"]
        return congestion_level

    def calculate_violations(self, start_time, speed, route_choice):
        # Example: Calculate violations (e.g., speeding, late arrival)
        violations = 0
        if speed > 80:  # Speeding violation
            violations += 1
        if start_time > 17.0:  # Late arrival violation
            violations += 1
        return violations

# Create an instance of your custom problem
# schedule = [
#     {"entry_time": 8.0, "trip_time": 2.0, "congestion": 0, "speed": [50, 55, 60]},
#     {"entry_time": 10.0, "trip_time": 1.5, "congestion": 1, "speed": [45, 50, 55]},
# ]
