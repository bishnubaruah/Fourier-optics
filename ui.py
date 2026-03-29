import sys
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QComboBox, QSlider
)
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# import your physics
from core_physics import compute_output


# ====================== Matplotlib Canvas ======================
class SphereCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 5))
        super().__init__(self.fig)

        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_box_aspect([1, 1, 1])

        self.plot_static_sphere()

    def plot_static_sphere(self):
        self.ax.clear()

        r = 1
        theta = np.linspace(0, np.pi, 100)
        phi = np.linspace(0, 2*np.pi, 100)
        theta, phi = np.meshgrid(theta, phi)

        x = r*np.sin(theta)*np.cos(phi)
        y = r*np.sin(theta)*np.sin(phi)
        z = r*np.cos(theta)

        self.ax.plot_surface(x, y, z, alpha=0.2)

        # axes
        self.ax.plot([-1.5, 1.5], [0, 0], [0, 0])
        self.ax.plot([0, 0], [-1.5, 1.5], [0, 0])
        self.ax.plot([0, 0], [0, 0], [-1.5, 1.5])

        self.ax.text(1.6, 0, 0, '$S_1$')
        self.ax.text(0, 1.6, 0, '$S_2$')
        self.ax.text(0, 0, 1.6, '$S_3$')

        self.ax.set_axis_off()

    def update_point(self, point):
        self.plot_static_sphere()

        x, y, z = point
        self.ax.scatter(x, y, z, color='red', s=60)

        self.draw()


# ====================== Main UI ======================
class PolarizationUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Poincaré Sphere Simulator")

        layout = QVBoxLayout()

        # -------- Canvas --------
        self.canvas = SphereCanvas()
        layout.addWidget(self.canvas)

        # -------- Input polarization --------
        self.pol_select = QComboBox()
        self.pol_select.addItems(["H", "V", "D", "R", "L"])
        layout.addWidget(QLabel("Input Polarization"))
        layout.addWidget(self.pol_select)

        # -------- Waveplate --------
        self.plate_select = QComboBox()
        self.plate_select.addItems(["HWP", "QWP"])
        layout.addWidget(QLabel("Waveplate"))
        layout.addWidget(self.plate_select)

        # -------- Angle slider --------
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(180)
        layout.addWidget(QLabel("Angle (degrees)"))
        layout.addWidget(self.slider)

        # -------- Output --------
        self.output = QLabel("Output will appear here")
        layout.addWidget(self.output)

        # -------- Connections --------
        self.slider.valueChanged.connect(self.update_output)
        self.plate_select.currentIndexChanged.connect(self.update_output)
        self.pol_select.currentIndexChanged.connect(self.update_output)

        self.setLayout(layout)

        # initial update
        self.update_output()

    # ================== Polarization presets ==================
    def get_jones(self):
        pol = self.pol_select.currentText()

        if pol == "H":
            return (1, 0)
        elif pol == "V":
            return (0, 1)
        elif pol == "D":
            return (1/np.sqrt(2), 1/np.sqrt(2))
        elif pol == "R":
            return (1/np.sqrt(2), -1j/np.sqrt(2))
        elif pol == "L":
            return (1/np.sqrt(2), 1j/np.sqrt(2))

    # ================== Update ==================
    def update_output(self):
        alpha = np.deg2rad(self.slider.value())
        plate = self.plate_select.currentText()
        jones = self.get_jones()

        result = compute_output(jones, plate, alpha)

        point = result["point"]
        chi = result["chi"]
        psi = result["psi"]
        ellipticity = result["ellipticity"]
        handedness = result["handedness"]

        # update plot
        self.canvas.update_point(point)

        # update text
        self.output.setText(
            f"ψ: {np.rad2deg(psi):.2f}°\n"
            f"χ: {np.rad2deg(chi):.2f}°\n"
            f"Ellipticity: {ellipticity:.3f}\n"
            f"Handedness: {handedness}"
        )


# ====================== Run App ======================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PolarizationUI()
    window.show()
    sys.exit(app.exec())