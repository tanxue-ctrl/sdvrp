from gurobipy import *
import numpy as np

# Define the SDVRPTW problem data
num_customers = 4
num_vehicles = 2
capacity = 600
service_time = [0, 15, 30, 19, 20]

time_window = [(0, 30), (0, 200), (50, 150), (60, 350), (0, 250)]

depot_location = (1350, 1288)
customer_locations = [(2007, 794), (2250, 1845), (650, 650), (450, 1500)]
dist_matrix = np.array([[0, 822, 1058.42, 947.12, 924.63],
                        [822, 0,1078.73, 1364.62,  1709.59],
                        [1058, 1078.73, 0, 1997, 1832.76],
                        [947.12, 1364.62, 1997, 0, 873.21],
                        [924.63, 1709.59, 1832.76, 873.21, 0]])
cost=np.array([[8.00, 	5789.95, 	8521.59, 	8565.34, 	5590.60],
               [5789.95, 	21.00, 	8684.42, 	12330.38, 	10314.60],
               [8521.59, 	8684.42, 	35.00, 	18033.35, 	11055.91],
               [8565.34, 	12330.38, 	18033.35, 	24.00, 	5281.15],
               [5590.60, 	10314.60, 	11055.91, 	5281.15, 	26.00]
               ])


demand = [0,287,377,336,200]
#create the model
model = Model('SDVRPTW')

# Create the decision variables
x = {}
u ={}
for i in range(num_customers + 1):
    for j in range(num_customers + 1):
        if i != j:
            for k in range(num_vehicles):
                x[i, j, k] = model.addVar(vtype=GRB.BINARY, name='x_%d,%d,%d' % (i, j, k))
                u[i, j, k] = model.addVar( ub=500,lb=0,name='u_%d,%d,%d' % (i, j, k))

# Create the objective function
obj = quicksum(cost[i, j] * x[i, j, k] for i in range(num_customers+1)
               for j in range(num_customers + 1) if i!=j for k in range(num_vehicles))
model.setObjective(obj, GRB.MINIMIZE)

# Create the constraints
for k in range(num_vehicles):
    # Constraint 1: Each customer is visited once by exactly one vehicle
    for j in range( num_customers + 1):
        model.addConstr(quicksum(x[i, j, k] for i in range(num_customers + 1) if i != j) == 1,
                        'customer %d visit once by vehicle %d' % (j, k))


    # Constraint 2: Each vehicle starts and ends at the depot
    model.addConstr(quicksum(x[i, 0, k] for i in range(1,num_customers + 1)) == 1,
                    'vehicle %d starts at depot' % k)
    model.addConstr(quicksum(x[0, j, k] for j in range(1,num_customers + 1)) == 1,
                    'vehicle %d ends at depot' % k)

for k in range(num_vehicles):
    # Constraint 1: Each customer is visited once by exactly one vehicle
    for i in range( num_customers + 1):
        model.addConstr(quicksum(x[i, j, k] for j in range(num_customers + 1) if i != j) == 1,
                        'customer %d visit once by vehicle %d' % (i, k))



# constraint 3: demand
for j in range(num_customers+1):
    model.addConstr(quicksum(u[i,j,k]*x[i,j,k] for i in range(num_customers+1) for k in range(num_vehicles) if i !=j)>=demand[j], "demand %d" %j)

# constraint 4: vehicle capacity
for k in range(num_vehicles):
    model.addConstr(quicksum(u[i,j,k]*x[i,j,k] for i in range(num_customers+1) for j in range(num_customers+1) if i !=j)<=capacity, "vehicle %d capacity" %k)


#时间窗约束
M = 1000 #max(dist_matrix.flatten())
t = model.addVars(num_customers + 1, num_vehicles, lb=0, ub=GRB.INFINITY, name='t')
service_times = [0, 15, 30, 19, 20]
for k in range(num_vehicles):
    model.addConstrs((t[i, k] + service_times[i] + dist_matrix[i][j]/20 - t[j, k]) <= M * (1 - x[i, j, k]) for i in range(num_customers + 1) for j in range(1,num_customers + 1) if i!=j)
    model.addConstrs(time_window[i][0] <= t[i, k] for i in range(num_customers + 1))
    model.addConstrs(t[i, k] <= time_window[i][1] for i in range(num_customers + 1))


model.optimize()

model.write("G:/tanxue/biyecode/sdvrp/a.lp")
print(model.status)
if model.status == GRB.Status.INFEASIBLE:
    print('Optimization was stopped with status %d' % model.status)
    # do IIS, find infeasible constraints
    model.computeIIS()
    model.write("model1.ilp")
    for c in model.getConstrs():
        if c.IISConstr:
            print('shi %s' % c.constrName)
    # print('No solution found')

# Print the optimal solution
if model.status == GRB.OPTIMAL:
    print('Objective value: %g' % model.objVal)
    for i in model.getVars():
        print(i)
