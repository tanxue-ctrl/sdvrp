import gurobipy as gp
from gurobipy import GRB

# Define the SDVRP problem data
num_vehicles = 2
depot = 0
num_customers = 4
capacity = 30
demands = [0, 5, 8, 5, 3]
costs = [[0, 4, 2, 5, 6],
         [4, 0, 1, 2, 3],
         [2, 1, 0, 3, 4],
         [5, 2, 3, 0, 3],
         [6, 3, 4, 3, 0]]

# Create a new model
model = gp.Model("SDVRP")

# Create decision variables
x = {}
for i in range(num_customers + 1):
    for j in range(num_customers + 1):
        for k in range(num_vehicles):
            x[i, j, k] = model.addVar(vtype=GRB.BINARY, name="x[%s,%s,%s]" % (i, j, k))

# Create capacity constraint
for k in range(num_vehicles):
    model.addConstr(gp.quicksum(demands[j] * x[i, j, k] for i in range(num_customers + 1) for j in range(num_customers + 1)) <= capacity)

# Create flow conservation constraints
for i in range(num_customers + 1):
    for k in range(num_vehicles):
        model.addConstr(gp.quicksum(x[i, j, k] for j in range(num_customers + 1)) - gp.quicksum(x[j, i, k] for j in range(num_customers + 1)) == 0)

# Create subtour elimination constraints
u = {}
for i in range(num_customers + 1):
    u[i] = model.addVar(lb=0, ub=num_customers, vtype=GRB.INTEGER, name="u[%s]" % i)

for k in range(num_vehicles):
    for i in range(num_customers + 1):
        for j in range(1, num_customers + 1):
            if i != j:
                model.addConstr(u[i] - u[j] + num_customers * x[i, j, k] <= num_customers - 1)

# Set objective function
model.setObjective(gp.quicksum(costs[i][j] * x[i, j, k] for i in range(num_customers + 1) for j in range(num_customers + 1) for k in range(num_vehicles)), GRB.MINIMIZE)

# Optimize the model
model.optimize()

# Print the optimal solution
if model.status == GRB.OPTIMAL:
    print('Objective value: %g' % model.objVal)
    for k in range(num_vehicles):
        print('Route for vehicle %s:' % k)
        route = [0]
        i = 0
        while True:
            for j in range(num_customers + 1):
                if x[i, j, k].X > 0.5:
                    route.append(j)
                    i = j
                    break
            if i == 0:
                break
        print(route)
else:
    print('No solution found')
