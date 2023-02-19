import gurobipy as gp
from gurobipy import GRB

# Define the SDVRPTW problem data
n_customers = 4
n_vehicles = 2
max_route_duration = 20

# Customer data
# (id, x, y, demand, ready_time, due_time, service_time)
customers = [
    (1, 35, 35, 10, 0, 10, 2),
    (2, 40, 20, 15, 5, 15, 3),
    (3, 50, 25, 20, 0, 10, 4),
    (4, 30, 20, 5, 0, 5, 1),

]

# Vehicle data
vehicle_capacity = 30
vehicle_start_location = (0, 0)
vehicle_speed = 1

# Calculate distance matrix
distance_matrix = {}
for i in range(n_customers):
    for j in range(n_customers):
        xi, yi, _, _, _, _, _ = customers[i]
        xj, yj, _, _, _, _, _ = customers[j]
        distance_matrix[i, j] = ((xi - xj)**2 + (yi - yj)**2)**0.5

print(distance_matrix)
# Create the model
model = gp.Model('SDVRPTW')

# Create decision variables
x = {}
for i in range(n_customers):
    for j in range(n_customers):
        if i != j:
            for k in range(n_vehicles):
                x[i, j, k] = model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{j}_{k}')
print('x',x)
# Departure time from a customer node
t = {}
for i in range(n_customers):
    for k in range(n_vehicles):
        t[i, k] = model.addVar(lb=0, name=f't_{i}_{k}')

print('t',t)
# Create objective function
obj = gp.quicksum(distance_matrix[i, j] * x[i, j, k] for i in range(n_customers)
                  for j in range(n_customers) if i != j for k in range(n_vehicles))
model.setObjective(obj, GRB.MINIMIZE)

# Add constraints
# Constraint 1: Each customer is visited exactly once
for i in range(n_customers):
    model.addConstr(gp.quicksum(x[i, j, k] for j in range(n_customers) if i != j for k in range(n_vehicles)) == 1,
                    f'customer_{i}_visit_once')

# Constraint 2: The number of customers serviced does not exceed the vehicle capacity
for k in range(n_vehicles):
    model.addConstr(gp.quicksum(customers[i][3] * x[i, j, k] for i in range(n_customers) for j in range(n_customers)
                                if i != j) <= vehicle_capacity, f'vehicle_{k}_capacity')

# Constraint 3: A vehicle must start and end at the depot
for k in range(n_vehicles):
     model.addConstr(gp.quicksum(x[0, j, k] for j in range(1,n_customers)) == 1, f'vehicle_{k}_start')
     model.addConstr(gp.quicksum(x[i,0,k] for i in range(1,n_customers))==1)
# Optimize the model

model.optimize()

# Print the optimal solution
if model.status == GRB.OPTIMAL:
    print('Objective value: %g' % model.objVal)

    for i in model.getVars():
        print(i)

else:
    print('No solution found')
