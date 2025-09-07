import gurobipy as gp
from gurobipy import GRB

try:
    with open("combined list coloring files.txt", "r") as file:
        filenames = file.read().splitlines()

    with open("combined(output).txt", "w") as output_file:

        for filename in filenames:
            with open(filename, 'r') as file:
                no_of_vertices = []
                for line in file:
                    if line.startswith('n'):
                        word = int(line.split('=')[1])
                        no_of_vertices.append(word)
                vertices = list(range(no_of_vertices[0]))
                colors = list(range(1, no_of_vertices[0]))

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

            # Constraints
            # C1
            for v in list_coloring.keys():
                valid_colors = list_coloring.get(v)
                vc.addConstr(gp.quicksum(x[v][c] for c in valid_colors) == 1)

            # C2
            for v1 in range(len(vertices)):
                for v2 in range(len(vertices)):
                    if (v1, v2) in edges:
                        for c in range(len(colors)):
                            vc.addConstr(x[v1][c] + x[v2][c] <= y[c])

            # Objective
            vc.setObjective(gp.quicksum(y[c] for c in range(len(colors))), GRB.MINIMIZE)

            # Set time limit
            vc.setParam(GRB.Param.TimeLimit, 1800)  # 1800 seconds = 30 minutes

            # Optimize
            vc.optimize()

            # Check status
            if vc.status == GRB.OPTIMAL:
                print("THE PROBLEM HAS AN OPTIMAL SOLUTION ")
                output_file.write(f"File Name: {filename} - ")

                colors_used = []
                for c in range(len(colors)):
                    if y[c].X == 1:
                        colors_used.append(colors[c])
                print("colors used = ", colors_used)
                output_file.write(f"Colors used = {colors_used} - ")
                print("total no of colors used = ", len(colors_used))

                vertex_color = {}
                for v in range(len(vertices)):
                    for c in range(len(colors)):
                        if x[v][c].X == 1:
                            if colors[c] not in vertex_color:
                                vertex_color[colors[c]] = []
                            vertex_color[colors[c]].append(vertices[v])

                print("vertex colors = ", vertex_color)
                print("Objective value = ", len(colors_used))
                output_file.write(f"Vertex Color: {vertex_color} - ")
                output_file.write(f"Objective value: {vc.ObjVal}\n")

            else:
                output_file.write(f"File Name: {filename} - No optimal solution for the problem\n")

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))
except AttributeError:
    print('Encountered an attribute error.')
