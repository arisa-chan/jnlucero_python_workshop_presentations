"""
================================================================================
EXPERT FOOTING FE ANALYSIS AND DESIGN SUITE
Framework: PySide6 (Qt) + Matplotlib (3D Visuals) + OpenSeesPy (FEM Engine)
Design Standard: ACI 318-19 / Bowles Foundation Analysis
================================================================================
"""

import sys
import numpy as np

# PySide6 Imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QTextEdit,
    QSplitter, QRadioButton, QButtonGroup, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator

# Visualization Imports
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.cm as cm

# Graceful OpenSeesPy Import
OPENSEES_AVAILABLE = False
try:
    import openseespy.opensees as ops
    OPENSEES_AVAILABLE = True
except ImportError:
    OPENSEES_AVAILABLE = False
except Exception:
    OPENSEES_AVAILABLE = False


# ==============================================================================
# STRUCTURAL ENGINEERING ANALYSIS & DESIGN ENGINE
# ==============================================================================
class FootingStructuralEngine:
    """
    Executes iterative sizing, structural design, and FEA using OpenSeesPy shell elements
    (or analytical fallback) for isolated concrete footings according to ACI 318-19 guidelines.
    """
    def __init__(self, inputs):
        self.inputs = inputs
        self.results = {}
        
        # Concrete & Steel Properties
        self.fc = inputs['fc']     # MPa
        self.fy = inputs['fy']     # MPa
        self.SBC = inputs['SBC']   # kPa
        
        # Geometry (converted to meters)
        self.cx = inputs['cx'] / 1000.0
        self.cy = inputs['cy'] / 1000.0
        self.ex = inputs['ex'] / 1000.0
        self.ey = inputs['ey'] / 1000.0
        self.mesh_size = max(0.10, inputs['mesh_size'])

        # Loads
        self.Ps = inputs['Ps']   # kN
        self.Msx = inputs['Msx'] # kN-m
        self.Msy = inputs['Msy'] # kN-m
        self.Pu = inputs['Pu']   # kN
        self.Mux = inputs['Mux'] # kN-m
        self.Muy = inputs['Muy'] # kN-m

        # Initial Dimensions Estimation
        P_eff_service = self.Ps * (1.0 + 2.5 * (abs(self.ex)/max(self.cx, 0.1) + abs(self.ey)/max(self.cy, 0.1)))
        area_est = max(1.0, (P_eff_service * 1.2) / self.SBC)
        min_b = np.sqrt(area_est)

        self.Bx = max(self.cx + 2.0 * abs(self.ex) + 0.5, min_b)
        self.By = max(self.cy + 2.0 * abs(self.ey) + 0.5, min_b)
        self.h = max(0.35, min(self.Bx, self.By) / 7.0)

    def solve(self):
        """Iteratively size footing until all structural and geotechnical checks pass."""
        converged = False
        max_iters = 50
        
        for iteration in range(max_iters):
            # Subgrade modulus ks = 120 * SBC (kN/m³)
            ks = 120.0 * self.SBC

            # Run FEA Engine (or fallback)
            if OPENSEES_AVAILABLE:
                try:
                    analysis_results = self.run_opensees_fem(ks)
                except Exception:
                    analysis_results = self.run_rigid_fallback(ks)
            else:
                analysis_results = self.run_rigid_fallback(ks)

            # Design Parameters (ACI 318-19)
            phi_shear = 0.75
            phi_moment = 0.90
            d = max(0.15, self.h - 0.075) # 75 mm clear cover

            max_q_service = np.max(analysis_results['soil_pressure_service'])
            max_settlement = np.max(analysis_results['settlement_mm'])
            max_q_u = np.max(analysis_results['soil_pressure_ultimate'])

            # One-Way Shear
            crit_x = max(0.0, (self.Bx - self.cx)/2.0 - d)
            crit_y = max(0.0, (self.By - self.cy)/2.0 - d)
            Vu_1w = max_q_u * max(self.By * crit_x, self.Bx * crit_y)
            Vc_1w = phi_shear * 0.17 * np.sqrt(self.fc) * (min(self.Bx, self.By) * 1000.0) * (d * 1000.0) / 1000.0

            # Two-Way Punching Shear
            bo = 2.0 * ((self.cx + d) + (self.cy + d))
            beta = max(self.cx, self.cy) / max(min(self.cx, self.cy), 1e-3)
            vc1 = 0.33 * np.sqrt(self.fc)
            vc2 = 0.17 * (1.0 + 2.0 / beta) * np.sqrt(self.fc)
            vc3 = 0.083 * (20.0 * d / bo + 2.0) * np.sqrt(self.fc)
            Vn_punch = min(vc1, vc2, vc3)
            phiVn_punch = phi_shear * Vn_punch * (bo * 1000.0) * (d * 1000.0) / 1000.0
            Vu_punch = max(0.0, self.Pu - max_q_u * (self.cx + d) * (self.cy + d))

            # Flexural Reinforcement Calculation
            arm_x = (self.Bx - self.cx) / 2.0
            arm_y = (self.By - self.cy) / 2.0
            Mu_x = max_q_u * self.By * (arm_x**2) / 2.0
            Mu_y = max_q_u * self.Bx * (arm_y**2) / 2.0

            def calc_as(Mu_kNm, width_m, eff_d_m):
                if Mu_kNm <= 0:
                    return 0.0018 * (width_m * 1000.0) * (self.h * 1000.0)
                Rn = (Mu_kNm * 1e6) / (phi_moment * (width_m * 1000.0) * (eff_d_m * 1000.0)**2)
                m = self.fy / (0.85 * self.fc)
                disc = 1.0 - 2.0 * Rn * m / self.fy
                if disc < 0:
                    return 999999.0
                rho = (1.0 / m) * (1.0 - np.sqrt(disc))
                rho = max(rho, 0.0018)
                return rho * (width_m * 1000.0) * (eff_d_m * 1000.0)

            As_req_x = calc_as(Mu_x, self.By, d)
            As_req_y = calc_as(Mu_y, self.Bx, d)

            # Adaptive Sizing Logic
            action_required = False

            if max_q_service > self.SBC:
                overstress = max_q_service / self.SBC
                inc = max(0.1, (overstress - 1.0) * 0.4 * self.Bx)
                self.Bx += inc
                self.By += inc
                action_required = True

            if max_settlement > 25.0:
                overstress = max_settlement / 25.0
                inc = max(0.1, (overstress - 1.0) * 0.3 * self.Bx)
                self.Bx += inc
                self.By += inc
                action_required = True

            shear_ratio = max(
                Vu_1w / max(Vc_1w, 1e-3),
                Vu_punch / max(phiVn_punch, 1e-3),
                As_req_x / 8000.0,
                As_req_y / 8000.0
            )
            if shear_ratio > 1.0:
                inc_h = max(0.05, (shear_ratio - 1.0) * 0.15 * self.h)
                self.h += inc_h
                action_required = True

            self.Bx = np.ceil(self.Bx * 20.0) / 20.0
            self.By = np.ceil(self.By * 20.0) / 20.0
            self.h  = np.ceil(self.h * 20.0) / 20.0

            if not action_required:
                converged = True
                self.results = analysis_results
                self.results.update({
                    'Bx': self.Bx, 'By': self.By, 'h': self.h, 'd': d,
                    'Vu_1w': Vu_1w, 'Vc_1w': Vc_1w,
                    'Vu_punch': Vu_punch, 'phiVn_punch': phiVn_punch,
                    'Mu_x': Mu_x, 'Mu_y': Mu_y,
                    'As_x': As_req_x, 'As_y': As_req_y,
                    'q_max_service': max_q_service,
                    'settlement_max': max_settlement,
                    'iterations': iteration + 1
                })
                break

        return converged

    def get_mesh_grid(self):
        """Generates refined mesh coordinate grid for FE analysis."""
        nx, ny = 21, 21  # High resolution grid for smooth plate bending contours
        x = np.linspace(-self.Bx/2.0, self.Bx/2.0, nx)
        y = np.linspace(-self.By/2.0, self.By/2.0, ny)
        return x, y, np.meshgrid(x, y)

    def solve_opensees_case(self, ks, P, Msx, Msy):
        """
        Executes OpenSeesPy FE model using ShellMITC4 elements for flexible footing plate
        bending stiffness and non-linear Elastic-No-Tension (ENT) Winkler springs for soil support.
        Moments and axial load are applied as an exact physical pressure distribution over the column footprint.
        """
        ops.wipe()
        ops.model('basic', '-ndm', 3, '-ndf', 6)

        # Concrete Material Properties
        Ec = 4700.0 * np.sqrt(self.fc) * 1000.0  # kPa
        nu = 0.2                                 # Poisson's ratio
        rho = 2.4                                # Density (kN/m^3)

        # Plate Shell Section (Elastic Bending & Membrane)
        sec_tag = 1
        ops.section('ElasticMembranePlateSection', sec_tag, Ec, nu, self.h, rho)

        x_vals, y_vals, (X, Y) = self.get_mesh_grid()
        nx, ny = len(x_vals), len(y_vals)
        dx = self.Bx / (nx - 1)
        dy = self.By / (ny - 1)

        # 1. Create Plate Nodes
        node_map = {}
        node_tag = 1
        for j, y in enumerate(y_vals):
            for i, x in enumerate(x_vals):
                ops.node(node_tag, x, y, 0.0)
                node_map[(i, j)] = node_tag
                node_tag += 1

        # 2. Build ShellMITC4 Elements (Full Bending/Shear Stiffness)
        ele_tag = 1
        for j in range(ny - 1):
            for i in range(nx - 1):
                n1 = node_map[(i, j)]
                n2 = node_map[(i+1, j)]
                n3 = node_map[(i+1, j+1)]
                n4 = node_map[(i, j+1)]
                ops.element('ShellMITC4', ele_tag, n1, n2, n3, n4, sec_tag)
                ele_tag += 1

        # 3. Model Non-Linear Winkler Subgrade Springs (ENT - Elastic No Tension)
        for (i, j), tag in node_map.items():
            wx = dx if (0 < i < nx - 1) else dx / 2.0
            wy = dy if (0 < j < ny - 1) else dy / 2.0
            Atrib = wx * wy

            Kz = ks * Atrib
            mat_tag = 100 + tag
            ops.uniaxialMaterial('ENT', mat_tag, Kz)

            # Fixed Base Ground Node
            g_tag = 10000 + tag
            ops.node(g_tag, x_vals[i], y_vals[j], 0.0)
            ops.fix(g_tag, 1, 1, 1, 1, 1, 1)

            # zeroLength Winkler Spring element in Z direction
            ops.element('zeroLength', 20000 + tag, g_tag, tag, '-mat', mat_tag, '-dir', 3)
            
            # Constrain in-plane translations and drilling rotation for stability
            ops.fix(tag, 1, 1, 0, 0, 0, 1)

        # 4. Integrate Column Axial Load & Bending Moments across Column Footprint
        x_min, x_max = self.ex - self.cx/2.0, self.ex + self.cx/2.0
        y_min, y_max = self.ey - self.cy/2.0, self.ey + self.cy/2.0

        # Sub-grid sampling over column footprint for exact load integration
        sub_n = 25
        sub_x = np.linspace(x_min, x_max, sub_n)
        sub_y = np.linspace(y_min, y_max, sub_n)
        dA = (self.cx / sub_n) * (self.cy / sub_n)

        nodal_P = np.zeros((ny, nx))

        for sy in sub_y:
            for sx in sub_x:
                # Transverse interface pressure stress (kPa) from axial force + moments
                q_p = (P / (self.cx * self.cy)) + \
                      (12.0 * Msx * (sy - self.ey) / (self.cx * (self.cy**3))) + \
                      (12.0 * Msy * (sx - self.ex) / (self.cy * (self.cx**3)))
                dP = q_p * dA

                # Map sub-point load to containing shell mesh element using bilinear interpolation
                sx_c = np.clip(sx, -self.Bx/2.0 + 1e-5, self.Bx/2.0 - 1e-5)
                sy_c = np.clip(sy, -self.By/2.0 + 1e-5, self.By/2.0 - 1e-5)

                i_idx = int(np.floor((sx_c - (-self.Bx/2.0)) / dx))
                j_idx = int(np.floor((sy_c - (-self.By/2.0)) / dy))

                i_idx = max(0, min(i_idx, nx - 2))
                j_idx = max(0, min(j_idx, ny - 2))

                xi = (sx_c - x_vals[i_idx]) / dx
                eta = (sy_c - y_vals[j_idx]) / dy

                N1 = (1.0 - xi) * (1.0 - eta)
                N2 = xi * (1.0 - eta)
                N3 = xi * eta
                N4 = (1.0 - xi) * eta

                nodal_P[j_idx, i_idx]     += dP * N1
                nodal_P[j_idx, i_idx+1]   += dP * N2
                nodal_P[j_idx+1, i_idx+1] += dP * N3
                nodal_P[j_idx+1, i_idx]   += dP * N4

        # Apply nodal vertical forces to FE plate model
        ops.timeSeries('Linear', 1)
        ops.pattern('Plain', 1, 1)
        for (i, j), tag in node_map.items():
            load_val = nodal_P[j, i]
            if abs(load_val) > 1e-8:
                ops.load(tag, 0.0, 0.0, -load_val, 0.0, 0.0, 0.0)

        # 5. Static FE Analysis Execution
        ops.system('BandGeneral')
        ops.numberer('RCM')
        ops.constraints('Transformation')
        ops.algorithm('Newton')
        ops.integrator('LoadControl', 1.0)
        ops.analysis('Static')
        
        ok = ops.analyze(1)
        if ok != 0:
            raise RuntimeError("OpenSees solver analysis did not converge.")

        # 6. Extract Nodal Settlement & Compute Soil Pressures
        disp_z = np.zeros((ny, nx))
        pressure = np.zeros((ny, nx))

        for (i, j), tag in node_map.items():
            uz = ops.nodeDisp(tag, 3)              # Z-displacement (m)
            settlement_m = max(0.0, -uz)           # Compression downward
            disp_z[j, i] = settlement_m * 1000.0   # Convert to mm
            pressure[j, i] = ks * settlement_m     # Soil pressure in kPa

        return X, Y, disp_z, pressure

    def run_opensees_fem(self, ks):
        """Runs OpenSeesPy FEA for both Service and Ultimate Load cases."""
        X, Y, settlement_s, q_service = self.solve_opensees_case(ks, self.Ps, self.Msx, self.Msy)
        _, _, _, q_ultimate = self.solve_opensees_case(ks, self.Pu, self.Mux, self.Muy)

        return {
            'X': X, 'Y': Y,
            'soil_pressure_service': q_service,
            'soil_pressure_ultimate': q_ultimate,
            'settlement_mm': settlement_s,
            'method': 'OpenSeesPy FE Engine (ShellMITC4 Flexible Plate on ENT Winkler Soil)'
        }

    def run_rigid_fallback(self, ks):
        """Rigid analytical fallback solver."""
        x_vals, y_vals, (X, Y) = self.get_mesh_grid()
        Area = self.Bx * self.By
        Ix = (self.Bx * (self.By**3)) / 12.0
        Iy = (self.By * (self.Bx**3)) / 12.0

        Mx_eff_s = self.Msx + self.Ps * self.ey
        My_eff_s = self.Msy + self.Ps * self.ex
        Mx_eff_u = self.Mux + self.Pu * self.ey
        My_eff_u = self.Muy + self.Pu * self.ex

        q_s = np.maximum(0.0, (self.Ps / Area) + (Mx_eff_s * Y / Ix) + (My_eff_s * X / Iy))
        q_u = np.maximum(0.0, (self.Pu / Area) + (Mx_eff_u * Y / Ix) + (My_eff_u * X / Iy))
        settlement_mm = (q_s / ks) * 1000.0

        return {
            'X': X, 'Y': Y,
            'soil_pressure_service': q_s,
            'soil_pressure_ultimate': q_u,
            'settlement_mm': settlement_mm,
            'method': 'Rigid Footing Analytical Solver'
        }


# ==============================================================================
# VISUALIZATION CANVAS (PREVENTS CANVAS SHRINKING)
# ==============================================================================
class MplCanvas(FigureCanvas):
    """3D Visualizer for Footing Plate, Column Stub, and FE Contours."""
    def __init__(self, parent=None, width=7, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)

    def visualize_footing(self, res, inputs, plot_mode='settlement'):
        """Re-draws 3D visualization cleanly without canvas padding accumulation."""
        self.fig.clf()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#f4f4f6')

        Bx, By, h = res['Bx'], res['By'], res['h']
        cx, cy = inputs['cx'] / 1000.0, inputs['cy'] / 1000.0
        ex, ey = inputs['ex'] / 1000.0, inputs['ey'] / 1000.0

        # 1. Outer Footing Wireframe & Top Surface
        x_corners = [-Bx/2, Bx/2, Bx/2, -Bx/2, -Bx/2]
        y_corners = [-By/2, -By/2, By/2, By/2, -By/2]
        
        self.ax.plot(x_corners, y_corners, [0]*5, color='#444444', lw=1.5)
        self.ax.plot(x_corners, y_corners, [-h]*5, color='#222222', lw=1.5)
        
        for i in range(4):
            self.ax.plot([x_corners[i], x_corners[i]], 
                         [y_corners[i], y_corners[i]], 
                         [0, -h], color='#444444', lw=1.2)

        XX, YY = np.meshgrid([-Bx/2, Bx/2], [-By/2, By/2])
        self.ax.plot_surface(XX, YY, np.zeros_like(XX), color='lightgray', alpha=0.25, shade=False)

        # 2. Column Stub
        col_h = max(0.5, h)
        col_x = [ex-cx/2, ex+cx/2, ex+cx/2, ex-cx/2, ex-cx/2]
        col_y = [ey-cy/2, ey-cy/2, ey+cy/2, ey+cy/2, ey-cy/2]

        self.ax.plot(col_x, col_y, [col_h]*5, color='darkred', lw=1.8)
        for i in range(4):
            self.ax.plot([col_x[i], col_x[i]], [col_y[i], col_y[i]], [0, col_h], color='darkred', lw=1.5)

        CX, CY = np.meshgrid([ex-cx/2, ex+cx/2], [ey-cy/2, ey+cy/2])
        self.ax.plot_surface(CX, CY, np.full_like(CX, col_h), color='red', alpha=0.45, shade=False)

        # 3. Load Vector Arrow
        arrow_len = col_h * 0.8
        self.ax.quiver(ex, ey, col_h + arrow_len, 0, 0, -arrow_len, 
                       color='blue', linewidth=2.5, arrow_length_ratio=0.25)

        # 4. FE Base Contours (Settlement or Pressure)
        X, Y = res['X'], res['Y']
        Z_bottom = np.full_like(X, -h)

        if plot_mode == 'settlement':
            data = res['settlement_mm']
            title = 'Settlement (mm)'
            cmap = cm.viridis
        else:
            data = res['soil_pressure_service']
            title = 'Soil Pressure (kPa)'
            cmap = cm.plasma

        norm = matplotlib.colors.Normalize(vmin=np.min(data), vmax=np.max(data))
        colors = cmap(norm(data))

        self.ax.plot_surface(X, Y, Z_bottom, facecolors=colors, 
                             rstride=1, cstride=1, antialiased=True, shade=False)

        # 5. Colorbar & View Adjustments
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = self.fig.colorbar(sm, ax=self.ax, shrink=0.5, aspect=12, pad=0.08)
        cbar.set_label(title, fontsize=10, fontweight='bold')

        self.ax.set_xlabel('X (m)', labelpad=6)
        self.ax.set_ylabel('Y (m)', labelpad=6)
        self.ax.set_zlabel('Z (m)', labelpad=6)
        self.ax.set_title(f"3D Footing Visualizer - {title}", fontsize=11, fontweight='bold', pad=10)

        max_dim = max(Bx, By, col_h*2)
        self.ax.set_box_aspect((Bx, By, max_dim))
        self.ax.view_init(elev=26, azim=-125)

        self.draw()


# ==============================================================================
# MAIN PYSIDE6 GUI APP
# ==============================================================================
class FootingDesignApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Engineered Footing Design & 3D FE Visualizer (ACI 318-19)")
        self.resize(1350, 850)

        self.setFont(QFont("Segoe UI", 9))
        self.init_ui()
        self.analyze_and_design()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Left Control Panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        input_grp = QGroupBox("Design Inputs")
        input_layout = QGridLayout(input_grp)
        input_layout.setSpacing(6)

        self.inputs = {}
        validator = QDoubleValidator(-10000.0, 100000.0, 2, self)

        def add_input(label, key, default, u_row, u_col, unit):
            lbl = QLabel(label)
            led = QLineEdit(str(default))
            led.setValidator(validator)
            led.setAlignment(Qt.AlignRight)
            unit_lbl = QLabel(unit)
            unit_lbl.setStyleSheet("color: #0066cc; font-weight: bold;")
            input_layout.addWidget(lbl, u_row, u_col * 3)
            input_layout.addWidget(led, u_row, u_col * 3 + 1)
            input_layout.addWidget(unit_lbl, u_row, u_col * 3 + 2)
            self.inputs[key] = led

        # Inputs Setup
        add_input("Concrete f'c:", 'fc', 28.0, 0, 0, "MPa")
        add_input("Rebar fy:", 'fy', 415.0, 0, 1, "MPa")
        add_input("Soil SBC:", 'SBC', 200.0, 1, 0, "kPa")
        add_input("FE Mesh Size:", 'mesh_size', 0.25, 1, 1, "m")

        add_input("Col Dim cx:", 'cx', 500.0, 2, 0, "mm")
        add_input("Col Dim cy:", 'cy', 500.0, 2, 1, "mm")
        add_input("Eccentricity ex:", 'ex', 100.0, 3, 0, "mm")
        add_input("Eccentricity ey:", 'ey', 50.0, 3, 1, "mm")

        add_input("Service Ps:", 'Ps', 1200.0, 4, 0, "kN")
        add_input("Service Msx:", 'Msx', 60.0, 4, 1, "kN-m")
        add_input("Service Msy:", 'Msy', 30.0, 5, 0, "kN-m")

        add_input("Ultimate Pu:", 'Pu', 1650.0, 6, 0, "kN")
        add_input("Ultimate Mux:", 'Mux', 85.0, 6, 1, "kN-m")
        add_input("Ultimate Muy:", 'Muy', 45.0, 7, 0, "kN-m")

        left_layout.addWidget(input_grp)

        self.btn_calc = QPushButton("Analyze and Design")
        self.btn_calc.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.btn_calc.setStyleSheet("background-color: #007acc; color: white; padding: 10px; border-radius: 4px;")
        self.btn_calc.clicked.connect(self.analyze_and_design)
        left_layout.addWidget(self.btn_calc)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setFont(QFont("Consolas", 9))
        left_layout.addWidget(self.report_text)

        # Right Panel (Visualization)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        controls_grp = QGroupBox("3D Display Controls")
        hbox = QHBoxLayout(controls_grp)
        
        self.btngrp_viz = QButtonGroup(self)
        self.radio_settle = QRadioButton("Show Settlement (mm)")
        self.radio_settle.setChecked(True)
        self.radio_press = QRadioButton("Show Soil Pressure (kPa)")
        self.btngrp_viz.addButton(self.radio_settle)
        self.btngrp_viz.addButton(self.radio_press)
        self.btngrp_viz.buttonClicked.connect(self.update_viz)
        
        hbox.addWidget(self.radio_settle)
        hbox.addWidget(self.radio_press)
        hbox.addStretch()
        right_layout.addWidget(controls_grp)

        self.canvas = MplCanvas(self, width=7, height=6, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, self)
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([460, 890])
        main_layout.addWidget(splitter)

        self.current_results = None
        self.current_inputs_vals = None

    def get_input_values(self):
        try:
            return {k: float(v.text()) for k, v in self.inputs.items()}
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please enter valid numerical values in all fields.")
            return None

    def analyze_and_design(self):
        input_vals = self.get_input_values()
        if not input_vals:
            return

        engine = FootingStructuralEngine(input_vals)
        converged = engine.solve()

        if converged:
            self.current_results = engine.results
            self.current_inputs_vals = input_vals
            self.update_viz()
            self.generate_report()
        else:
            QMessageBox.warning(self, "Convergence Warning", "Footing design did not converge within allowable dimensions.")

    def update_viz(self):
        if self.current_results is None:
            return
        mode = 'settlement' if self.radio_settle.isChecked() else 'pressure'
        self.canvas.visualize_footing(self.current_results, self.current_inputs_vals, mode)

    def generate_report(self):
        res = self.current_results
        inp = self.current_inputs_vals
        
        rpt = f"=================================================================\n"
        rpt += f"             STRUCTURAL FOOTING DESIGN REPORT (ACI 318-19)\n"
        rpt += f"=================================================================\n"
        rpt += f"Analysis Engine: {res['method']}\n"
        rpt += f"Iterations to Convergence: {res['iterations']}\n\n"
        
        rpt += f"1. FINAL FOOTING GEOMETRY\n"
        rpt += f"-----------------------------------------------------------------\n"
        rpt += f" Width Along X (Bx)        : {res['Bx']:.3f} m  ({res['Bx']*1000:.0f} mm)\n"
        rpt += f" Width Along Y (By)        : {res['By']:.3f} m  ({res['By']*1000:.0f} mm)\n"
        rpt += f" Total Thickness (h)       : {res['h']:.3f} m  ({res['h']*1000:.0f} mm)\n"
        rpt += f" Effective Depth (d)       : {res['d']:.3f} m  (75mm clear cover)\n\n"
        
        rpt += f"2. SERVICEABILITY CHECKS\n"
        rpt += f"-----------------------------------------------------------------\n"
        rpt += f" Max Soil Pressure (qs)    : {res['q_max_service']:.2f} kPa  (Allowable SBC: {inp['SBC']:.0f} kPa)\n"
        rpt += f" Bearing Check             : {'[ PASS ]' if res['q_max_service'] <= inp['SBC'] else '[ FAIL ]'}\n"
        rpt += f" Max Settlement (s)        : {res['settlement_max']:.2f} mm  (Limit: 25.00 mm)\n"
        rpt += f" Settlement Check          : {'[ PASS ]' if res['settlement_max'] <= 25.0 else '[ FAIL ]'}\n\n"
        
        rpt += f"3. ULTIMATE SHEAR CHECKS\n"
        rpt += f"-----------------------------------------------------------------\n"
        rpt += f" One-Way Shear Vu          : {res['Vu_1w']:.1f} kN  (phiVc: {res['Vc_1w']:.1f} kN)\n"
        rpt += f" One-Way Shear Check       : {'[ PASS ]' if res['Vu_1w'] <= res['Vc_1w'] else '[ FAIL ]'}\n"
        rpt += f" Punching Shear Vu         : {res['Vu_punch']:.1f} kN  (phiVn: {res['phiVn_punch']:.1f} kN)\n"
        rpt += f" Punching Shear Check      : {'[ PASS ]' if res['Vu_punch'] <= res['phiVn_punch'] else '[ FAIL ]'}\n\n"
        
        rpt += f"4. FLEXURAL REINFORCEMENT REQUIREMENTS\n"
        rpt += f"-----------------------------------------------------------------\n"
        rpt += f" Moment About Y (Mu_x)     : {res['Mu_x']:.2f} kN-m/m\n"
        rpt += f" Required As (X-Dir)       : {res['As_x']:.0f} mm^2/m\n"
        rpt += f" Moment About X (Mu_y)     : {res['Mu_y']:.2f} kN-m/m\n"
        rpt += f" Required As (Y-Dir)       : {res['As_y']:.0f} mm^2/m\n"
        rpt += f"================================================================="
        
        self.report_text.setText(rpt)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FootingDesignApp()
    window.show()
    sys.exit(app.exec())