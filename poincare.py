from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt

##========================plot a 3d surface==================================
r = 1
theta = np.linspace(0,np.pi,500)
phi = np.linspace(0,2*np.pi,500)
theta,phi = np.meshgrid(theta,phi)

x = r*np.sin(theta)*np.cos(phi)
y = r*np.sin(theta)*np.sin(phi)
z = r*np.cos(theta)

fig = plt.figure(figsize=(6,5))
ax = plt.axes(projection ='3d')
ax.set_box_aspect([1,1,1])
ax.plot_surface(x, y, z, alpha=0.5)

#=================================plot input field polarization==================
import numpy as np

def jones_to_polarization(a, b):
    """
    Input:
        a, b : complex numbers (Jones vector components)

    Returns:
        dict with:
        S0, S1, S2, S3
        s1, s2, s3 (normalized)
        chi (ellipticity angle, rad)
        psi (orientation angle, rad)
    """

    # ---- Stokes parameters ----
    S0 = abs(a)**2 + abs(b)**2
    S1 = abs(a)**2 - abs(b)**2
    S2 = 2 * np.real(a * np.conj(b))
    S3 = 2 * np.imag(a * np.conj(b))

    # ---- Normalize ----
    s1 = S1 / S0
    s2 = S2 / S0
    s3 = S3 / S0

    # ---- Polarization angles ----
    psi = 0.5 * np.arctan2(S2, S1)
    chi = 0.5 * np.arcsin(s3)

    return {
        "S0": S0, "S1": S1, "S2": S2, "S3": S3,
        "s1": s1, "s2": s2, "s3": s3,
        "chi (rad)": chi,
        "psi (rad)": psi
    }

ex = 1
ey = 0
result = jones_to_polarization(ex,ey)
chi,psi = result["chi (rad)"],result["psi (rad)"]

theta_p = np.pi/2 - 2*chi
phi_p = 2*psi
# optional: wrap phi to [0, 2π]
phi_p = np.mod(phi_p, 2*np.pi)

a = r*np.sin(theta_p)*np.cos(phi_p)
b = r*np.sin(theta_p)*np.sin(phi_p)
c = r*np.cos(theta_p)

ax.scatter(a,b,c, c = 'red', s=50)
#=============================================================================

ax.set_xlabel('x_axis')
ax.set_ylabel('y_axis')
ax.set_zlabel('z_axis')

#==================================plot new axes================================
ax.plot([-1.5, 1.5], [0, 0], [0, 0])
ax.plot([0, 0], [-1.5, 1.5], [0, 0])
ax.plot([0, 0], [0, 0], [-1.5, 1.5])
#==============================================================================
#===================make a unit vector and rotation generator around it==========

point = ax.scatter(a, b, c, color='red', s=50)
theta_axis = np.deg2rad(90) #Thistwo angles control the position of the rotation axis
phi_axis = np.deg2rad(45)

nx = np.sin(theta_axis)*np.cos(phi_axis)
ny = np.sin(theta_axis)*np.sin(phi_axis)
nz = np.cos(theta_axis)

n = np.array([nx, ny, nz])   # unit axis
angle = np.deg2rad(90) # how much angle rotation

nx, ny, nz = n

K = np.array([
    [0, -nz, ny],
    [nz, 0, -nx],
    [-ny, nx, 0]
])

#===============================================================================
#=================================rotate the point==============================

I = np.eye(3)

R = I*np.cos(angle) + (1 - np.cos(angle)) * np.outer(n, n) + K*np.sin(angle)

p = np.array([a,b,c]) #old point
p_new = R @ p  #final point after rotation
#print(p_new)

# ax.scatter(p_new[0],p_new[1],p_new[2])

t = np.linspace(0, 1, 100)

x_line = t * nx
y_line = t * ny
z_line = t * nz

ax.plot(x_line, y_line, z_line)

#=============================================================================
#animation
#===================================rotate about unit vector =================
angles = np.linspace(0, np.deg2rad(90), 10)

traj_x, traj_y, traj_z = [], [], []
line, = ax.plot([], [], [])
def update(frame):
    m = angles[frame]

    I = np.eye(3)
    R_u = I*np.cos(m) + (1 - np.cos(m)) * np.outer(n, n) + K*np.sin(m)

    p = np.array([a, b, c])
    p_new = R_u @ p

    # update moving point
    point._offsets3d = ([p_new[0]], [p_new[1]], [p_new[2]])

    # store trajectory
    traj_x.append(p_new[0])
    traj_y.append(p_new[1])
    traj_z.append(p_new[2])

    # update line (NO new object)
    line.set_data(traj_x, traj_y)
    line.set_3d_properties(traj_z)

    return point, line

from matplotlib.animation import FuncAnimation

ani = FuncAnimation(fig, update, frames=len(angles), interval=10,repeat=False)
ax.text(1.6, 0, 0, '$S_1$')
ax.text(0, 1.6, 0, '$S_2$')
ax.text(0, 0, 1.6, '$S_3$')
#plt.show()
#==========================================================================
#=========================extract final points==============================
fx, fy, fz = p_new

ftheta = np.arccos(fz)
fphi = np.arctan2(fy, fx)

# optional: make phi in [0, 2π]
if fphi < 0:
    fphi += 2*np.pi

print(ftheta, fphi)

ax.scatter(fx, fy, fz, c='green', s=50)
plt.show()
#===========================convert back to chi and psi=======================
# ===== Convert (theta, phi) → (chi, psi) =====
chi_final = (np.pi/2 - ftheta) / 2
psi_final = fphi / 2

# ===== Ellipticity =====
ellipticity = np.tan(chi_final)

# ===== Handedness =====
if chi_final > 0:
    handedness = "Left-handed"
elif chi_final < 0:
    handedness = "Right-handed"
else:
    handedness = "Linear"

# ===== Print results =====
print("\n--- Final Polarization State ---")
print("theta (deg):", np.rad2deg(ftheta))
print("phi (deg):", np.rad2deg(fphi))
print("chi (deg):", np.rad2deg(chi_final))
print("psi (deg):", np.rad2deg(psi_final))
print("Ellipticity:", ellipticity)
print("Handedness:", handedness)
#=============================================================================

