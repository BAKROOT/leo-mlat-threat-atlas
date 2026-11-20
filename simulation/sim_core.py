"""Core of the end-to-end simulation testbed for space-based multilateration (assumed SATERA-like design).

Everything here is an ASSUMED model, not the SATERA implementation (which is not published):
  * constellation  : Walker-Star, 200 satellites at 500 km and 86 deg (planes x satellites per plane are parameters);
                     Earth rotation is ignored, as in the geometry scripts of geometry/;
  * measurement    : pseudorange of satellite i for aircraft a,  rho = |s_i - p_a| + c*t_emit + b_i + n,
                     b_i = c * (residual clock error of satellite i), n ~ N(0, sigma^2);
  * solver         : Gauss-Newton least squares on (east, north, c*t_emit) at the known aircraft altitude;
  * L3 monitor     : chi-square residual test, P_FA (RAIM, Brown 1992), plus protection level for P_MD;
  * cross-check    : distance between the MLAT position and the aircraft's broadcast ADS-B position.
All lengths in metres, times in seconds.
"""
import numpy as np
from scipy.stats import chi2, ncx2
from scipy.optimize import brentq

C = 299792458.0
RE = 6371e3
H_SAT = 500e3
A_SAT = RE + H_SAT
INC = np.radians(86.0)
MU = 3.986004418e14
T_ORB = 2 * np.pi * np.sqrt(A_SAT ** 3 / MU)
N_MOT = 2 * np.pi / T_ORB
ALT_AC = 10e3


def constellation(P=10, S=20, F=1):
    raan = np.repeat(np.pi * np.arange(P) / P, S)
    m0 = np.tile(2 * np.pi * np.arange(S) / S, P) + 2 * np.pi * F * np.repeat(np.arange(P), S) / (P * S)
    return np.stack([raan, m0], 1)


def sat_pos(c, t):
    raan, u = c[:, 0], c[:, 1] + N_MOT * t
    x, y, z = A_SAT * np.cos(u), A_SAT * np.sin(u) * np.cos(INC), A_SAT * np.sin(u) * np.sin(INC)
    return np.stack([x * np.cos(raan) - y * np.sin(raan), x * np.sin(raan) + y * np.cos(raan), z], 1)


def llh_to_xyz(lat, lon, h=ALT_AC):
    r = RE + h
    return np.array([r * np.cos(lat) * np.cos(lon), r * np.cos(lat) * np.sin(lon), r * np.sin(lat)])


def enu_basis(lat, lon):
    up = np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
    east = np.array([-np.sin(lon), np.cos(lon), 0.0])
    north = np.cross(up, east)
    return east, north, up


def visible(sp, p, mask_deg=0.0):
    d = sp - p
    rng = np.linalg.norm(d, axis=1)
    up = p / np.linalg.norm(p)
    el = np.degrees(np.arcsin((d @ up) / rng))
    return np.where(el >= mask_deg)[0]


def horiz_dist(p, q):
    """great-circle distance between two points at aircraft altitude (m)"""
    a = p / np.linalg.norm(p); b = q / np.linalg.norm(q)
    return (RE + ALT_AC) * np.arccos(np.clip(a @ b, -1, 1))


def solve(sp, rho, p0, iters=6):
    """Gauss-Newton least squares for (east, north, c*t) at known altitude. Returns position, ct, residuals, G."""
    p = p0.copy(); ct = 0.0
    for _ in range(iters):
        lat = np.arcsin(p[2] / np.linalg.norm(p)); lon = np.arctan2(p[1], p[0])
        e, n, u = enu_basis(lat, lon)
        d = sp - p; rng = np.linalg.norm(d, axis=1); los = d / rng[:, None]
        G = np.column_stack([-(los @ e), -(los @ n), np.ones(len(sp))])
        res = rho - (rng + ct)
        dx, *_ = np.linalg.lstsq(G, res, rcond=None)
        p = p + dx[0] * e + dx[1] * n
        p = p / np.linalg.norm(p) * (RE + ALT_AC)          # keep the known altitude
        ct += dx[2]
        if abs(dx[0]) + abs(dx[1]) < 1e-3: break
    d = sp - p; rng = np.linalg.norm(d, axis=1)
    return p, ct, rho - (rng + ct), G


_lam = {}
def lam_det(dof, p_fa=1e-3, p_md=1e-3, k=1.0):
    key = (dof, p_fa, p_md, k)
    if key not in _lam:
        T2 = k * k * chi2.ppf(1 - p_fa, dof)
        _lam[key] = brentq(lambda l: ncx2.cdf(T2, dof, l) - p_md, 1e-6, 1e5)
    return _lam[key]


def monitor(res, G, sigma, p_fa=1e-3, p_md=1e-3, k=1.0):
    """residual chi-square test and horizontal protection level (HPL) of the geometry"""
    n = len(res)
    if n <= 3:
        return False, np.inf
    q = (res @ res) / sigma ** 2
    alarm = q > k * k * chi2.ppf(1 - p_fa, n - 3)
    K = np.linalg.pinv(G); g = np.sqrt((K[:2] ** 2).sum(0))
    hii = np.clip(np.diag(G @ K), 0, 1 - 1e-12)
    hpl = float(np.max(g * sigma * np.sqrt(lam_det(n - 3, p_fa, p_md, k) / (1 - hii))))
    return bool(alarm), hpl


def gains(G):
    K = np.linalg.pinv(G); g = np.sqrt((K[:2] ** 2).sum(0))
    hii = np.clip(np.diag(G @ K), 0, 1 - 1e-12)
    return g, hii
