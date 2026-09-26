import gurobipy as gp
from gurobipy import GRB
import time
import csv

# Create a list to store the results for all input files
results = []

try:
    with open("combined list coloring files.txt", "r") as file:
        filenames = file.read().splitlines()
    for filename in filenames:
        with open(filename, 'r') as file:
            no_of_vertices = []
            for line in file:
                if line.startswith('n'):
                    word = int(line.split('=')[1])
                    no_of_vertices.append(word)
        vertices = list(range(no_of_vertices[0]))
        colors = list(range(no_of_vertices[0]))

        with open(filename, 'r') as file:
            edges = []
            for line in file:
                if line.startswith('e'):
                    num = line.split()[1:]
                    edge = tuple(map(int, num))
                    edges.append(edge)

        with open(filename, 'r') as file:
            list_coloring = {}
            for line in file:
                if ":" in line:
                    parts = line.split(":")
                    vertex = int(parts[0].strip())
                    colors_str = parts[1].strip().split("\t")
                    colors_corr = [int(color) for color in colors_str]
                    list_coloring[vertex] = colors_corr

        print("vertices =", vertices)
        print("colors =", colors)
        print("edges =", edges)
        print("list coloring= ", list_coloring)

        # Model
        vc = gp.Model("VCP")

        # Variables
        x = []
        for v in vertices:
            x.append([vc.addVar(vtype=GRB.BINARY, name="X" + str(v) + " " + str(c)) for c in colors])
        y = []
        for c in colors:
            y.append(vc.addVar(vtype=GRB.BINARY, name="Y" + str(c)))

        #constraints
        for v in list_coloring.keys():
            valid_colors = list_coloring.get(v)
            vc.addConstr(gp.quicksum(x[v][c] for c in valid_colors) == 1)

        for v1 in range(len(vertices)):
            for v2 in range(len(vertices)):
                if (v1, v2) in edges:
                    for c in range(len(colors)):
                        vc.addConstr(x[v1][c] + x[v2][c] <= y[c])

        #objective
        vc.setObjective(gp.quicksum(y[c] for c in range(len(colors))), GRB.MINIMIZE)

        vc.setParam(GRB.Param.TimeLimit, 3600)
        start_time = time.time()

        #optimize
        vc.optimize()

        end_time = time.time()
        time_taken = end_time - start_time
        print(f"time = {time_taken}")
        best_objective = vc.ObjVal
        best_bound = vc.ObjBound

        # Calculate the gap percentage
        gap_percentage = 100 * (best_bound - best_objective) / best_bound
        print(f"gap = {gap_percentage:.2f}%")

        # Check status
        if vc.status == GRB.OPTIMAL:
            colors_used = []
            for c in range(len(colors)):
                if y[c].X == 1:
                    colors_used.append(colors[c])

            vertex_color = {}
            for v in range(len(vertices)):
                for c in range(len(colors)):
                    if x[v][c].X == 1:
                        if colors[c] not in vertex_color:
                            vertex_color[colors[c]] = []
                        vertex_color[colors[c]].append(vertices[v])

            result_instance = {
                "File Name": filename,
                "Colors Used": colors_used,
                "Total Colors Used": len(colors_used),
                "Vertex Color": vertex_color,
                "Objective Value": vc.ObjVal,
                "Time Taken": time_taken,
                "Gap Percentage": gap_percentage
            }

            results.append(result_instance)

            # Write result_instance to the CSV file
            with open("Result 60.csv", "a", newline="") as csv_file:
                fieldnames = ["File Name", "Colors Used", "Total Colors Used", "Vertex Color", "Objective Value", "Time Taken", "Gap Percentage"]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if csv_file.tell() == 0:
                    writer.writeheader()
                writer.writerow(result_instance)

        else:
            result_instance = {
                "File Name": filename,
                "Status": "No optimal solution for the problem"
            }
            results.append(result_instance)

            # Write result_instance to the CSV file
            with open("Result 60.csv", "a", newline="") as csv_file:
                fieldnames = ["File Name", "Status"]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                if csv_file.tell() == 0:
                    writer.writeheader()
                writer.writerow(result_instance)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))
except AttributeError:
    print('Encountered an attribute error.')