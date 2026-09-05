"""
Plasticity yield criteria visualizer -- Tresca, von Mises, Drucker-Prager.

Views:
    3d          yield surface in principal stress space (sigma1, sigma2, sigma3)
                -- drag the plot to rotate it
    deviatoric  pi-plane section (perpendicular to the hydrostatic axis) with
                the projected sigma1, sigma2, sigma3 directions 120 deg apart
    plane       plane stress (sigma3 = 0): the classic hexagon inside an ellipse

How to run (any one of these):
    python yield_criteria.py                   graphical interface
    python yield_criteria.py --cli             question-and-answer mode
    python yield_criteria.py --criterion mises --view 3d --sy 250
    python yield_criteria.py --criterion tresca mises drucker --view plane
    python yield_criteria.py --criterion drucker --eta 0.5 --save cone.png

Author: Aiden Azarnoush
Dedicated to my beloved mother, Simin Nematpour.
"""

import argparse
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# ============================================================== geometry
# Orthonormal basis: n along the hydrostatic axis, (e1, e2) spanning the
# pi-plane, with e1 the projection of the sigma1 axis.
N_HYD = np.array([1.0, 1.0, 1.0]) / np.sqrt(3.0)
E1 = np.array([2.0, -1.0, -1.0]) / np.sqrt(6.0)
E2 = np.array([0.0, 1.0, -1.0]) / np.sqrt(2.0)

CRITERIA = ('tresca', 'mises', 'drucker')
ALIASES = {'both': ('tresca', 'mises'), 'all': CRITERIA}
VIEWS = ('3d', 'deviatoric', 'plane')


def parse_criteria(items):
    """Accept names, aliases, or comma-separated strings -> ordered tuple."""
    out = []
    for item in items:
        for name in str(item).replace(',', ' ').split():
            name = name.lower()
            names = ALIASES.get(name, (name,))
            for n in names:
                if n not in CRITERIA:
                    raise ValueError(f'unknown criterion: {n}')
                if n not in out:
                    out.append(n)
    if not out:
        raise ValueError('choose at least one criterion')
    return tuple(out)
DEFAULTS = dict(sy=1.0, cbar=1.0, eta=1.0)


def to_principal(rho, theta, xi):
    """Map cylindrical coords about the hydrostatic axis to (s1, s2, s3)."""
    return (rho*np.cos(theta)*E1[:, None, None] + rho*np.sin(theta)*E2[:, None, None]
            + xi*N_HYD[:, None, None])


def rho_mises(sy):
    """von Mises deviatoric radius: sqrt(2/3) sigma_y (constant)."""
    return np.sqrt(2.0/3.0)*sy


def rho_tresca(theta, sy):
    """Tresca deviatoric radius as a function of the Lode-type angle:
    a regular hexagon inscribed in the von Mises circle, touching it at
    the six uniaxial directions (theta = 0, 60, 120 ...)."""
    rv = rho_mises(sy)                         # vertex radius
    t = np.mod(theta, np.pi/3.0) - np.pi/6.0
    return rv*np.cos(np.pi/6.0)/np.cos(t)


def drucker_params(cbar, eta):
    """Drucker-Prager cone in the tension-positive convention:
    deviatoric radius rho = cbar at the origin plane (xi = 0), apex on the
    hydrostatic axis at xi_apex = sqrt(3) cbar / eta (hydrostatic tension),
    widening toward compression. Equivalent to sqrt(J2) = k - alpha I1 with
    k = cbar/sqrt(2), alpha = eta/(3 sqrt(2))."""
    xi_apex = np.sqrt(3.0)*cbar/eta
    return xi_apex, cbar/np.sqrt(2.0), eta/(3.0*np.sqrt(2.0))


def rho_drucker(xi, cbar, eta):
    xi_apex, _, _ = drucker_params(cbar, eta)
    return np.clip(cbar*(1.0 - xi/xi_apex), 0.0, None)


# ============================================================== 3D views
def _style_3d(ax, lim):
    ax.plot([-lim, lim], [-lim, lim], [-lim, lim], 'r--', lw=1.4,
            label='hydrostatic axis σ₁ = σ₂ = σ₃')
    ax.set_xlabel('σ₁', fontsize=13, fontweight='bold')
    ax.set_ylabel('σ₂', fontsize=13, fontweight='bold')
    ax.set_zlabel('σ₃', fontsize=13, fontweight='bold')
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=22, azim=32)


def surface_prism(ax, rho_fn, sy, length, color, label, n_th=241, n_xi=2):
    theta = np.linspace(0, 2*np.pi, n_th)
    xi = np.linspace(-length, length, n_xi)
    TH, XI = np.meshgrid(theta, xi)
    S = to_principal(rho_fn(TH), TH, XI)
    ax.plot_surface(S[0], S[1], S[2], color=color, alpha=0.45,
                    linewidth=0, antialiased=True)
    ax.plot([], [], color=color, lw=6, alpha=0.6, label=label)


NAMES = {'tresca': 'Tresca', 'mises': 'von Mises', 'drucker': 'Drucker-Prager'}


def _title(criteria):
    return ' + '.join(NAMES[c] for c in criteria)


def plot_3d(criteria, sy, cbar, eta, ax=None):
    if ax is None:
        fig = plt.figure(figsize=(7.5, 6.5))
        ax = fig.add_subplot(projection='3d')
    lim = 0.0
    length = 2.2*sy if 'drucker' not in criteria else max(2.2*sy, 2.6*cbar)
    if 'tresca' in criteria:
        surface_prism(ax, lambda th: rho_tresca(th, sy), sy, length,
                      '#2a9d5c', 'Tresca (hexagonal prism)')
        lim = max(lim, 2.4*sy)
    if 'mises' in criteria:
        surface_prism(ax, lambda th: np.full_like(th, rho_mises(sy)), sy,
                      length, '#1f5fbf', 'von Mises (cylinder)')
        lim = max(lim, 2.4*sy)
    if 'drucker' in criteria:
        xi_apex, k, alpha = drucker_params(cbar, eta)
        theta = np.linspace(0, 2*np.pi, 181)
        xi = np.linspace(-length, xi_apex, 40)
        TH, XI = np.meshgrid(theta, xi)
        S = to_principal(rho_drucker(XI, cbar, eta), TH, XI)
        ax.plot_surface(S[0], S[1], S[2], color='#d3541f', alpha=0.5,
                        linewidth=0)
        ax.plot([], [], color='#d3541f', lw=6, alpha=0.6,
                label=f'Drucker-Prager cone, c̄ = {cbar:g}, η = {eta:g}')
        lim = max(lim, 2.6*cbar)
    _style_3d(ax, lim)
    ax.set_title(_title(criteria) + '   (drag to rotate)', fontsize=12)
    ax.legend(loc='upper left', fontsize=9)
    return ax


# ======================================================== deviatoric view
def plot_deviatoric(criteria, sy, cbar, eta, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6.4, 6.4))
    theta = np.linspace(0, 2*np.pi, 721)
    r = max([1.45*rho_mises(sy)] * ('tresca' in criteria or 'mises' in criteria)
            + [1.6*cbar] * ('drucker' in criteria))
    # projected principal axes, 120 degrees apart
    for k, name in enumerate(['σ₁', 'σ₂', 'σ₃']):
        a = 2*np.pi*k/3
        ax.plot([0, r*np.cos(a)], [0, r*np.sin(a)], color='0.35', lw=1.2)
        ax.plot([0, -0.55*r*np.cos(a)], [0, -0.55*r*np.sin(a)], color='0.75',
                lw=1, ls=':')
        ax.text(1.08*r*np.cos(a), 1.08*r*np.sin(a), name, fontsize=14,
                ha='center', va='center', fontweight='bold')
    if 'tresca' in criteria:
        rho = rho_tresca(theta, sy)
        ax.plot(rho*np.cos(theta), rho*np.sin(theta), color='#2a9d5c', lw=2.4,
                label='Tresca hexagon')
    if 'mises' in criteria:
        rho = rho_mises(sy)
        ax.plot(rho*np.cos(theta), rho*np.sin(theta), color='#1f5fbf', lw=2.4,
                label=f'von Mises circle, ρ = √(2/3) σ_y = {rho:.3g}')
    if 'drucker' in criteria:
        # alone: several hydrostatic levels; combined: the xi = 0 section
        levels = [(0.0, '-'), (-1.0*cbar, '--'), (-2.0*cbar, ':')] \
            if criteria == ('drucker',) else [(0.0, '-')]
        for xi, ls in levels:
            rho = rho_drucker(xi, cbar, eta)
            ax.plot(rho*np.cos(theta), rho*np.sin(theta), color='#d3541f',
                    lw=2.2, ls=ls, label=f'Drucker-Prager, ξ = {xi:g}  (ρ = {rho:.3g})')
    ax.set_aspect('equal'); ax.set_xlim(-1.25*r, 1.25*r); ax.set_ylim(-1.25*r, 1.25*r)
    ax.axis('off')
    ax.set_title('π-plane (deviatoric) section: ' + _title(criteria), fontsize=12)
    ax.legend(loc='lower right', fontsize=9)
    return ax


# ====================================================== plane-stress view
def plot_plane_stress(criteria, sy, cbar, eta, ax=None):
    if ax is None:
        fig, ax = plt.subplots(figsize=(6.4, 6.4))
    lim = 0.0
    if 'tresca' in criteria:
        hx = np.array([1, 1, 0, -1, -1, 0, 1])*sy
        hy = np.array([0, 1, 1, 0, -1, -1, 0])*sy
        ax.plot(hx, hy, color='#2a9d5c', lw=2.4, label='Tresca hexagon')
        lim = max(lim, 1.5*sy)
    if 'mises' in criteria:
        t = np.linspace(0, 2*np.pi, 400)
        # ellipse s1^2 - s1 s2 + s2^2 = sy^2, principal axes at 45 deg
        a, b = np.sqrt(2.0)*sy, np.sqrt(2.0/3.0)*sy
        x, y = a*np.cos(t), b*np.sin(t)
        c45 = np.cos(np.pi/4)
        ax.plot(c45*(x - y), c45*(x + y), color='#1f5fbf', lw=2.4,
                label='von Mises ellipse')
        lim = max(lim, 1.5*sy)
    if 'drucker' in criteria:
        # DP with sigma3 = 0: sqrt(J2) = k - alpha I1 -> a conic in (s1, s2)
        xi_apex, k, alpha = drucker_params(cbar, eta)
        s = np.linspace(-4*cbar, 3*cbar, 500)
        S1, S2 = np.meshgrid(s, s)
        J2 = (S1**2 - S1*S2 + S2**2)/3.0
        F = np.sqrt(J2) + alpha*(S1 + S2) - k
        ax.contour(S1, S2, F, levels=[0.0], colors='#d3541f', linewidths=2.4)
        ax.plot([], [], color='#d3541f', lw=2.4,
                label=f'Drucker-Prager, c̄ = {cbar:g}, η = {eta:g}')
        lim = max(lim, 3.2*cbar)
    ax.axhline(0, color='0.6', lw=0.8); ax.axvline(0, color='0.6', lw=0.8)
    ax.set_aspect('equal'); ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_xlabel('σ₁', fontsize=13, fontweight='bold')
    ax.set_ylabel('σ₂', fontsize=13, fontweight='bold')
    ax.set_title('Plane stress (σ₃ = 0): ' + _title(criteria), fontsize=12)
    ax.grid(alpha=0.3); ax.legend(loc='upper left', fontsize=9)
    return ax


PLOTTERS = {'3d': plot_3d, 'deviatoric': plot_deviatoric, 'plane': plot_plane_stress}


def make_plot(criteria, view, sy, cbar, eta, save=None):
    criteria = parse_criteria([criteria] if isinstance(criteria, str) else criteria)
    PLOTTERS[view](criteria, sy, cbar, eta)
    if save:
        plt.savefig(save, dpi=150, bbox_inches='tight')
        print(f'saved {save}')
    else:
        plt.show()


# ================================================================== CLI
def ask(prompt, options=None, default=None, cast=str):
    """Ask a question; Enter accepts the default."""
    tail = f' [{default}]' if default is not None else ''
    while True:
        raw = input(f'{prompt}{tail}: ').strip()
        if not raw and default is not None:
            return default
        if options and raw.lower() not in options:
            print(f'   please choose one of: {", ".join(options)}')
            continue
        try:
            return cast(raw)
        except ValueError:
            print('   please enter a number')


def run_cli():
    print('\nPlasticity yield criteria visualizer')
    print('------------------------------------')
    print('Criteria:  tresca, mises, drucker -- pick one or several, comma separated')
    print('           shortcuts: both = tresca,mises   all = all three')
    while True:
        try:
            crit = parse_criteria([ask('Which criteria', default='both')])
            break
        except ValueError as e:
            print(f'   {e}')
    print('Views:     3d (rotate with the mouse) | deviatoric (π-plane) | plane (σ₃ = 0)')
    view = ask('Which view', VIEWS, '3d')
    sy, cbar, eta = DEFAULTS['sy'], DEFAULTS['cbar'], DEFAULTS['eta']
    if 'tresca' in crit or 'mises' in crit:
        sy = ask('Yield stress σ_y (any units, 1 = normalized)', default=sy, cast=float)
    if 'drucker' in crit:
        cbar = ask('Cohesion-like constant c̄', default=cbar, cast=float)
        eta = ask('Friction parameter η (try 0.5 or 1.0)', default=eta, cast=float)
    save = ask('Save to file instead of showing? (filename or Enter)', default='')
    make_plot(crit, view, sy, cbar, eta, save or None)


# ================================================================== GUI
def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog

    root = tk.Tk()
    root.title('Yield Criteria Visualizer')
    root.resizable(False, False)
    frm = ttk.Frame(root, padding=14); frm.grid()
    pad = dict(padx=6, pady=5)

    ttk.Label(frm, text='Criteria (tick any)').grid(row=0, column=0, sticky='nw', **pad)
    checks = {}
    box = ttk.Frame(frm); box.grid(row=0, column=1, sticky='w', **pad)
    for i, (key, name, on) in enumerate([('tresca', 'Tresca', True),
                                         ('mises', 'von Mises', True),
                                         ('drucker', 'Drucker-Prager', False)]):
        v = tk.BooleanVar(value=on)
        ttk.Checkbutton(box, text=name, variable=v).grid(row=i, column=0, sticky='w')
        checks[key] = v

    ttk.Label(frm, text='View').grid(row=1, column=0, sticky='w', **pad)
    view = tk.StringVar(value='3d')
    ttk.Combobox(frm, textvariable=view, state='readonly', width=30,
                 values=['3d', 'deviatoric', 'plane']).grid(row=1, column=1, **pad)

    entries = {}
    for i, (label, key) in enumerate([('Yield stress σ_y', 'sy'),
                                      ('Drucker-Prager c̄', 'cbar'),
                                      ('Drucker-Prager η', 'eta')], start=2):
        ttk.Label(frm, text=label).grid(row=i, column=0, sticky='w', **pad)
        v = tk.StringVar(value=str(DEFAULTS[key]))
        ttk.Entry(frm, textvariable=v, width=12, justify='right').grid(
            row=i, column=1, sticky='w', **pad)
        entries[key] = v

    status = ttk.Label(frm, text='Defaults are fine — just press Plot.',
                       foreground='#555')
    status.grid(row=6, column=0, columnspan=2, sticky='w', **pad)

    def values():
        try:
            return (float(entries['sy'].get()), float(entries['cbar'].get()),
                    float(entries['eta'].get()))
        except ValueError:
            status.config(text='Please enter numbers.', foreground='#b00')
            return None

    def chosen():
        c = [k for k, v in checks.items() if v.get()]
        if not c:
            status.config(text='Tick at least one criterion.', foreground='#b00')
        return c

    def do_plot():
        v, c = values(), chosen()
        if v and c:
            status.config(text='Plot window opened (drag 3D plots to rotate).',
                          foreground='#555')
            make_plot(c, view.get(), *v)

    def do_save():
        v, c = values(), chosen()
        if not (v and c):
            return
        f = filedialog.asksaveasfilename(defaultextension='.png',
                                         filetypes=[('PNG', '*.png'), ('PDF', '*.pdf')])
        if f:
            make_plot(c, view.get(), *v, save=f)
            plt.close('all')
            status.config(text=f'Saved {f}', foreground='#555')

    ttk.Button(frm, text='Plot', command=do_plot).grid(row=5, column=0, sticky='ew', **pad)
    ttk.Button(frm, text='Save PNG…', command=do_save).grid(row=5, column=1, sticky='ew', **pad)
    root.mainloop()


# ================================================================= main
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--gui', action='store_true', help='graphical interface (default)')
    p.add_argument('--cli', action='store_true', help='question-and-answer mode')
    p.add_argument('--criterion', nargs='+', metavar='NAME',
                   help='one or more of: tresca mises drucker  (or both / all)')
    p.add_argument('--view', choices=VIEWS, default='3d')
    p.add_argument('--sy', type=float, default=DEFAULTS['sy'], help='yield stress')
    p.add_argument('--cbar', type=float, default=DEFAULTS['cbar'], help='DP constant c̄')
    p.add_argument('--eta', type=float, default=DEFAULTS['eta'], help='DP parameter η')
    p.add_argument('--save', metavar='FILE', help='write the figure instead of showing it')
    a = p.parse_args(argv)

    if a.cli:
        run_cli()
    elif a.criterion:
        make_plot(a.criterion, a.view, a.sy, a.cbar, a.eta, a.save)
    else:
        try:
            run_gui()
        except ImportError:
            print('tkinter not available; falling back to the question mode.')
            run_cli()


if __name__ == '__main__':
    main()
