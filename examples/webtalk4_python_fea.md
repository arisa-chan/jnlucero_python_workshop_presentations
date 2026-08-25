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

1. What is FEA? From apps to elements
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

```pyxel-flow
direction=right
color=2
gap=12
Webtalk 1|Agentic coding
Webtalk 2|Task automation
Webtalk 3|Publishing apps
Webtalk 4|FEA in Python
```

<!-- incremental -->
Now that we know how to publish an app...

<!-- incremental -->

==**What goes inside a complex engineering app?**==

---

## Why Python for FEA?

`Compared to black-box GUI software`

<!-- incremental -->

- **Customizable:** inspect and modify *every* line
<!-- incremental -->
- **Open source:** no fees, math fully visible
<!-- incremental -->
- **Parametric:** change a variable, rerun, done
<!-- incremental -->
- **Ecosystem:** *numpy*, *scipy*, *matplotlib*

|||

<!-- incremental -->

col_widths=120,150
| Aspect | GUI | Python |
| --- | --- | --- |
| Cost | Fee | Free |
| Customize | Fixed | Unlimited |
| Automation | Macro | Native |
| Parametric | Clicks | Variable |
| Source | Closed | Open |

---

## Demystifying the black box

Every commercial FEA program reduces to one equation.

<!-- incremental -->

```pyxel-flow
direction=down
gap=14
color=2
F|what we apply
K|how the structure resists
d|what we solve for
```

<!-- incremental -->

==**F = K d**==

<!-- incremental -->

==**Goal of this talk:**== build the matrix stiffness method from scratch in Python, and watch the black box open up.

---

## What is finite element analysis?

`A numerical method for continuum problems`

<!-- incremental -->

*Continuum* (infinite unknowns) -> **discretize** -> *mesh* of elements + nodes -> **assemble** -> solve once.

<!-- incremental -->

```pyxel-canvas
width=300
height=104
bg=0
border=0
rect 12 22 116 64 color=15 fill=9 thickness=2
line 16 30 124 30 color=15
line 16 40 124 40 color=15
line 16 50 124 50 color=15
line 16 60 124 60 color=15
line 16 70 124 70 color=15
line 16 80 124 80 color=15
text 36 8 "continuum" color=1
text 12 92 "infinite unknowns" color=3
arrow 140 54 156 54 color=2 head=7 thickness=2
rect 168 22 116 64 color=1 thickness=2
line 168 22 284 22 color=14
line 168 43 284 43 color=14
line 168 64 284 64 color=14
line 168 86 284 86 color=14
line 168 22 168 86 color=14
line 197 22 197 86 color=14
line 226 22 226 86 color=14
line 255 22 255 86 color=14
line 284 22 284 86 color=14
line 168 22 197 43 color=14
line 197 22 226 43 color=14
line 226 22 255 43 color=14
line 168 43 197 64 color=14
line 197 43 226 64 color=14
line 226 43 255 64 color=14
line 168 64 197 86 color=14
line 197 64 226 86 color=14
line 226 64 255 86 color=14
circle 168 22 1 color=2 fill=2
circle 197 22 1 color=2 fill=2
circle 226 22 1 color=2 fill=2
circle 255 22 1 color=2 fill=2
circle 284 22 1 color=2 fill=2
circle 168 43 1 color=2 fill=2
circle 197 43 1 color=2 fill=2
circle 226 43 1 color=2 fill=2
circle 255 43 1 color=2 fill=2
circle 284 43 1 color=2 fill=2
circle 168 64 1 color=2 fill=2
circle 197 64 1 color=2 fill=2
circle 226 64 1 color=2 fill=2
circle 255 64 1 color=2 fill=2
circle 284 64 1 color=2 fill=2
circle 168 86 1 color=2 fill=2
circle 197 86 1 color=2 fill=2
circle 226 86 1 color=2 fill=2
circle 255 86 1 color=2 fill=2
circle 284 86 1 color=2 fill=2
text 204 8 "discretized" color=1
text 168 92 "finite unknowns" color=3
```

<!-- incremental -->

==**Trade-off:**== smaller elements -> more accurate, but more elements -> more computation.

---

## FEA dictionary: the model

`Discretization vocabulary`

<!-- incremental -->
- **Mathematical model** - governing equations + idealizations
<!-- incremental -->
- **Domain** - the physical region (plate, beam, truss)
<!-- incremental -->
- **Discretization** - continuous -> finite pieces
<!-- incremental -->
- **Mesh** - the elements + nodes covering the domain
<!-- incremental -->
- **Element size** *h* - smaller *h* = finer mesh = more compute

|||

<!-- incremental -->

```pyxel-canvas
width=172
height=124
bg=0
border=0
rect 20 28 132 80 color=1 thickness=2
line 20 48 152 48 color=14
line 20 68 152 68 color=14
line 20 88 152 88 color=14
line 53 28 53 108 color=14
line 86 28 86 108 color=14
line 119 28 119 108 color=14
line 53 28 86 48 color=14
line 86 28 119 48 color=14
line 119 28 152 48 color=14
line 20 48 53 68 color=14
line 53 48 86 68 color=14
line 86 48 119 68 color=14
line 119 48 152 68 color=14
line 20 68 53 88 color=14
line 53 68 86 88 color=14
line 86 68 119 88 color=14
line 119 68 152 88 color=14
line 20 88 53 108 color=14
line 53 88 86 108 color=14
line 86 88 119 108 color=14
line 119 88 152 108 color=14
line 20 28 53 28 color=7 thickness=2
line 53 28 53 48 color=7 thickness=2
line 20 28 53 48 color=7 thickness=2
line 20 18 53 18 color=7 thickness=2
line 20 18 20 28 color=7
line 53 18 53 28 color=7
text 30 8 "h" color=7
circle 20 28 2 color=2 fill=2
circle 152 28 2 color=2 fill=2
circle 20 108 2 color=2 fill=2
circle 152 108 2 color=2 fill=2
circle 53 28 2 color=2 fill=2
circle 53 48 2 color=2 fill=2
text 78 2 "mesh" color=1
text 8 116 "smaller h = finer mesh" color=3
```

---

## FEA dictionary: the computation

`From element to global equation`

<!-- incremental -->
- **Node** - where elements meet; displacements live here
<!-- incremental -->
- **Element** - one mesh piece; its stiffness *k* is computed here
<!-- incremental -->
- **Boundary condition** - supports (fixed DOFs) + loads (forces)
<!-- incremental -->
- **Finite element equation** - *k d = f* -> assembled *K d = F*
<!-- incremental -->
- **Assembly** - summing every *k* block into global *K*

|||

<!-- incremental -->

```pyxel-canvas
width=172
height=76
bg=0
border=0
line 24 58 132 58 color=14 thickness=2
line 24 58 24 14 color=14 thickness=2
line 132 58 24 14 color=14 thickness=2
circle 24 58 3 color=2
circle 132 58 3 color=2
circle 24 14 3 color=2
line 16 67 24 56 color=3
line 24 56 32 67 color=3
line 12 67 36 67 color=3
line 124 67 132 56 color=3
line 132 56 140 67 color=3
circle 127 70 2 color=3 fill=3
circle 137 70 2 color=3 fill=3
line 122 74 142 74 color=3
line 24 14 24 30 color=5 thickness=2
line 20 25 24 30 color=5 thickness=2
line 28 25 24 30 color=5 thickness=2
text 4 46 "1" color=1
text 140 46 "2" color=1
text 4 2 "3" color=1
```

```pyxel-canvas
width=172
height=108
bg=0
border=0
rect 50 12 12 12 color=9 fill=9
rect 62 12 12 12 color=9 fill=9
rect 74 12 12 12 color=9 fill=9
rect 86 12 12 12 color=9 fill=9
rect 50 24 12 12 color=9 fill=9
rect 62 24 12 12 color=9 fill=9
rect 74 24 12 12 color=9 fill=9
rect 86 24 12 12 color=9 fill=9
rect 50 36 12 12 color=9 fill=9
rect 62 36 12 12 color=9 fill=9
rect 74 36 12 12 color=9 fill=9
rect 86 36 12 12 color=9 fill=9
rect 50 48 12 12 color=9 fill=9
rect 62 48 12 12 color=9 fill=9
rect 74 48 12 12 color=9 fill=9
rect 86 48 12 12 color=9 fill=9
rect 50 12 12 12 color=12 fill=12
rect 62 12 12 12 color=12 fill=12
rect 98 12 12 12 color=12 fill=12
rect 110 12 12 12 color=12 fill=12
rect 50 24 12 12 color=12 fill=12
rect 62 24 12 12 color=12 fill=12
rect 98 24 12 12 color=12 fill=12
rect 110 24 12 12 color=12 fill=12
rect 50 60 12 12 color=12 fill=12
rect 62 60 12 12 color=12 fill=12
rect 98 60 12 12 color=12 fill=12
rect 110 60 12 12 color=12 fill=12
rect 50 72 12 12 color=12 fill=12
rect 62 72 12 12 color=12 fill=12
rect 98 72 12 12 color=12 fill=12
rect 110 72 12 12 color=12 fill=12
rect 74 36 12 12 color=5 fill=5
rect 86 36 12 12 color=5 fill=5
rect 98 36 12 12 color=5 fill=5
rect 110 36 12 12 color=5 fill=5
rect 74 48 12 12 color=5 fill=5
rect 86 48 12 12 color=5 fill=5
rect 98 48 12 12 color=5 fill=5
rect 110 48 12 12 color=5 fill=5
rect 74 60 12 12 color=5 fill=5
rect 86 60 12 12 color=5 fill=5
rect 98 60 12 12 color=5 fill=5
rect 110 60 12 12 color=5 fill=5
rect 74 72 12 12 color=5 fill=5
rect 86 72 12 12 color=5 fill=5
rect 98 72 12 12 color=5 fill=5
rect 110 72 12 12 color=5 fill=5
line 50 12 122 12 color=1
line 50 24 122 24 color=1
line 50 36 122 36 color=1
line 50 48 122 48 color=1
line 50 60 122 60 color=1
line 50 72 122 72 color=1
line 50 84 122 84 color=1
line 50 12 50 84 color=1
line 62 12 62 84 color=1
line 74 12 74 84 color=1
line 86 12 86 84 color=1
line 98 12 98 84 color=1
line 110 12 110 84 color=1
line 122 12 122 84 color=1
rect 50 12 72 72 color=1 thickness=2
text 64 38 "k1" color=15
text 52 22 "k2" color=1
text 86 64 "k3" color=1
text 56 2 "global K (6 x 6)" color=1
text 50 94 "K = k1 + k2 + k3" color=3
```

---

# Part 2

**The matrix stiffness method**

---

## Data structures for structural engineers

`Mesh -> arrays`

```pyxel-flow
direction=down
gap=8
color=2
nodes|np.array([[0,0],[4,0],[0,3]])
elements|[(0,1),(0,2),(1,2)]
E, A|200e6, 0.01
```

---

## The matrix stiffness method

`For one truss member, the local stiffness matrix is`

```pyxel-flow
direction=down
gap=8
color=2
k_local|(EA/L) * [[1,-1],[-1,1]]
transform|T^T * k_local * T
k_global|4x4 with c=cos, s=sin
```

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

Each member matrix lands in *K* at the rows/columns of its nodes.

```pyxel-flow
direction=down
gap=8
color=2
K = zeros(ndof, ndof)
dofs = [2*n1, 2*n1+1, 2*n2, 2*n2+1]
K[dofs, dofs] += k_global
```

<!-- incremental -->
`np.ix_` fancy indexing drops each 4x4 block into the 6x6 *K*. Members sharing a node simply add up.

---

## Boundary conditions

A structure needs supports, or *K* is singular.

<!-- incremental -->

```pyxel-flow
direction=right
gap=12
color=2
Method 1|partitioning|exact
Method 2|penalty|1e15
```

<!-- incremental -->
Partitioning: `d[free] = solve(K[free, free], F[free])`
<!-- incremental -->
Penalty: `K[fixed, fixed] += 1e15; d = solve(K, F)`

---

## The big picture

`From model to answers, in five steps`

<!-- incremental -->

```pyxel-flow
direction=down
gap=8
color=2
1. Nodes and elements|arrays
2. Global stiffness K|K += k_global
3. Loads and supports|F, fixed
4. Solve F = K d|np.linalg.solve
5. Forces and reactions|post-process
```

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

---

## The `scipy` library

`Sparse matrices`

Stiffness matrices are *mostly zeros*.

```pyxel-flow
direction=down
gap=8
color=2
K_sparse = csr_matrix(K)
Dense 800 DOFs|5.12 MB -> 20 GB at 50k
CSR sparse|0.04 MB -> ~150 MB at 50k
```

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

A 3-member pin-jointed truss. Node 1 pinned, node 2 on a roller, node 3 carries the loads.

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

```pyxel-flow
direction=down
gap=6
color=2
Small|follow by hand
Every FEA concept
Exact answers exist
3 members, 3 nodes, 6 DOFs
```

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

```pyxel-flow
direction=right
gap=10
color=2
Node 1|pin|u1=v1=0
Node 2|roller|v2=0
Node 3|free|u3, v3 unknown
```

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

```pyxel-flow
direction=down
gap=6
color=2
u2 = 0.010 mm
u3 = 0.0225 mm
v3 = -0.00938 mm
```

<!-- incremental -->
`Tiny displacements - exactly what steel-sized stiffness predicts.`

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

```pyxel-flow
direction=down
gap=8
color=2
OpenSeesPy|structural + earthquake|frames, nonlinear, time history
FEniCS|continuum mechanics|concrete stress, heat transfer
SfePy|pythonic finite elements|general PDEs, research
```

<!-- incremental -->
`Install and go: pip install openseespy`

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

```pyxel-flow
direction=down
gap=8
color=2
1. Define the mesh|nodes + elements
2. Assemble|weak-form matrices
3. Boundary conditions
4. Solve
5. Post-process
```

<!-- incremental -->
`If you understood Part 2, you already understand the engine inside these libraries.`

---

# Part 6

**Next steps**

---

## Tying it all together

`One engineer, four Webtalks, one complete product`

<!-- incremental -->

```pyxel-flow
direction=right
gap=12
color=2
Webtalk 1|debugging
Webtalk 2|automation
Webtalk 3|the UI
Webtalk 4|the engine
```

<!-- incremental -->
A Python FEA backend (today), wrapped in a UI (Webtalk 3), automated (Webtalk 2), debugged with agentic coding (Webtalk 1).

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
- Engineers who write their own tools are no longer limited by a menu.

<!-- incremental -->

```pyxel-flow
direction=down
gap=8
color=2
Buy solutions
Build them
```

==**Shift from buying solutions to building them.**==

---

## Next steps

<!-- incremental -->

```pyxel-flow
direction=down
gap=6
color=2
Github account
Read the docs
Build your own projects
Make mistakes
Ask questions
Verify AI results
Pick a specialization
Join a community
Keep learning
```

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
