import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QComboBox, QGridLayout, QGroupBox, QVBoxLayout
)
from PyQt6.QtCore import QTimer

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core_physics import compute_output, compute_trajectory


# ====================== Sphere Canvas ======================
class SphereCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        super().__init__(self.fig)

        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_box_aspect([1, 1, 1])

        # remove padding
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

        self.draw_base()

    def draw_base(self):
        self.ax.clear()

        r = 1
        theta = np.linspace(0, np.pi, 80)
        phi = np.linspace(0, 2*np.pi, 80)
        theta, phi = np.meshgrid(theta, phi)

        x = r*np.sin(theta)*np.cos(phi)
        y = r*np.sin(theta)*np.sin(phi)
        z = r*np.cos(theta)

        self.ax.plot_surface(x, y, z, alpha=0.2)

        # axes
        self.ax.plot([-1.2,1.2],[0,0],[0,0])
        self.ax.plot([0,0],[-1.2,1.2],[0,0])
        self.ax.plot([0,0],[0,0],[-1.2,1.2])

        self.ax.text(1.3,0,0,'S1')
        self.ax.text(0,1.3,0,'S2')
        self.ax.text(0,0,1.3,'S3')

        self.ax.set_xlim([-1.2, 1.2])
        self.ax.set_ylim([-1.2, 1.2])
        self.ax.set_zlim([-1.2, 1.2])

        self.ax.set_axis_off()

    def draw_waveplate_axis(self, alpha):
        nx = np.cos(2*alpha)
        ny = np.sin(2*alpha)
        nz = 0

        t = np.linspace(-1, 1, 100)
        self.ax.plot(t*nx, t*ny, t*nz, color='black', linewidth=3)

    def draw_point(self, point):
        x, y, z = point
        self.point = self.ax.scatter(x, y, z, color='red', s=60)

    def update_point(self, point):
        x, y, z = point
        self.point._offsets3d = ([x], [y], [z])


# ====================== MAIN UI ======================
class PolarizationUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poincaré Sphere Simulator")

        layout = QGridLayout()

        # ===== SPHERE (LEFT, BIG) =====
        self.canvas = SphereCanvas()
        sphere_box = QGroupBox()
        v1 = QVBoxLayout()
        v1.addWidget(self.canvas)
        sphere_box.setLayout(v1)

        # ===== CONTROLS (TOP RIGHT) =====
        control_box = QGroupBox("Controls")
        v2 = QVBoxLayout()

        self.theta_input = QLineEdit()
        self.theta_input.setPlaceholderText("theta (deg)")
        v2.addWidget(self.theta_input)

        self.delta_input = QLineEdit()
        self.delta_input.setPlaceholderText("delta (deg)")
        v2.addWidget(self.delta_input)

        self.plate_select = QComboBox()
        self.plate_select.addItems(["HWP", "QWP"])
        v2.addWidget(self.plate_select)

        self.angle_input = QLineEdit()
        self.angle_input.setPlaceholderText("alpha (deg)")
        v2.addWidget(self.angle_input)

        self.run_button = QPushButton("Run")
        v2.addWidget(self.run_button)

        control_box.setLayout(v2)

        # ===== RESULTS (BOTTOM RIGHT) =====
        result_box = QGroupBox("Results")
        v3 = QVBoxLayout()

        self.result_label = QLabel("Result will appear here")
        v3.addWidget(self.result_label)

        result_box.setLayout(v3)

        # ===== GRID PLACEMENT =====
        layout.addWidget(sphere_box, 0, 0, 2, 1)  # big sphere
        layout.addWidget(control_box, 0, 1)
        layout.addWidget(result_box, 1, 1)

        # stretch (important)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)

        layout.setRowStretch(0, 3)
        layout.setRowStretch(1, 2)

        self.setLayout(layout)

        self.run_button.clicked.connect(self.run_animation)

    # ================= Jones =================
    def get_jones(self):
        try:
            theta = np.deg2rad(float(self.theta_input.text()))
            delta = np.deg2rad(float(self.delta_input.text()))
        except:
            return (1, 0)

        ex = np.cos(theta)
        ey = np.sin(theta) * np.exp(1j * delta)

        norm = np.sqrt(abs(ex)**2 + abs(ey)**2)
        return (ex/norm, ey/norm)

    # ================= Animation =================
    def run_animation(self):
        try:
            alpha = np.deg2rad(float(self.angle_input.text()))
        except:
            return

        plate = self.plate_select.currentText()
        jones = self.get_jones()

        self.canvas.draw_base()
        self.canvas.draw_waveplate_axis(alpha)

        trajectory = compute_trajectory(jones, plate, alpha)

        # input point
        p0 = trajectory[0]
        self.canvas.ax.scatter(p0[0], p0[1], p0[2], color='blue', s=60)

        # moving point
        self.canvas.draw_point(p0)

        # trajectory
        self.traj_x, self.traj_y, self.traj_z = [], [], []
        self.line, = self.canvas.ax.plot([], [], [], color='blue')

        self.step = 0

        def animate():
            if self.step >= len(trajectory):
                self.timer.stop()
                result = compute_output(jones, plate, alpha)
                self.update_result(p0, result)
                return

            p = trajectory[self.step]

            self.canvas.update_point(p)

            self.traj_x.append(p[0])
            self.traj_y.append(p[1])
            self.traj_z.append(p[2])

            self.line.set_data(self.traj_x, self.traj_y)
            self.line.set_3d_properties(self.traj_z)

            self.canvas.draw()
            self.step += 1

        self.timer = QTimer()
        self.timer.timeout.connect(animate)
        self.timer.start(30)

    # ================= Result =================
    def update_result(self, p0, result):
        p = result["point"]
        chi = result["chi"]
        psi = result["psi"]
        e = result["ellipticity"]
        hand = result["handedness"]

        self.result_label.setText(
            f"INPUT:\n({p0[0]:.2f}, {p0[1]:.2f}, {p0[2]:.2f})\n\n"
            f"FINAL:\n({p[0]:.2f}, {p[1]:.2f}, {p[2]:.2f})\n\n"
            f"ψ={np.rad2deg(psi):.2f}°, χ={np.rad2deg(chi):.2f}°\n"
            f"Ellipticity={e:.3f}\n{hand}"
        )


# ====================== RUN ======================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PolarizationUI()
    window.resize(1100, 750)
    window.show()
    sys.exit(app.exec())