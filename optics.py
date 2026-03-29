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

#=================================plot a point=================================
theta_p = np.deg2rad(90)
phi_p = np.deg2rad(0)

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

#ax.plot([-1.3, 1.3],[-1.3,1.3],[0,0])

#ax.plot([0,0.5],[0,0.5],[0,-0.5])
#animation
#===================================rotate about z axis==========================
# angles = np.linspace(0, np.deg2rad(90), 10)
# point = ax.scatter(a, b, c, color='red', s=50)

# traj_x, traj_y, traj_z = [], [], []
# line, = ax.plot([], [], [])
# def update(frame):
#     m = angles[frame]

#     R_z = np.array([
#         [np.cos(m), -np.sin(m), 0],
#         [np.sin(m),  np.cos(m), 0],
#         [0, 0, 1]
#     ])

#     p = np.array([a, b, c])
#     p_new = R_z @ p

#     # update moving point
#     point._offsets3d = ([p_new[0]], [p_new[1]], [p_new[2]])

#     # store trajectory
#     traj_x.append(p_new[0])
#     traj_y.append(p_new[1])
#     traj_z.append(p_new[2])

#     # update line (NO new object)
#     line.set_data(traj_x, traj_y)
#     line.set_3d_properties(traj_z)

#     return point, line

# from matplotlib.animation import FuncAnimation

# ani = FuncAnimation(fig, update, frames=len(angles), interval=10,repeat=False)
#plt.show()

# m = np.deg2rad(90)


# R_z = np.array([[np.cos(m), -np.sin(m), 0],[np.sin(m), np.cos(m) , 0],[0, 0, 1]]) #rotation matrix about z

# p_a = np.array([a,b,c])
# p_a = np.array([a,b,c])
# p_a_p = R_z @ p_a
#===============================================================================
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
#plt.show()
#==========================================================================
#=========================extract final points==============================
fx, fy, fz = p_new

ftheta = np.arccos(fz)
fphi = np.arctan2(fy, fx)

# optional: make phi in [0, 2π]
if fphi < 0:
    fphi += 2*np.pi

# ---- Output ----
# print("Final Cartesian:", p_new)
# print("theta (rad):", theta)
# print("phi (rad):", phi)
# print("theta (deg):", np.rad2deg(theta))
# print("phi (deg):", np.rad2deg(phi))
#==========================================================================

#ax.scatter(p_a_p[0], p_a_p[1], p_a_p[2], c='green')
ax.text(1.6, 0, 0, '$S_1$')
ax.text(0, 1.6, 0, '$S_2$')
ax.text(0, 0, 1.6, '$S_3$')
#ax.set_axis_off()
plt.show()

#============================================================
# def analyze_polarization(Ex, Ey):
#     """
#     Calculates Stokes parameters and Poincaré angles from Jones vector components.
#     Ex, Ey can be complex numbers.
#     """
#     # 1. Calculate Stokes Parameters
#     s0 = np.abs(Ex)**2 + np.abs(Ey)**2
#     s1 = np.abs(Ex)**2 - np.abs(Ey)**2
#     s2 = 2 * (Ex.real * Ey.real + Ex.imag * Ey.imag)
#     s3 = 2 * (Ex.real * Ey.imag - Ex.imag * Ey.real)
    
#     stokes = np.array([s0, s1, s2, s3])
    
#     # 2. Normalize for the Poincaré Sphere (q, u, v)
#     q, u, v = s1/s0, s2/s0, s3/s0
    
#     # 3. Calculate Orientation (psi) and Ellipticity (chi)
#     # Using arctan2 for correct quadrant handling
#     psi = 0.5 * np.arctan2(s2, s1)
#     # chi is related to the ratio of axes; sin(2*chi) = S3/S0
#     chi = 0.5 * np.arcsin(np.clip(v, -1, 1))
    
#     return {
#         "Stokes Vector": stokes,
#         "Normalized (q,u,v)": (q, u, v),
#         "Orientation (degrees)": np.degrees(psi),
#         "Ellipticity (degrees)": np.degrees(chi)
#     }

# # --- Example: Right-Handed Elliptical Case ---
# # Suppose Ex = 1, Ey = 0.5 + 0.5j
# Ex_val = 1.0 + 0j
# Ey_val = 0.5 + 0.5j

# results = analyze_polarization(Ex_val, Ey_val)

# for key, value in results.items():
#     print(f"{key}: {value}")
# #============================================================