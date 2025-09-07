import gurobipy as gp
from gurobipy import GRB

try:
    file = open("30v-100e.col", 'r') # saved the file in the same folder were this python file got saved
    lines = file.readlines()
    del lines[0:7]

    colors = list(range(1, 31))

    vertices = []
    ver = [int(num[2:4]) for num in lines]
    for x in ver:
        if x not in vertices:
            vertices.append(x)
    vertices.append(30)

    edges = [(int(num[2:4]), int(num[4:-1])) for num in lines]

    print("vertices =", vertices)
    print("colors =", colors)
    print("edges =", edges)

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
    for v in range(len(vertices)):
        vc.addConstr(gp.quicksum(x[v][c] for c in range(len(colors))) == 1)

    # C2
    for v1 in range(len(vertices)):
        for v2 in range(len(vertices)):
            if (v1, v2) in edges:
                for c in range(len(colors)):
                    vc.addConstr(x[v1][c] + x[v2][c] <= y[c])

    # Objective
    #git check_2
    vc.setObjective(gp.quicksum(y[c] for c in range(len(colors))), GRB.MINIMIZE)

    # Check status
    vc.optimize()
    status = vc.status

    #check status
    if status == GRB.OPTIMAL:
        print("The problem has optimal solution")

        output = open("30v-100e(output).txt", 'w')

        print("THE SOLUTION:")
        output.write("THE SOLUTION:\n")

        colors_used = []
        for c in range(len(colors)):
            if y[c].X == 1:
                colors_used.append(colors[c])
        print("Colors used =", colors_used)
        print("Total number of colors used =", len(colors_used))
        output.write("Colors used = {}\n".format(colors_used))
        output.write("Total number of colors used = {}\n".format(len(colors_used)))

        vertex_color = {}
        for v in range(len(vertices)):
            for c in range(len(colors)):
                if x[v][c].X == 1:
                    if colors[c] not in vertex_color:
                        vertex_color[colors[c]] = []
                    vertex_color[colors[c]].append(vertices[v])
        for c, v in vertex_color.items():
            print("Color", c, "-", "Vertices:", v)
            output.write("Color {} - Vertices: {}\n".format(c, v))

        print('Objective value (total number of colors used to color the graph) = %g' % vc.ObjVal)
        output.write("Objective value (total number of colors used to color the graph) = %g\n" % vc.ObjVal)
        output.close()

    else:
        print("No optimal solution for the problem")


    for v in vc.getVars():
        print('%s %g' % (v.VarName, v.X))
    print('Obj: %g' % vc.ObjVal)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))
except AttributeError:
    print('Encountered an attribute error.')