from gurobipy import *
import numpy as np

# Define the SDVRPTW problem data
num_customers = 4
num_vehicles = 2
capacity = 20
service_time = [0, 2, 2, 2, 2]
time_window = [(0, 10), (1, 15), (5, 20), (10, 30), (0, 30)]
depot_location = (0, 0)
customer_locations = [(1, 1), (1, 5), (5, 5), (5, 1)]
dist_matrix = np.array([[0, 1, 5, 5, 2],
                        [1, 0, 4, 5, 3],
                        [5, 4, 0, 6, 7],
                        [5, 5, 6, 0, 7],
                        [2, 3, 7, 7, 0]])
demand = [0,3,6,4,3]
#create the model
model = Model('SDVRPTW')

# Create the decision variables
x = {}
for i in range(num_customers + 1):
    for j in range(num_customers + 1):
        if i != j:
            for k in range(num_vehicles):
                x[i, j, k] = model.addVar(vtype=GRB.BINARY, name='x_%d,%d,%d' % (i, j, k))

#
# obj = gp.quicksum(distance_matrix[i, j] * x[i, j, k] for i in range(n_customers)
#                   for j in range(n_customers) if i != j for k in range(n_vehicles))
# model.setObjective(obj, GRB.MINIMIZE)

# Create the objective function
obj = quicksum(dist_matrix[i, j] * x[i, j, k] for i in range(num_customers+1)
               for j in range(num_customers + 1) if i!=j for k in range(num_vehicles))
model.setObjective(obj, GRB.MINIMIZE)


# Create the constraints
for k in range(num_vehicles):
    # Constraint 1: Each customer is visited once by exactly one vehicle
    for j in range( num_customers + 1):
        model.addConstr(quicksum(x[i, j, k] for i in range(num_customers + 1) if i != j) == 1,
                        'customer %d visit once by vehicle %d' % (j, k))

    # Constraint 2: The number of customers served by each vehicle cannot exceed its capacity
    model.addConstr(demand[i]*quicksum(x[i, j, k] for i in range(num_customers + 1) for j in range(1, num_customers + 1) if i!=j) <= capacity,
                    'vehicle %d capacity' % k)

    # Constraint 3: Each vehicle starts and ends at the depot
    model.addConstr(quicksum(x[i, 0, k] for i in range(1,num_customers + 1)) == 1,
                  'vehicle %d starts at depot' % k)
    model.addConstr(quicksum(x[0, j, k] for j in range(1,num_customers + 1)) == 1,
                    'vehicle %d ends at depot' % k)

M = max(dist_matrix.flatten())
t = model.addVars(num_customers + 1, num_vehicles, lb=0, ub=GRB.INFINITY, name='t')
service_times = [0, 1, 2, 1, 3]
model.addConstrs((t[i, k] + service_times[i] + dist_matrix[i][j] - t[j, k]) <= M * (1 - x[i, j, k]) for i in range(num_customers + 1) for j in range(1,num_customers + 1) if i!=j)
model.addConstrs(time_window[i][0] <= t[i, k] for i in range(num_customers + 1))
model.addConstrs(t[i, k] <= time_window[i][1] for i in range(num_customers + 1))


model.optimize()

# Print the optimal solution
if model.status == GRB.OPTIMAL:
    print('Objective value: %g' % model.objVal)

    # for i in model.getVars():
    #     print(i)

else:
    print('No solution found')
