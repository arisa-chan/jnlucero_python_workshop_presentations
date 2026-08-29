# %%
#
# BEYOND BRIDGE CONSTRUCTION SIMULATOR:
# THE MATH, MECHANICS AND MACHINES BEHIND BRIDGE SIMULATOR GAMES
# Sample backend code
#
# ver 1.0
# by Engr. Jaydee N. Lucero
# November 19, 2025
#

# Import libraries
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as shp
from IPython.display import display, clear_output, Markdown
from numpyarray_to_latex import to_ltx

# Truss geometry (base units kN and m)
nodes = [
    ("A", (0, 0)),
    ("B", (12, 0)),
    ("C", (30, 0)),
    ("D", (42, 0)),
    ("E", (6, 8)),
    ("F", (21, 8)),
    ("G", (36, 8)),
]

members = [
    ("A", "B"),
    ("B", "C"),
    ("C", "D"),
    ("E", "F"),
    ("F", "G"),
    ("A", "E"),
    ("E", "B"),
    ("B", "F"),
    ("F", "C"),
    ("C", "G"),
    ("G", "D"),
]

forces = [
    ("B", (0, -100)), 
    ("C", (0, -150))
]

supports = [
    ("A", ("fixed", "fixed")), 
    ("D", ("free", "fixed"))
]

A_mem = 0.1**2 - (0.1 - 0.006 * 2) ** 2     # Cross-section area of each member
E_mem = 200e6                               # Modulus of elasticity
scale = 100                                 # Scale to amplify deflected shape in plots

node_names = [w[0] for w in nodes]

# %%
# 
# Plot the undeformed truss.
#

fig, ax = plt.subplots()

# Plot the joints.
for node in nodes:
    x = node[1][0] + 0.1
    y = node[1][1] + 0.05
    ax.plot(*node[1], color="black", marker="o", linewidth=5)
    ax.text(x, y, node[0])

# Plot the members.
for member in members:
    start_node, end_node = member
    start_coord = nodes[node_names.index(start_node)][1]
    end_coord = nodes[node_names.index(end_node)][1]
    ax.plot(*zip(start_coord, end_coord), color="black", linewidth=2)

# Plot the supports.
for support in supports:
    node_name = support[0]
    node_support = support[1]

    # pinned support
    if node_support[0] == "fixed" and node_support[1] == "fixed":
        supp_node_1 = np.array(nodes[node_names.index(node_name)][1])
        supp_node_2 = supp_node_1 + np.array([-1, -2])
        supp_node_3 = supp_node_1 + np.array([1, -2])
        ax.add_artist(shp.Polygon([supp_node_1, supp_node_2, supp_node_3]))

    # roller support
    elif node_support[0] == "free" and node_support[1] == "fixed":
        supp_node_1 = np.array(nodes[node_names.index(node_name)][1])
        radius = 1
        center = supp_node_1 - np.array([0, radius])
        ax.add_artist(shp.Circle(center, radius))

# Plot the loads.
for force in forces :
    node_name = force[0]
    nodal_force = np.array(force[1], dtype='float')
    scale_force = 20
    node_loc = np.array(nodes[node_names.index(node_name)][1], dtype='float')

    ax.add_artist(shp.Arrow(*node_loc, *(nodal_force/scale_force), color='red'))

ax.set_xlabel(rf"$x$ (m)")
ax.set_ylabel(rf"$y$ (m)")
ax.axis("equal")

# %%
#
# Analyze the truss.
#
np.set_printoptions(linewidth=np.inf)   # Write results in a single line.

# Transformed element stiffness matrix.
def k_element(node_1, node_2, E=1, A=1):
    dx = node_2[0] - node_1[0]
    dy = node_2[1] - node_1[1]
    L = np.sqrt(dx**2 + dy**2)          # Element length
    theta = np.atan2(dy, dx)            # Element angle from +x-axis
    
    # Constructing the matrix.
    cc = np.cos(theta) ** 2
    cs = np.sin(theta) * np.cos(theta)
    ss = np.sin(theta) ** 2
    return np.array([
        [cc, cs, -cc, -cs],
        [cs, ss, -cs, -ss],
        [-cc, -cs, cc, cs],
        [-cs, -ss, cs, ss],
    ], dtype="float")*E*A/L

# Containers for global matrices
# Degrees of freedom = 2*n, where n is the number of nodes.
Kg = np.zeros((2 * len(node_names), 2 * len(node_names)))   # stiffness
Fg = np.zeros(2 * len(node_names))                          # nodal forces

# Set up the structure global stiffness matrix.
for member in members:
    # For each member, calculate the transformed element stiffness matrix.
    start_node, end_node = member
    start_coord = nodes[node_names.index(start_node)][1]
    end_coord = nodes[node_names.index(end_node)][1]
    k_elem = k_element(start_coord, end_coord, E=E_mem, A=A_mem)
    # The gather array.
    l_elem = np.zeros((4, 2 * len(node_names)))
    l_elem[0, 2 * node_names.index(start_node)] = 1
    l_elem[1, 2 * node_names.index(start_node) + 1] = 1
    l_elem[2, 2 * node_names.index(end_node)] = 1
    l_elem[3, 2 * node_names.index(end_node) + 1] = 1
    # Assembly.
    Kg_elem = l_elem.T @ k_elem @ l_elem
    Kg += Kg_elem

# Set up the global nodal force vector.
for force in forces:
    node_no = node_names.index(force[0])
    Fg[2 * node_no] = force[1][0]           # x-direction
    Fg[2 * node_no + 1] = force[1][1]       # y-direction

# Set up the condensed global matrix equation.
Kg_cond = np.copy(Kg)
for support in supports:
    node_no = node_names.index(support[0])
    # x-direction
    if support[1][0] == "fixed":
        # Zero out all rows and columns.
        Kg_cond[2 * node_no, :] = 0
        Kg_cond[:, 2 * node_no] = 0
        # And assign 1 to the main diagonal.
        Kg_cond[2 * node_no, 2 * node_no] = 1
    # y-direction
    if support[1][1] == "fixed":
        Kg_cond[2 * node_no + 1, :] = 0
        Kg_cond[:, 2 * node_no + 1] = 0
        Kg_cond[2 * node_no + 1, 2 * node_no + 1] = 1

display(Markdown(rf"$\mathbf{{K}} = {to_ltx(Kg, brackets="[]")}$"))
display(Markdown(rf"$\mathbf{{F}} = {to_ltx(Fg, brackets="[]")}$"))
display(Markdown(rf"$\mathbf{{K}}_\text{{cond}} = {to_ltx(Kg_cond, brackets="[]")}$"))

# Calculate the nodal displacements.
ug = np.linalg.inv(Kg_cond) @ Fg
display(Markdown(rf"$\mathbf{{u}} = {to_ltx(ug, brackets="[]")}$"))

# 
# Plot the deformed configuration.
#
new_nodes = []
new_nodes_scaled = []
for node_no, node in enumerate(nodes):
    # Nodal coordinates of deformed shape for further calculations.
    new_node = np.array(node[1], dtype="float") + np.array(
        [ug[2 * node_no], ug[2 * node_no + 1]], dtype="float"
    )
    new_nodes.append(new_node)

    # Nodal coordinates of deformed shape for plotting.
    # Scaled to exaggerate displacements.
    new_node_scaled = np.array(node[1], dtype="float") + scale * np.array(
        [ug[2 * node_no], ug[2 * node_no + 1]], dtype="float"
    )
    new_nodes_scaled.append(new_node_scaled)

    x = new_node_scaled[0] + 0.1
    y = new_node_scaled[1] + 0.05
    ax.plot(*new_node_scaled, color="blue", marker="o", linewidth=5)
    ax.text(x, y, "{0}'".format(node_names[node_no]), color="blue")

for member in members:
    start_node, end_node = member
    start_coord = new_nodes_scaled[node_names.index(start_node)]
    end_coord = new_nodes_scaled[node_names.index(end_node)]
    ax.plot(*zip(start_coord, end_coord), color="blue", linestyle="dashed", linewidth=2)

display(fig)

# %%
# 
# Calculate member forces.
#

# Container for axial forces in each member.
axial = []

for member in members:
    start_node, end_node = member
    start_node_no = node_names.index(start_node)
    end_node_no = node_names.index(end_node)

    # Collect displacements for each node.
    u_element = np.array([
            ug[2 * start_node_no],
            ug[2 * start_node_no + 1],
            ug[2 * end_node_no],
            ug[2 * end_node_no + 1],
    ], dtype="float")

    # Calculate end reactions.
    f_element = (
        k_element(nodes[start_node_no][1], nodes[end_node_no][1], E=E_mem, A=A_mem)
        @ u_element
    )

    # Transform to internal forces.
    dx = nodes[end_node_no][1][0] - nodes[start_node_no][1][0]
    dy = nodes[end_node_no][1][1] - nodes[start_node_no][1][1]
    L = np.sqrt(dx**2 + dy**2)
    theta = np.atan2(dy, dx)
    c = np.cos(theta)
    s = np.sin(theta)

    t_mat = np.array([          # Transformation matrix.
        [c, s, 0, 0], 
        [-s, c, 0, 0], 
        [0, 0, c, s], 
        [0, 0, -s, c]
    ], dtype="float")

    axial_element = t_mat @ f_element
    axial.append(axial_element[2])

display(Markdown(rf"$\mathbf{{P}}_\text{{cond}} = {to_ltx(axial, brackets="[]")}$"))

# %%
# 
# Extra 1: Plot members in tension and compression.
# 

fig, ax = plt.subplots()

# Plot the joints.
for node in nodes:
    x = node[1][0] + 0.1
    y = node[1][1] + 0.05
    ax.plot(*node[1], color="black", marker="o", linewidth=5)
    ax.text(x, y, node[0])

# Plot the members.
for member_no, member in enumerate(members):
    start_node, end_node = member
    start_coord = nodes[node_names.index(start_node)][1]
    end_coord = nodes[node_names.index(end_node)][1]

    # Key code for this part.
    ax.plot(*zip(start_coord, end_coord),
        color="red" if axial[member_no] > 0 else "blue" if axial[member_no] < 0 else "black",
        linewidth=2,
    )

# Plot the supports.
for support in supports:
    node_name = support[0]
    node_support = support[1]

    # pinned
    if node_support[0] == "fixed" and node_support[1] == "fixed":
        supp_node_1 = np.array(nodes[node_names.index(node_name)][1])
        supp_node_2 = supp_node_1 + np.array([-0.25, -0.5])
        supp_node_3 = supp_node_1 + np.array([0.25, -0.5])
        ax.add_artist(shp.Polygon([supp_node_1, supp_node_2, supp_node_3]))

    # roller support
    elif node_support[0] == "free" and node_support[1] == "fixed":
        supp_node_1 = np.array(nodes[node_names.index(node_name)][1])
        radius = 0.25
        center = supp_node_1 - np.array([0, radius])
        ax.add_artist(shp.Circle(center, radius))

ax.set_xlabel(rf"$x$ (m)")
ax.set_ylabel(rf"$y$ (m)")
ax.axis("equal")
# %%
# 
# Extra 2: Plot members exceeding certain force value.
#

# Maximum axial force in the member.
axial_max = 110

fig, ax = plt.subplots()

# Plot the joints.
for node in nodes:
    x = node[1][0] + 0.1
    y = node[1][1] + 0.05
    ax.plot(*node[1], color="black", marker="o", linewidth=5)
    ax.text(x, y, node[0])

# Plot the members.
for member_no, member in enumerate(members):
    start_node, end_node = member
    start_coord = nodes[node_names.index(start_node)][1]
    end_coord = nodes[node_names.index(end_node)][1]

    # Key code for this part.
    ax.plot(
        *zip(start_coord, end_coord),
        color="red" if abs(axial[member_no]) > axial_max 
                    else "pink" if 0.75*axial_max < abs(axial[member_no]) <= axial_max
                    else "green" if 0.5*axial_max < abs(axial[member_no]) <= 0.75*axial_max
                    else "yellow",
        linewidth=2,
    )

# Plot the supports.
for support in supports:
    node_name = support[0]
    node_support = support[1]

    # pinned
    if node_support[0] == "fixed" and node_support[1] == "fixed":
        supp_node_1 = np.array(nodes[node_names.index(node_name)][1])
        supp_node_2 = supp_node_1 + np.array([-0.25, -0.5])
        supp_node_3 = supp_node_1 + np.array([0.25, -0.5])
        ax.add_artist(shp.Polygon([supp_node_1, supp_node_2, supp_node_3]))

    # roller support
    elif node_support[0] == "free" and node_support[1] == "fixed":
        supp_node_1 = np.array(nodes[node_names.index(node_name)][1])
        radius = 0.25
        center = supp_node_1 - np.array([0, radius])
        ax.add_artist(shp.Circle(center, radius))

ax.set_xlabel(rf"$x$ (m)")
ax.set_ylabel(rf"$y$ (m)")
ax.axis("equal")

#######################
# END OF CODE LISTING #
#######################
