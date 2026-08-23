# Developing Finite Element Analysis (FEA)<br/>Applications using Python

## Webtalk 4

<br/>Engr. Jaydee N. Lucero<br/>
Senior Structural Engineer I, Abinales Associates Engineers + Consultants

---

## Hi! I'm Jaydee.

- *Senior Structural Engineer I* (2021-present), Abinales Associates Engineers + Consultants
- *Part-time Review Instructor* (2019-present), Review Innovations
- *Associate Member* (2022-present), Association of Structural Engineers of the Philippines, Inc.
- *MS Civil Engineering (Structural Engineering) student* (2024-present), University of the Philippines Diliman
- `Pythonista since August 2024`

|||

![Jaydee Lucero](../picture_aboutme.png?scale=1.3)

---

## Outline

1. From apps to FEA
2. The matrix stiffness method
3. The Python FEA toolbox
4. Live code: a two-dimensional truss solver
5. Existing FEA frameworks
6. Next steps

---

## QR Codes

`Python 3.14 cheat sheet`

![Python 3.14 cheat sheet QR Code](../qr_codes/qrcode_cheatsheet.png?scale=1.2)

|||

`PDF and source code of presentation`

![Github repository](../qr_codes/qrcode_presentation.png?scale=1.2)

---

# Part 1

**From apps to FEA**

---

## The journey so far

In the previous Webtalks, we learned *how to ship software*.

<!-- incremental -->

| Webtalk | Topic | Its role today |
| --- | --- | --- |
| 1 | Agentic coding | Debugging the solver |
| 2 | Task automation | Batch parametric runs |
| 3 | Publishing apps | The UI wrapper |

<!-- incremental -->
Now that we know how to publish an app...

<!-- incremental -->

==**What goes inside a complex engineering app?**==

---

## Why Python for FEA?

`Compared to black-box GUI software`

<!-- incremental -->

- **Customizable:** You can inspect and modify *every* line.
<!-- incremental -->
- **Open source:** No license fees; the math is fully visible.
<!-- incremental -->
- **Parametric:** Change a variable, rerun the model, done.
<!-- incremental -->
- **Automation-ready:** Directly plugs into Webtalk 2 workflows.
<!-- incremental -->
- **Ecosystem:** *numpy*, *scipy*, *matplotlib* and specialized FEA libraries.

|||

<!-- incremental -->

col_widths=140,220
| Aspect | Black-box GUI | Python |
| --- | --- | --- |
| Cost | License fee | Free |
| Customize | Fixed menus | Unlimited |
| Automation | Macro scripts | Native loops |
| Parametric | Repeat clicks | One variable |
| Post-process | Built-in only | Any plot |
| Source | Closed | Open |

---

## Demystifying the black box

Every commercial FEA program reduces to one equation.

<!-- incremental -->

F = K d

<!-- incremental -->

- *F* - nodal forces (what we apply)
- *K* - global stiffness matrix (how the structure resists)
- *d* - nodal displacements (what we solve for)

<!-- incremental -->

==**Goal of this talk:**== build the matrix stiffness method from scratch in Python, and watch the black box open up.

---

# Part 2

**The matrix stiffness method**

---

## Data structures for structural engineers

`How to represent physical entities in code`

<!-- incremental -->
*Nodes:* arrays of X, Y, Z coordinates.

```python
import numpy as np

nodes = np.array([[0.0, 0.0],   # node 1: x, y
                  [4.0, 0.0],   # node 2
                  [0.0, 3.0]])  # node 3
```

<!-- incremental -->
*Elements:* connectivity arrays linking nodes.

```python
elements = [(0, 1), (0, 2), (1, 2)]   # node pairs
```

<!-- incremental -->
*Materials:* properties assigned to each element.

```python
E = 200e6    # elastic modulus (kN/m^2)
A = 0.01     # cross-section area (m^2)
I = 8e-6     # moment of inertia (m^4), for beams
```

---

## The matrix stiffness method

`For one truss member, the local stiffness matrix is`

k_local = (EA/L) * [[ 1, -1],
                    [-1,  1]]

<!-- incremental -->
It maps axial forces to axial displacements: F = k_local * d.

<!-- incremental -->
`Local to global transformation`

c = cos(theta) = (x2 - x1) / L<br/>
s = sin(theta) = (y2 - y1) / L

T = [[ c,  s,  0,  0],
     [ 0,  0,  c,  s]]

k_global = T^T * k_local * T

---

## The matrix stiffness method

`In Python, the transformed member matrix becomes`

```python
c, s = (x2 - x1) / L, (y2 - y1) / L

k_global = k * np.array([
    [ c*c,  c*s, -c*c, -c*s],
    [ c*s,  s*s, -c*s, -s*s],
    [-c*c, -c*s,  c*c,  c*s],
    [-c*s, -s*s,  c*s,  s*s],
])
```

<!-- incremental -->
A 4x4 matrix - two translational degrees of freedom per node.

---

## Global assembly

Each member matrix is placed into the *global* stiffness matrix *K* at the rows and columns of its nodes.

```python
ndof = 2 * len(nodes)          # 2 DOFs per node
K = np.zeros((ndof, ndof))

for n1, n2 in elements:
    ...
    dofs = [2*n1, 2*n1 + 1, 2*n2, 2*n2 + 1]
    K[np.ix_(dofs, dofs)] += k_global
```

<!-- incremental -->
`np.ix_` performs fancy indexing - it drops the 4x4 block into the correct place of the 6x6 *K*. Members sharing a node simply add up.

---

## Boundary conditions

A structure needs supports, or *K* is singular.

<!-- incremental -->
==Method 1: partitioning== (exact)

```python
fixed = [0, 1, 3]          # pinned DOFs
free = [d for d in range(ndof) if d not in fixed]

d[free] = np.linalg.solve(K[np.ix_(free, free)],
                          F[free])
```

<!-- incremental -->
==Method 2: penalty== (approximate, easier to automate)

```python
penalty = 1e15
K[fixed, fixed] += penalty
d = np.linalg.solve(K, F)
```

---

## The big picture

`From model to answers, in five steps`

<!-- incremental -->

| Step | Operation | Python |
| --- | --- | --- |
| 1 | Nodes and elements | arrays |
| 2 | Global stiffness *K* | `K += k_global` |
| 3 | Loads and supports | `F`, `fixed` |
| 4 | Solve F = K d | `np.linalg.solve` |
| 5 | Forces and reactions | post-process |

<!-- incremental -->
Steps 1-4 are the *engine*. Step 5 turns numbers back into engineering insight.

---

# Part 3

**The Python FEA toolbox**

---

## The `numpy` library

`The backbone of matrix operations`

Why plain Python lists are too slow:

```python
import time

K = [[(i + j) % 7 for j in range(500)]
     for i in range(500)]
v = [1.0] * 500

t_start = time.time()
for i in range(500):
    s = 0.0
    for j in range(500):
        s += K[i][j] * v[j]
t_end = time.time()
print(round(t_end - t_start, 4))    # ~0.05 s
```

---

## The `numpy` library

*numpy* stores numbers in contiguous C arrays and calls optimized BLAS kernels.

```python
import numpy as np

K = np.array(K, dtype='float')
v = np.array(v)

t_start = time.time()
K @ v
t_end = time.time()
print(round(t_end - t_start, 4))    # ~0.0004 s
```

<!-- incremental -->
`About 100 times faster - and it only gets better as the model grows.`

<!-- incremental -->
Real FEA matrices have thousands of rows, and we solve them hundreds of times.

---

## The `scipy` library

`Sparse matrices`

Stiffness matrices are *mostly zeros* - each node connects to only a few neighbors.

<!-- incremental -->

```python
from scipy.sparse import csr_matrix

K_sparse = csr_matrix(K)
print(K.nbytes)              # 5120000 bytes (dense)
print(K_sparse.data.nbytes)  # 38336 bytes (CSR)
```

<!-- incremental -->

col_widths=140,180
| Storage | 800 DOFs | 50,000 DOFs |
| --- | --- | --- |
| Dense | 5.12 MB | 20 GB |
| CSR sparse | 0.04 MB | ~150 MB |

<!-- incremental -->
`Less than 1% of the entries are non-zero. Sparse is not optional - it is the only way.`

---

## Solvers and post-processing

`Solving F = Kd`

<!-- incremental -->
```python
from scipy.linalg import solve            # dense
from scipy.sparse.linalg import spsolve   # sparse

d = solve(K_free, F_free)     # small models
d = spsolve(K_sparse, F)      # large models
```

<!-- incremental -->
`Post-processing with matplotlib`

```python
w, L = 10.0, 5.0
x = np.linspace(0, L, 100)
V = w * L / 2 - w * x            # shear
M = w * L / 2 * x - w * x**2 / 2 # moment
```

|||

<!-- incremental -->
`Shear and moment diagrams`

```pyxel-graph
width=160
height=110
bg=9
border=14
x=0,5
y=-30,35
grid=true
plot 25-10*x color=2 thickness=3
plot 25*x-5*x^2 color=5 thickness=3
```

<!-- incremental -->
*V = 25 - 10x* (color 2) and *M = 25x - 5x^2* (color 5) for a simply supported beam.

---

# Part 4

**Live code: a 2D truss solver**

---

## Live code: a 2D truss solver

### Problem setup

A 3-member pin-jointed truss. Node 1 is pinned, node 2 rests on a roller, and node 3 carries the loads.

E = 200e6 kN/m^2, A = 0.01 m^2

```pyxel-canvas
width=152
height=152
bg=0
border=0
line 24 124 128 124 color=14 thickness=2
line 24 124 24 32 color=14 thickness=2
line 128 124 24 32 color=14 thickness=2
circle 24 124 3 color=2
circle 128 124 3 color=2
circle 24 32 3 color=2
line 16 133 24 122 color=3
line 24 122 32 133 color=3
line 12 133 36 133 color=3
line 120 133 128 122 color=3
line 128 122 136 133 color=3
circle 123 136 2 color=3
circle 133 136 2 color=3
line 116 140 140 140 color=3
line 24 32 24 46 color=5 thickness=2
line 20 41 24 46 color=5 thickness=2
line 28 41 24 46 color=5 thickness=2
line 24 32 38 32 color=5 thickness=2
line 34 28 38 32 color=5 thickness=2
line 34 36 38 32 color=5 thickness=2
text 6 118 "1" color=1
text 132 118 "2" color=1
text 6 22 "3" color=1
text 66 116 "4 m" color=1
text 4 78 "3 m" color=1
text 62 62 "5 m" color=1
text 42 30 "5 kN" color=5
text 28 48 "10 kN" color=5
```

|||

<!-- incremental -->
`Why this example?`

<!-- incremental -->
- Small enough to follow by hand
<!-- incremental -->
- Exercises every FEA concept
<!-- incremental -->
- Exact answers exist for checking
<!-- incremental -->
- 3 members, 3 nodes, 6 DOFs, 5 lines of theory

---

## Live code: a 2D truss solver

==**Step 1**== Define nodes and elements.

```python
import numpy as np

nodes = np.array([[0.0, 0.0],   # node 1
                  [4.0, 0.0],   # node 2
                  [0.0, 3.0]])  # node 3
elements = [(0, 1), (0, 2), (1, 2)]
E, A = 200e6, 0.01

ndof = 2 * len(nodes)       # 6 DOFs
K = np.zeros((ndof, ndof))
```

<!-- incremental -->
`Each node owns two DOFs: ux (index 2n) and uy (index 2n+1).`

---

## Live code: a 2D truss solver

==**Step 2**== Generate and assemble the global stiffness matrix.

```python hl=6,7,8,9,10,11
for n1, n2 in elements:
    x1, y1 = nodes[n1]; x2, y2 = nodes[n2]
    L = np.hypot(x2 - x1, y2 - y1)
    c, s = (x2 - x1) / L, (y2 - y1) / L
    k = E * A / L
    k_global = k * np.array([
        [ c*c,  c*s, -c*c, -c*s],
        [ c*s,  s*s, -c*s, -s*s],
        [-c*c, -c*s,  c*c,  c*s],
        [-c*s, -s*s,  c*s,  s*s],
    ])
    dofs = [2*n1, 2*n1 + 1, 2*n2, 2*n2 + 1]
    K[np.ix_(dofs, dofs)] += k_global
```

<!-- incremental -->
`Three passes through the loop, three 4x4 blocks added into the 6x6 K.`

---

## Live code: a 2D truss solver

==**Step 3**== Apply loads and boundary conditions.

```python hl=4,5,6
F = np.zeros(ndof)
F[4] = 5.0       # u3 = 5 kN (right)
F[5] = -10.0     # v3 = -10 kN (down)

fixed = [0, 1, 3]     # u1, v1 (pin), v2 (roller)
free = [d for d in range(ndof) if d not in fixed]
```

<!-- incremental -->
Node 1 is pinned: both u1 and v1 are zero.
<!-- incremental -->
Node 2 is a roller: v2 is zero, but u2 is free to slide.
<!-- incremental -->
Node 3 is free: u3 and v3 are our unknowns.

---

## Live code: a 2D truss solver

==**Step 4**== Solve for the nodal displacements.

```python hl=3
d = np.zeros(ndof)
d[free] = np.linalg.solve(K[np.ix_(free, free)],
                          F[free])
print(d)
```

<!-- incremental -->

```python
# [ 0.000e+00  0.000e+00  1.000e-05  0.000e+00
#   2.250e-05 -9.375e-06]
```

<!-- incremental -->
u2 = 0.010 mm, u3 = 0.0225 mm, v3 = -0.00938 mm.

<!-- incremental -->
`Displacements are tiny - exactly what we expect from steel-sized stiffness.`

---

## Live code: a 2D truss solver

==**Step 5**== Back-calculate reactions and member forces.

```python hl=2,3
R = K @ d - F          # reactions at supports
print(R[fixed])        # [-5.    6.25  3.75] kN
```

<!-- incremental -->

```python
member_forces = []
for n1, n2 in elements:
    x1, y1 = nodes[n1]; x2, y2 = nodes[n2]
    L = np.hypot(x2 - x1, y2 - y1)
    c, s = (x2 - x1) / L, (y2 - y1) / L
    elong = (d[2*n2]*c + d[2*n2 + 1]*s) \
            - (d[2*n1]*c + d[2*n1 + 1]*s)
    member_forces.append(float(E * A / L * elong))
print(member_forces)   # [5.0, -6.25, -6.25] kN
```

---

## Live code: a 2D truss solver

### Visualization

`Original vs. deformed shape`

```python
import matplotlib.pyplot as plt

scale = 10000
deformed = nodes + scale * d.reshape(-1, 2)

fig, ax = plt.subplots()
for n1, n2 in elements:
    ax.plot([nodes[n1, 0], nodes[n2, 0]],
            [nodes[n1, 1], nodes[n2, 1]], "b-o")
    ax.plot([deformed[n1, 0], deformed[n2, 0]],
            [deformed[n1, 1], deformed[n2, 1]], "r--")
ax.set_aspect("equal")
ax.set_title("Original vs. deformed shape")
```

|||

```pyxel-canvas
width=152
height=152
bg=0
border=0
line 24 124 128 124 color=14
line 24 124 24 32 color=14
line 128 124 24 32 color=14
line 24 124 138 124 color=5 thickness=2
line 24 124 47 44 color=5 thickness=2
line 138 124 47 44 color=5 thickness=2
circle 24 124 3 color=14
circle 128 124 3 color=14
circle 24 32 3 color=14
circle 138 124 3 color=5
circle 47 44 3 color=5
text 4 142 "deformed shape x40000" color=1
```

---

# Part 5

**Existing FEA frameworks**

---

## Don't reinvent the wheel

Custom matrix code is perfect for *learning* and *specialized apps*.

<!-- incremental -->
But real 3D projects need robust, battle-tested libraries.

<!-- incremental -->

| Library | Strength | Typical use |
| --- | --- | --- |
| OpenSeesPy | Structural & earthquake | Frames, nonlinear, time history |
| FEniCS | Continuum mechanics | Concrete stress, heat transfer |
| SfePy | Pythonic finite elements | General PDEs, research |

<!-- incremental -->
`Install and go:`

```python
pip install openseespy
```

---

## The `openseespy` library

`The industry standard for advanced structural engineering`

<!-- incremental -->
The same 3-member truss, in OpenSeesPy:

```python
import openseespy.opensees as ops

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 2)  # 2D truss: ux, uy

ops.node(1, 0.0, 0.0)
ops.node(2, 4.0, 0.0)
ops.node(3, 0.0, 3.0)
ops.fix(1, 1, 1)     # pin
ops.fix(2, 0, 1)     # roller (v2 fixed)

ops.uniaxialMaterial('Elastic', 1, 200e6)
ops.element('Truss', 1, 1, 2, 0.01, 1)
ops.element('Truss', 2, 1, 3, 0.01, 1)
ops.element('Truss', 3, 2, 3, 0.01, 1)
```

|||

<!-- incremental -->
Loads and analysis:

```python
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(3, 5.0, -10.0)

ops.constraints('Plain')
ops.numberer('Plain')
ops.system('BandGeneral')
ops.algorithm('Linear')
ops.analysis('Static')
ops.analyze(1)

print(ops.nodeDisp(3))      # displacements
print(ops.nodeReaction(1))  # reactions
```

<!-- incremental -->
`Nonlinear materials, pushover, earthquake time history - all just commands away.`

---

## `fenics` and `sfepy`

`For continuum mechanics`

<!-- incremental -->
When the problem is a *volume*, not a *skeleton*:

<!-- incremental -->
- Concrete stress distribution
- Heat conduction and diffusion
- Fluid-structure interaction

<!-- incremental -->
The same workflow still applies:

<!-- incremental -->

1. Define the mesh (nodes + elements)
<!-- incremental -->
2. Assemble the weak-form matrices
<!-- incremental -->
3. Apply boundary conditions
<!-- incremental -->
4. Solve
<!-- incremental -->
5. Post-process

<!-- incremental -->
`If you understood Part 2, you already understand the engine inside these libraries.`

---

# Part 6

**Next steps**

---

## Tying it all together

`One engineer, four Webtalks, one complete product`

<!-- incremental -->

| Webtalk | Skill | Role in your FEA app |
| --- | --- | --- |
| 1 | Agentic coding | Debugging the solver |
| 2 | Task automation | Batch parametric studies |
| 3 | Publishing apps | The user interface |
| 4 | FEA in Python | The engine inside |

<!-- incremental -->
A Python FEA backend (today), wrapped in a UI and deployed to the web (Webtalk 3), debugged with agentic coding (Webtalk 1).

<!-- incremental -->
==**That is an app.**==

---

## The future of structural engineering

`From software consumers to software developers`

<!-- incremental -->
- Commercial software solves *common* problems well.
<!-- incremental -->
- Your projects will have problems nobody has coded yet.
<!-- incremental -->
- Engineers who can write their own tools are no longer limited by what a menu offers.
<!-- incremental -->
- Every line you write is a new capability for the profession.

<!-- incremental -->
==**Shift from buying solutions to building them.**==

---

## Next steps

<!-- incremental -->
1. Create your Github account.
<!-- incremental -->
2. Read the library documentation **a lot**.
<!-- incremental -->
3. Stop coding examples. Start building your own projects.
<!-- incremental -->
4. Feel free to make mistakes.
<!-- incremental -->
5. Feel free to ask questions.
<!-- incremental -->
6. When using AI, `always` verify the results.
<!-- incremental -->
7. Find your desired specialization (e.g. structural analysis, earthquake engineering, AI/ML, software and game development, etc).
<!-- incremental -->
8. Join a community (e.g. Reddit, Discord, community groups, etc).
<!-- incremental -->
9. Continue learning.

---

## Closing

This presentation was created using a heavily modified version of [Pyxel slides](https://github.com/shimizukawa/pyxel-slide-pyasia-2026), which I learned at PythonAsia 2026 from the presentation of [Takayuki Shimizukawa](https://github.com/shimizukawa). Special thanks to Shimizukawa-sensei for creating such an amazing tool!

`Contact me`

- Email: [jaydee.lucero@gmail.com](mailto:jaydee.lucero@gmail.com)
- Facebook: [facebook.com/jaydee.lucero](https://www.facebook.com/jaydee.lucero)
- Linkedin: [linkedin.com/in/jaydee-lucero-977070200](https://www.linkedin.com/in/jaydee-lucero-977070200)
- Github: [github.com/arisa-chan](https://github.com/arisa-chan)
- Website: [engrjaydee.com](https://engrjaydee.com/)

|||

`PDF and source code of presentation`

![Github repository](../qr_codes/qrcode_presentation.png?scale=1.2)

---

# Thank you very much!

**Do you have any questions?**
