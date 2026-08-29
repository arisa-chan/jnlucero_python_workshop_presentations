# Developing Finite Element Analysis Applications<br/>using Python

## ASEP Webinar Series 2026-2027 W01

<br/>Engr. Jaydee N. Lucero<br/>
Senior Structural Engineer I<br/>Abinales Associates Engineers + Consultants

---

## Hi! I'm Jaydee.

- *Senior Structural Engineer I* (2021-present), Abinales Associates Engineers + Consultants
- *Part-time Review Instructor* (2019-present), Review Innovations
- *Associate Member* (2022-present), Association of Structural Engineers of the Philippines, Inc.
- *MS Civil Engineering (Structural Engineering) student* (2024-present), University of the Philippines Diliman
- ==Pythonista since August 2024==

|||

![Jaydee Lucero](../picture_aboutme.png?scale=1.15)

---

## Outline

1. Introduction
2. Finite element analysis concepts
3. Python libraries from scratch
4. ==Example 1== A two-dimensional truss analysis program
5. Python FEA libraries
6. ==Example 2== A two-dimensional isolated foundation design program
7. Next steps

---

## QR Codes

Python 3.14 cheat sheet

![Python 3.14 cheat sheet QR Code](../qr_codes/qrcode_cheatsheet.png?scale=1.1)

|||

PDF and source code of presentation

![Github repository](../qr_codes/qrcode_presentation.png?scale=1.1)

---

# Part 1

**Introduction**

---

## A quick recap

<!-- incremental -->
```pyxel-flow
direction=down
color=2
gap=12
Webtalk 1|Coding and agentic coding using Python
Webtalk 2|Task automation using Python
Webtalk 3|Publishing apps using Python
```

<!-- incremental -->
We can make our structural engineering programs even more sophisticated.

<!-- incremental -->

```pyxel-flow
direction=down
color=2
gap=12
Webtalk 4|Finite element analysis using Python
```

---

## Why Python for FEA?

<!-- incremental -->
Compared to black-box FEA software, an FEA program created using programming languages like Python can be

<!-- incremental -->
- `Customizable`<br/>Inspect and modify *every* line
<!-- incremental -->
- `Open-source`<br/>No fees, math fully visible
<!-- incremental -->
- `Parametric`<br/>Change a variable, rerun, done
<!-- incremental -->
- `Ecosystem`<br/>*numpy*, *scipy*, *matplotlib*, *openseespy*, *pyniteFEA*, etc.

|||

<!-- incremental -->

col_widths=0
| Aspect | GUI | Python |
| --- | --- | --- |
| Cost | Fee | Free |
| Customize | Fixed | Unlimited |
| Automation | Macro | Native |
| Parametric | Clicks | Variable |
| Source | Closed | Open |

---

## Demystifying the black box
<!-- incremental -->
Every commercial FEA program reduces to just one equation.
<!-- incremental -->
> **KU** = **F** + **Q**

<!-- incremental -->

```pyxel-flow
direction=down
gap=14
color=2
F, Q|what we apply
K|how the structure resists
U|what we solve for
```

<!-- incremental -->

In this talk, we will build FEA programs in two ways: 
<!-- incremental -->
- ==from scratch== using basic Python libraries, and
<!-- incremental -->
- ==from Python FEA libraries==

---

# Part 2

**Finite element analysis concepts**

---

## What is finite element analysis?
<!-- incremental -->
> Instead of providing the infinite number of solutions as in the exact solutions, the ==finite element concept== is to determine solutions only at some finite locations. This is done by first discretizing the geometry of the model into a number of finite elements... These elements are connected at grid points or nodes at which the unknowns are to be determined (Dechaumpai, 2024).
<!-- incremental -->
> The key idea of ==finite element method== is to transform the differential equations into a set of algebraic equations for each element. The finite element equations from all elements are then assembled together to form a large set of simultaneous equations. The boundary conditions of the problem are applied prior to solving for the unknowns at all nodes (Dechaumpai, 2024).

---

## What is finite element analysis?
<!-- incremental -->
![alt text](/ASEP%20Webinar%20Series%20W01/FEA_bridge.png?scale=0.65)
<!-- incremental -->
![alt text](/ASEP%20Webinar%20Series%20W01/FEA_steel_platform.png?scale=0.8)

|||
<!-- incremental -->
![alt text](/ASEP%20Webinar%20Series%20W01/FEA_aerodynamics_car.png?scale=0.7)
<!-- incremental -->
![alt text](/ASEP%20Webinar%20Series%20W01/FEA_thermal.png?scale=0.8)

---

## What is finite element analysis?


<!-- incremental -->
```pyxel-flow
direction=right
color=2
gap=12
Continuum|
Discretization|
Finite element|equations
Assembly|
Solve|
```
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

---

## What is finite element analysis?

<!-- incremental -->

- <u>Smaller elements</u> -> more accurate, but more elements -> more computational time

<!-- incremental -->
- <u>Larger elements</u> -> less elements, but less accuracy -> less computational time

<!-- incremental -->
```pyxel-canvas
width=380
height=200
bg=2
align=center

# --- LEFT SIDE: COARSE MESH ---
# Coarse grid lines
line 20 65 125 65 color=5
line 20 90 130 90 color=5
line 20 115 125 115 color=5
line 45 40 45 140 color=5
line 70 40 70 140 color=5
line 95 40 95 140 color=5
line 120 40 120 140 color=5

# Mask the hole to clear the grid inside it
circle 70 90 14 color=0 fill=0

# Draw coarse plate boundaries and hole
line 20 40 120 40 color=7
line 20 140 120 140 color=7
line 20 40 20 140 color=7
curve 120,40 150,90 150,90 120,140 color=7 steps=5
circle 70 90 15 color=7

# Label
text 35 160 "Coarse Mesh" color=7 size=2

# --- RIGHT SIDE: FINE MESH ---
# Fine grid lines (Horizontal)
line 220 50 322 50 color=13
line 220 60 326 60 color=13
line 220 70 332 70 color=13
line 220 80 336 80 color=13
line 220 90 338 90 color=13
line 220 100 336 100 color=13
line 220 110 332 110 color=13
line 220 120 326 120 color=13
line 220 130 322 130 color=13

# Fine grid lines (Vertical)
line 230 40 230 140 color=13
line 240 40 240 140 color=13
line 250 40 250 140 color=13
line 260 40 260 140 color=13
line 280 40 280 140 color=13
line 290 40 290 140 color=13
line 300 40 300 140 color=13
line 310 40 310 140 color=13
line 320 40 320 140 color=13

# Mask the hole to clear the grid inside it
circle 270 90 14 color=0 fill=0

# Draw fine plate boundaries and hole
line 220 40 320 40 color=7
line 220 140 320 140 color=7
line 220 40 220 140 color=7
curve 320,40 350,90 350,90 320,140 color=7 steps=16
circle 270 90 15 color=7

# Label
text 245 160 "Fine Mesh" color=7 size=2
```

---

## Some terms

<!-- incremental -->
`Mathematical model`
- A differential equation or a set of differential equations that mimic the behavior of a natural or physical system.
<!-- incremental -->
`Domain`
- Everything that is in the system, including geometry, loads, constraints.
<!-- incremental -->
`Node`
- A point in the domain.
<!-- incremental -->
`Element`
- A group of adjacent nodes that are related to each other by the mathematical model.
<!-- incremental -->
`Discretization`
- The process of dividing the domain into nodes and elements.

|||
<!-- incremental -->
`Finite element mesh`
- The result of discretization, a collection of nodes and elements approximating the domain. 
<!-- incremental -->
`Element size`
- Distance between two nodes in an element, denoted by *h*.

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

## Some terms

<!-- incremental -->
`Boundary`
- Edge (2D) or surface (3D) of the domain.
<!-- incremental -->
`Boundary conditions`
- Loads and constraints that occur at the boundary.
<!-- incremental -->
`Finite element equation`
- A matrix equation derived from the <u>integral formulation</u> of a mathematical model.
<!-- incremental -->
- Takes the form ==**ku = f + q**==. Small letters denote that it is for an element. Here,
    - **k** = stiffness matrix
    - **u** = displacements vector
    - **f** = point load vector
    - **q** = distributed load vector

|||

<!-- incremental -->
`Assembly`
- Combining the finite element equations from all elements into a single finite element equation for the domain. 
<!-- incremental -->
- Takes the form ==**KU = F + Q**==. The capital letters denote that it is for the whole structure.

<!-- incremental -->
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

# Part 3

**Python FEA from scratch**

---

## Basic Python FEA concepts

<!-- incremental -->
### General procedure
<!-- incremental -->
```pyxel-flow
direction=right
gap=8
color=2
1|dimensions, DOF
2|nodes
3|elements
4|materials
5|sections
```


```pyxel-flow
direction=right
gap=8
color=2
6|constraints
7|loads
8|post-processors
9|solver options
10|RUN ANALYSIS
```
<!-- incremental -->
### Nodes
<!-- incremental -->
Nodes can be represented as a list/tuple,
<!-- incremental -->
```python
coords = [(0, 0, 0), (0, 6, 0), (6, 0, 0), (2, 2, 4)]
```
<!-- incremental -->
...or as a dictionary,
<!-- incremental -->
```python
coords = {"P1": (0, 0, 0), "P2": (0, 6, 0), "P3": (6, 0, 0), "P4": (2, 2, 4)}
```
<!-- incremental -->
...or as an instance of a class.
<!-- incremental -->
```python
class Node:
    def __init__(self, x, y, z, id) :
        self.x, self.y, self.z, self.id = x, y, z, id

P1 = Node(0, 0, 0, "P1")
```

---

## Basic Python FEA concepts

### Elements
<!-- incremental -->
Depending on your representation of nodes, your representation of elements will differ.
<!-- incremental -->
```python
# Assuming using two-node bar elements.

# as list/tuples
elements = [(0, 3), (1, 3), (2, 3)]

# as dictionaries
elements = {"E1": ("P1", "P4"), "E2": ("P2", "P4"), "E3": ("P3", "P4")}

# as class instances
class Element:
    def __init__(self, start, end):
        self.start, self.end = start, end

E1 = Element(P1, P4)
```

---

## Basic Python FEA concepts

### Element finite element equations
<!-- incremental -->
- To estimate the response of the system between nodes, <u>interpolation functions</u> are used.
<!-- incremental -->
- `First-order elements` are elements that use linear functions as interpolating functions.
<!-- incremental -->
- `Second-order elements` are elements that use quadratic functions as interpolating functions.
<!-- incremental -->
```pyxel-canvas
width=500
height=130
align=center

# Grid Labels
text 0 35 "1st-Order" color=1
text 0 95 "2nd-Order" color=1
text 125 5 "1D" color=1
text 275 5 "2D" color=1
text 435 5 "3D" color=1

# --- 1D LINE ELEMENT ---
# Linear (2-node)
line 100 38 160 38 color=5
circle 100 38 3 fill=12 color=1
circle 160 38 3 fill=12 color=1

# Quadratic (3-node)
line 100 98 160 98 color=5
circle 100 98 3 fill=12 color=1
circle 160 98 3 fill=12 color=1
circle 130 98 3 fill=10 color=1

# --- 2D QUADRILATERAL ELEMENT ---
# Linear (4-node)
line 250 18 310 18 color=5
line 310 18 310 58 color=5
line 310 58 250 58 color=5
line 250 58 250 18 color=5
circle 250 18 3 fill=12 color=1
circle 310 18 3 fill=12 color=1
circle 310 58 3 fill=12 color=1
circle 250 58 3 fill=12 color=1

# Quadratic (8-node serendipity)
line 250 78 310 78 color=5
line 310 78 310 118 color=5
line 310 118 250 118 color=5
line 250 118 250 78 color=5
# Corners
circle 250 78 3 fill=12 color=1
circle 310 78 3 fill=12 color=1
circle 310 118 3 fill=12 color=1
circle 250 118 3 fill=12 color=1
# Mid-edges
circle 280 78 3 fill=10 color=1
circle 310 98 3 fill=10 color=1
circle 280 118 3 fill=10 color=1
circle 250 98 3 fill=10 color=1

# --- 3D TETRAHEDRAL ELEMENT ---
# Linear (4-node)
line 440 10 410 55 color=5
line 440 10 470 55 color=5
line 440 10 445 35 color=5
line 410 55 470 55 color=5
line 410 55 445 35 color=5
line 470 55 445 35 color=5
circle 440 10 3 fill=12 color=1
circle 410 55 3 fill=12 color=1
circle 470 55 3 fill=12 color=1
circle 445 35 3 fill=12 color=1

# Quadratic (10-node)
line 440 70 410 115 color=5
line 440 70 470 115 color=5
line 440 70 445 95 color=5
line 410 115 470 115 color=5
line 410 115 445 95 color=5
line 470 115 445 95 color=5
# Corners
circle 440 70 3 fill=12 color=1
circle 410 115 3 fill=12 color=1
circle 470 115 3 fill=12 color=1
circle 445 95 3 fill=12 color=1
# Mid-edges
circle 425 92 3 fill=10 color=1
circle 455 92 3 fill=10 color=1
circle 442 82 3 fill=10 color=1
circle 440 115 3 fill=10 color=1
circle 427 105 3 fill=10 color=1
circle 457 105 3 fill=10 color=1
```
<!-- incremental -->
- Refer to FEA books (e.g. Reddy) on per-element finite element equations in matrix form.

---

## Basic Python FEA concepts

### Assembly
<!-- incremental -->
```pyxel-canvas
width=480
height=240
bg=0
align=center

# --- TITLE & PHYSICAL MESH ---
text 40 15 "Direct Stiffness Assembly Mapping" color=4
line 300 15 360 15 color=5
circle 300 15 4 color=7 fill=8
circle 330 15 4 color=7 fill=10
circle 360 15 4 color=7 fill=12
text 298 5 "1" color=4
text 328 5 "2" color=4
text 358 5 "3" color=4
text 380 13 "Physical Mesh" color=5

# --- ELEMENT 1 LOCAL MATRIX (Red) ---
text 40 50 "Element 1 (K^1)" color=8
rect 41 71 18 18 color=8 fill=8
rect 61 71 18 18 color=8 fill=8
rect 41 91 18 18 color=8 fill=8
rect 61 91 18 18 color=8 fill=8
# Element 1 Grid
line 40 70 80 70 color=5
line 40 90 80 90 color=5
line 40 110 80 110 color=5
line 40 70 40 110 color=5
line 60 70 60 110 color=5
line 80 70 80 110 color=5

# --- ELEMENT 2 LOCAL MATRIX (Blue) ---
text 40 140 "Element 2 (K^2)" color=12
rect 41 161 18 18 color=12 fill=12
rect 61 161 18 18 color=12 fill=12
rect 41 181 18 18 color=12 fill=12
rect 61 181 18 18 color=12 fill=12
# Element 2 Grid
line 40 160 80 160 color=5
line 40 180 80 180 color=5
line 40 200 80 200 color=5
line 40 160 40 200 color=5
line 60 160 60 200 color=5
line 80 160 80 200 color=5

# --- GLOBAL STIFFNESS MATRIX ---
text 280 40 "Global Stiffness Matrix (K^G)" color=4

# Mapped Element 1 contributions
rect 281 61 18 18 color=8 fill=8
rect 301 61 18 18 color=8 fill=8
rect 281 81 18 18 color=8 fill=8

# Mapped Element 2 contributions
rect 321 81 18 18 color=12 fill=12
rect 301 101 18 18 color=12 fill=12
rect 321 101 18 18 color=12 fill=12

# Superposition (Overlap at Node 2)
rect 301 81 18 18 color=10 fill=10

# Global Matrix Grid (4x4 to show boundary)
line 280 60 360 60 color=5
line 280 80 360 80 color=5
line 280 100 360 100 color=5
line 280 120 360 120 color=5
line 280 140 360 140 color=5
line 280 60 280 140 color=5
line 300 60 300 140 color=5
line 320 60 320 140 color=5
line 340 60 340 140 color=5
line 360 60 360 140 color=5

# Global DOF Labels
text 287 52 "1" color=5
text 307 52 "2" color=5
text 327 52 "3" color=5
text 347 52 "4" color=5
text 270 67 "1" color=5
text 270 87 "2" color=5
text 270 107 "3" color=5
text 270 127 "4" color=5

# --- MAPPING ARROWS ---
arrow 90 90 270 80 color=8 head=6
arrow 90 180 270 100 color=12 head=6

# --- LEGEND ---
rect 280 170 10 10 color=8 fill=8
text 295 172 "Element 1 DOF Map" color=4
rect 280 190 10 10 color=12 fill=12
text 295 192 "Element 2 DOF Map" color=4
rect 280 210 10 10 color=10 fill=10
text 295 212 "Superposition at Node 2 (Addition)" color=4
```

---

## Basic Python FEA concepts

### Applying boundary conditions
<!-- incremental -->
```pyxel-canvas
width=480
height=210
bg=0
align=center

# --- TITLE & CONTEXT ---
text 20 15 "Applying Boundary Conditions (Direct Elimination)" color=4
text 20 30 "Fixed support at Node 1 (D1 = 0). Eliminate Row 1 and Col 1." color=10

# --- HIGHLIGHT ACTIVE PARTITIONS ---
# Left Side Active Zones
rect 44 104 72 72 color=1 fill=1
rect 140 104 24 72 color=1 fill=1
rect 200 104 24 72 color=1 fill=1

# Right Side Active Zones (Reduced System)
rect 310 104 72 72 color=1 fill=1
rect 400 104 24 72 color=1 fill=1
rect 450 104 24 72 color=1 fill=1

# --- LEFT SIDE: FULL SYSTEM [K]{D}={F} ---
text 60 55 "[ K ]" color=4
text 142 55 "{ D }" color=4
text 202 55 "{ F }" color=4
text 178 124 "=" color=7 size=2

# K Matrix Grid (4x4)
line 20 80 116 80 color=5
line 20 104 116 104 color=5
line 20 128 116 128 color=5
line 20 152 116 152 color=5
line 20 176 116 176 color=5
line 20 80 20 176 color=5
line 44 80 44 176 color=5
line 68 80 68 176 color=5
line 92 80 92 176 color=5
line 116 80 116 176 color=5

# D Vector Grid (4x1)
line 140 80 164 80 color=5
line 140 104 164 104 color=5
line 140 128 164 128 color=5
line 140 152 164 152 color=5
line 140 176 164 176 color=5
line 140 80 140 176 color=5
line 164 80 164 176 color=5

# F Vector Grid (4x1)
line 200 80 224 80 color=5
line 200 104 224 104 color=5
line 200 128 224 128 color=5
line 200 152 224 152 color=5
line 200 176 224 176 color=5
line 200 80 200 176 color=5
line 224 80 224 176 color=5

# Matrix Dummy Variables (to show what is deleted)
text 25 88 "k11" color=6
text 49 88 "k12" color=6
text 73 88 "k13" color=6
text 97 88 "k14" color=6
text 25 112 "k21" color=6
text 25 136 "k31" color=6
text 25 160 "k41" color=6

# Vector Values
text 148 88 "0" color=10
text 146 112 "D2" color=7
text 146 136 "D3" color=7
text 146 160 "D4" color=7

text 206 88 "R1" color=10
text 206 112 "F2" color=7
text 206 136 "F3" color=7
text 206 160 "F4" color=7

# Strike-throughs (Red)
line 15 92 121 92 color=8 thickness=2
line 32 75 32 181 color=8 thickness=2
line 135 92 169 92 color=8 thickness=2
line 195 92 229 92 color=8 thickness=2

# --- TRANSFORMATION ARROW ---
arrow 245 128 290 128 color=10 head=6 thickness=2
text 248 114 "Reduce" color=10

# --- RIGHT SIDE: REDUCED SYSTEM ---
text 330 79 "[ K_red ]" color=4
text 392 79 "{ D_red }" color=4
text 442 79 "{ F_red }" color=4
text 431 136 "=" color=7 size=2

# Reduced K Matrix Grid (3x3)
line 310 104 382 104 color=5
line 310 128 382 128 color=5
line 310 152 382 152 color=5
line 310 176 382 176 color=5
line 310 104 310 176 color=5
line 334 104 334 176 color=5
line 358 104 358 176 color=5
line 382 104 382 176 color=5

# Reduced D Vector Grid (3x1)
line 400 104 424 104 color=5
line 400 128 424 128 color=5
line 400 152 424 152 color=5
line 400 176 424 176 color=5
line 400 104 400 176 color=5
line 424 104 424 176 color=5

# Reduced F Vector Grid (3x1)
line 450 104 474 104 color=5
line 450 128 474 128 color=5
line 450 152 474 152 color=5
line 450 176 474 176 color=5
line 450 104 450 176 color=5
line 474 104 474 176 color=5

# Reduced Vector Values
text 406 112 "D2" color=7
text 406 136 "D3" color=7
text 406 160 "D4" color=7

text 456 112 "F2" color=7
text 456 136 "F3" color=7
text 456 160 "F4" color=7
```

---

## Basic Python FEA concepts

### Python libraries
<!-- incremental -->
- `numpy` for matrix creation and operations. Install using `pip install numpy`.
<!-- incremental -->
```python hl=1,7,11,13
import numpy as np                  # Import the numpy library.

k1, k2 = 4000, 6000
K = [[ k1,     -k1,   0],
     [-k1, k1 + k2, -k2],
     [  0,     -k2,  k2]]
K = np.array(K, dtype='float')      # Create the numpy array.

f1, f2 = 3000, 5000
F = [f1, f1 + f2, f2]
F = np.array(F, dtype='float').T    # Create the numpy array, then transpose.

U = np.linalg.inv(K) @ F            # Solve the system [K]{U} = {F} using matrix inverse method 
print(U)                            # {U} = [K]^-1 {F}.
```

---

## Basic Python FEA concepts

### Python libraries
<!-- incremental -->
- `scipy` for faster matrix operations, especially for <u>sparse arrays</u>. Install using `pip install scipy`.
<!-- incremental -->
- A `sparse array` is a type of matrix in which most of the entries are zero.
<!-- incremental -->
[Example from here](https://docs.scipy.org/doc/scipy/reference/sparse.html)

```python
import numpy as np
from scipy.sparse import csr_array                  # Import the scipy library.

A = csr_array([[1, 2, 0], [0, 0, 3], [4, 0, 5]])    # Create a compressed sparse row array.
v = np.array([1, 0, -1])
u = A @ v
print(u)
```

---

# Part 4

**Example 1: A two-dimensional truss analysis program**

---

## A two-dimensional truss program

```pyxel-canvas
width=480
height=270
align=center

# --- TITLE ---
text 20 15 "Example" color=1 size=2

# --- DIMENSIONS ---
# Vertical 8m
line 112 114 25 114 color=1
line 70 170 25 170 color=1
arrow 35 142 35 114 color=1 head=4
arrow 35 142 35 170 color=1 head=4
text 10 140 "8 m" color=1

# Horizontal 12m, 18m, 12m (Placed clearly under the truss)
text 105 185 "12 m" color=1
text 210 185 "18 m" color=1
text 315 185 "12 m" color=1

# --- TRUSS MEMBERS ---
line 70 170 154 170 color=1 thickness=2
line 154 170 280 170 color=1 thickness=2
line 280 170 364 170 color=1 thickness=2
line 70 170 112 114 color=1 thickness=2
line 112 114 154 170 color=1 thickness=2
line 154 170 217 114 color=1 thickness=2
line 112 114 217 114 color=1 thickness=2
line 217 114 280 170 color=1 thickness=2
line 217 114 322 114 color=1 thickness=2
line 322 114 280 170 color=1 thickness=2
line 322 114 364 170 color=1 thickness=2

# --- SUPPORTS ---
# Pin at A
area 70,173 60,188 80,188 color=1 fill=1
text 85 175 "Pin" color=1
# Roller at D
area 364,173 354,185 374,185 color=1 fill=1
line 350 189 378 189 color=1 thickness=2
text 370 175 "Roller" color=1

# --- HINGE INDICATOR ---
arrow 185 95 212 110 color=1 head=4
text 155 90 "Hinge" color=1

# --- NODES ---
# Using white fill (7) so they pop against the navy outlines
circle 70 170 3 color=1 fill=7 thickness=2
circle 154 170 3 color=1 fill=7 thickness=2
circle 280 170 3 color=1 fill=7 thickness=2
circle 364 170 3 color=1 fill=7 thickness=2
circle 112 114 3 color=1 fill=7 thickness=2
circle 217 114 3 color=1 fill=7 thickness=2
circle 322 114 3 color=1 fill=7 thickness=2

# Node Labels (Moved away from the lines)
text 40 155 "A (0, 0)" color=1
text 160 155 "B (12, 0)" color=1
text 285 155 "C (30, 0)" color=1
text 370 155 "D (42, 0)" color=1
text 100 100 "E (6, 8)" color=1
text 210 100 "F (21, 8)" color=1
text 320 100 "G (36, 8)" color=1

# --- APPLIED LOADS (DOWNWARD) ---
arrow 154 173 154 215 color=1 head=4 thickness=2
text 140 220 "100 kN" color=1
arrow 280 173 280 215 color=1 head=4 thickness=2
text 265 220 "150 kN" color=1

# --- REACTIONS ---
arrow 35 170 65 170 color=1 head=4 thickness=2
text 20 175 "AH" color=1
arrow 70 215 70 190 color=1 head=4 thickness=2
text 75 205 "AV" color=1
arrow 364 215 364 190 color=1 head=4 thickness=2
text 368 205 "BV" color=1

# --- CROSS SECTION DETAIL ---
text 360 15 "steel tubular section" color=1
rect 390 30 40 40 color=1 thickness=3
rect 395 35 30 30 color=1 thickness=2
text 365 35 "6 mm" color=1
arrow 365 48 390 48 color=1 head=3
arrow 415 48 395 48 color=1 head=3
text 435 45 "100 mm" color=1
text 395 75 "100 mm" color=1

# --- EQUATIONS ---
text 20 235 "A = 0.1^2 - (0.1 - 2 * 0.006)^2 = 0.002256 m^2" color=1
text 20 250 "E = 200 GPa = 200 * 10^6 kPa" color=1
```

---

# Part 5

**Python FEA libraries**

---

## Python FEA libraries

![alt text](/ASEP%20Webinar%20Series%20W01/FEA_libraries.png?scale=1.3)

---

## The `openseespy` library
<!-- incremental -->
==OpenSees (Open System for Earthquake Engineering Simulation)== is a software framework for developing applications to simulate the performance of structural and geotechnical systems subjected to earthquakes, developed by the Pacific Earthquake Engineering Research (PEER) Center.
<!-- incremental -->
```bash
# Install the main library.
pip install openseespy

# Install results visualization engine.
pip install opsvis      # using matplotlib
pip install vfo         # using pyvista
```

|||
<!-- incremental -->
![alt text](/ASEP%20Webinar%20Series%20W01/FEA_SSI_model.png?scale=0.65)
<!-- incremental -->
![alt text](/ASEP%20Webinar%20Series%20W01/FEA_SSI_output.png?scale=0.69)

Soil-structure interaction.

---

## The `openseespy` library

<!-- incremental -->
==Example==
<!-- incremental -->
```python
import openseespy.opensees as ops
ops.wipe()

# Create a two-dimensional model with two
# degrees of freedom only (translation x, y).
ops.model('basic', '-ndm', 2, '-ndf', 2)

# Create nodes.
ops.node(1, 0.0, 0.0)
ops.node(2, 4.0, 0.0)
ops.node(3, 0.0, 3.0)

# Create boundary conditions.
ops.fix(1, 1, 1)     # pinned support
ops.fix(2, 0, 1)     # roller support

# Create material for each member.
ops.uniaxialMaterial('Elastic', 1, 200e6)

# Create elements and assign material.
ops.element('Truss', 1, 1, 2, 0.01, 1)
ops.element('Truss', 2, 1, 3, 0.01, 1)
ops.element('Truss', 3, 2, 3, 0.01, 1)
```

|||
<!-- incremental -->
```python
# Create loads
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(3, 5.0, -10.0)     # point load

# Analysis options
ops.constraints('Plain')
ops.numberer('Plain')
ops.system('BandGeneral')
ops.algorithm('Linear')     # linear analysis
ops.analysis('Static')      # static analysis
ops.analyze(1)

# Extract results.
print(ops.nodeDisp(3))      # displacements
print(ops.nodeReaction(1))  # reactions
```

---

# Part 6

**Example 2: An isolated footing design program**

---

## Isolated footing program

### Sample output

![Output program](/ASEP%20Webinar%20Series%20W01/FEA_Example%202_output.png?scale=1.4)

---

## Isolated footing program

### Prompt

> Take the role of a structural engineer with several years of experience in the analysis, design and detailing of structures of various heights and lengths (horizontal/vertical). ==Create a GUI program in Python using the PySide6 library== that does the following.<br/><br/>Accept as inputs: <br/>(a) 28-day compressive strength of concrete fc', <br/>(b) reinforcement yield strength fy, <br/>(c) soil bearing capacity SBC (kPa), <br/>(d) column dimensions along x and y directions (rectangular), <br/>(e) column eccentricity from center of footing along x and y directions, <br/>(f) factored service loads at column (Ps, Msx, Msy, Vsx, Vsy, Ts), <br/>(g) factored ultimate loads at column (Pu, Mux, Muy, Vux, Vuy, Tu), <br/>(h) footing maximum finite element size.

---

## Isolated footing program

### Prompt

> Accept as output: <br/>(a) a three-dimensional visualization of the footing, <br/>(b) upon pressing [Analyze and Design], create a finite element model using OpenSeesPy library,<br/>----> take the subgrade modulus as 120 times the SBC<br/>----> use compression-only springs to model the soil<br/>----> the stiffness of horizontal springs is 10% of the stiffness of vertical springs, <br/>----> consider the actual stiffness of the plate elements (rather than rigid body assumption) when analyzing the footing<br/>(c) report the following (display contour plots in three-dimensional visualization):<br/>----> settlement (in mm),<br/>----> soil pressure (in kPa), <br/>(d) design the footing based on NSCP 2015 provisions, increase sizes iteratively where needed:<br/>----> footing dimension in the x- and y- directions,<br/>----> footing thickness from one-way and two-way shear checks<br/>----> footing reinforcement from one-way moment checks in each direction.

---

# Part 7

**Next steps**

---

## Putting it all together

<!-- incremental -->

```pyxel-flow
direction=down
gap=12
color=8
Webtalk 1|Code in Python and use AI
Webtalk 2|Automate engineering stuff
Webtalk 3|Create and publish applications
Webtalk 4|Create advanced applications using FEA
*** AN AMAZING APP ***
```

|||
<!-- incremental -->
Commercial software do their best to cover all possible use cases by the engineer.
<!-- incremental -->
However, there will be use cases that are not covered by the software.
<!-- incremental -->
Programming is there to give the engineer the power to make his own.
<!-- incremental -->
==From software user to software developer.==
<!-- incremental -->
```pyxel-flow
direction=right
gap=12
color=7
Buy|software
Find|issues
Build|solutions
```

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
