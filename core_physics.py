import numpy as np


def compute_output(jones, plate, alpha):
    ex, ey = jones

    # ===== Stokes parameters =====
    S0 = abs(ex)**2 + abs(ey)**2
    S1 = abs(ex)**2 - abs(ey)**2
    S2 = 2 * np.real(ex * np.conj(ey))
    S3 = 2 * np.imag(ex * np.conj(ey))

    s1, s2, s3 = S1/S0, S2/S0, S3/S0

    # ===== initial point on sphere =====
    theta = np.arccos(s3)
    phi = np.arctan2(s2, s1)

    x = np.sin(theta)*np.cos(phi)
    y = np.sin(theta)*np.sin(phi)
    z = np.cos(theta)

    p = np.array([x, y, z])

    # ===== rotation axis from waveplate =====
    theta_axis = np.pi / 2
    phi_axis = 2 * alpha

    nx = np.sin(theta_axis)*np.cos(phi_axis)
    ny = np.sin(theta_axis)*np.sin(phi_axis)
    nz = np.cos(theta_axis)

    n = np.array([nx, ny, nz])

    # ===== rotation angle =====
    if plate == "HWP":
        angle = np.pi
    elif plate == "QWP":
        angle = np.pi / 2
    else:
        angle = 0

    # ===== Rodrigues rotation =====
    K = np.array([
        [0, -nz, ny],
        [nz, 0, -nx],
        [-ny, nx, 0]
    ])

    I = np.eye(3)

    R = I*np.cos(angle) + (1 - np.cos(angle)) * np.outer(n, n) + K*np.sin(angle)

    final_point = R @ p

    # ===== back to spherical =====
    fx, fy, fz = final_point
    fz = np.clip(fz, -1, 1)

    theta_f = np.arccos(fz)
    phi_f = np.arctan2(fy, fx)

    if phi_f < 0:
        phi_f += 2*np.pi

    # ===== chi, psi =====
    chi = (np.pi/2 - theta_f)/2
    psi = phi_f/2

    ellipticity = np.tan(chi)

    # ===== handedness =====
    if chi > 1e-6:
        handedness = "Left-handed"
    elif chi < -1e-6:
        handedness = "Right-handed"
    else:
        handedness = "Linear"

    return {
        "point": final_point,
        "chi": chi,
        "psi": psi,
        "ellipticity": ellipticity,
        "handedness": handedness
    }