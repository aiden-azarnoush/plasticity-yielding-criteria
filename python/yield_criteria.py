"""
Plasticity yield criteria visualizer -- Tresca, von Mises, Drucker-Prager.

    python yield_criteria.py          graphical interface
    python yield_criteria.py --cli    question-and-answer mode

Both ask the same three things:
    1. which criterion   (Tresca / von Mises / Drucker-Prager / Tresca + von Mises)
    2. which view        (3D principal stress space / 2D plane stress / pi-plane)
    3. the constant      (sigma_y, or eta for Drucker-Prager)

Leave the constant empty and you get a SCHEMATIC plot: normalized surface,
no tick numbers -- the kind of picture that goes in a paper or a textbook.
Enter a number and the plot has real axes.

The code is organized as one small function per criterion and view, so
it is easy to read and to change:

    tresca_3d   tresca_2d   tresca_pi
    mises_3d    mises_2d    mises_pi
    drucker_3d  drucker_2d  drucker_pi
    both_3d     both_2d     both_pi        (Tresca + von Mises together)

Author: Aiden Azarnoush
Dedicated to my beloved mother, Simin Nematpour.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

GREEN, BLUE, ORANGE = '#2a9d5c', '#1f5fbf', '#d3541f'

# Basis around the hydrostatic axis: n along sigma1 = sigma2 = sigma3,
# e1 and e2 spanning the pi-plane (e1 = projection of the sigma1 axis).
N_HYD = np.array([1.0, 1.0, 1.0]) / np.sqrt(3.0)
E1 = np.array([2.0, -1.0, -1.0]) / np.sqrt(6.0)
E2 = np.array([0.0, 1.0, -1.0]) / np.sqrt(2.0)


# =============================================================== helpers
def cyl_to_principal(rho, theta, xi):
    """(deviatoric radius, angle in pi-plane, hydrostatic coord) -> sigma."""
    return (rho*np.cos(theta)*E1[:, None, None]
            + rho*np.sin(theta)*E2[:, None, None]
            + xi*N_HYD[:, None, None])


def rho_mises(sy):
    """von Mises: constant deviatoric radius sqrt(2/3) sigma_y."""
    return np.sqrt(2.0/3.0)*sy


def rho_tresca(theta, sy):
    """Tresca: regular hexagon inscribed in the von Mises circle."""
    t = np.mod(theta, np.pi/3.0) - np.pi/6.0
    return rho_mises(sy)*np.cos(np.pi/6.0)/np.cos(t)


def rho_drucker(xi, eta, cbar=1.0):
    """Drucker-Prager cone: radius cbar at xi = 0, apex at sqrt(3) cbar/eta
    on the hydrostatic axis (tension side), widening in compression."""
    xi_apex = np.sqrt(3.0)*cbar/eta
    return np.clip(cbar*(1.0 - xi/xi_apex), 0.0, None)


def new_3d():
    fig = plt.figure(figsize=(7.5, 6.5))
    return fig.add_subplot(projection='3d')


def new_2d():
    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    return ax


def finish_3d(ax, lim, title, schematic):
    ax.plot([-lim, lim], [-lim, lim], [-lim, lim], 'r--', lw=1.4,
            label='hydrostatic axis σ₁ = σ₂ = σ₃')
    ax.set_xlabel('σ₁', fontsize=13, fontweight='bold')
    ax.set_ylabel('σ₂', fontsize=13, fontweight='bold')
    ax.set_zlabel('σ₃', fontsize=13, fontweight='bold')
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=22, azim=32)
    if schematic:
        ax.set_xticklabels([]); ax.set_yticklabels([]); ax.set_zticklabels([])
    ax.set_title(title + '   (drag to rotate)', fontsize=12)
    ax.legend(loc='upper left', fontsize=9)


def finish_2d(ax, lim, title, schematic):
    ax.axhline(0, color='0.6', lw=0.8); ax.axvline(0, color='0.6', lw=0.8)
    ax.set_aspect('equal'); ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_xlabel('σ₁', fontsize=13, fontweight='bold')
    ax.set_ylabel('σ₂', fontsize=13, fontweight='bold')
    if schematic:
        ax.set_xticklabels([]); ax.set_yticklabels([])
    ax.grid(alpha=0.3)
    ax.set_title(title, fontsize=12)
    ax.legend(loc='upper left', fontsize=9)


def finish_pi(ax, r, title):
    """Draw the three projected principal axes, 120 degrees apart."""
    for k, name in enumerate(['σ₁', 'σ₂', 'σ₃']):
        a = 2*np.pi*k/3
        ax.plot([0, r*np.cos(a)], [0, r*np.sin(a)], color='0.35', lw=1.2)
        ax.plot([0, -0.55*r*np.cos(a)], [0, -0.55*r*np.sin(a)],
                color='0.75', lw=1, ls=':')
        ax.text(1.08*r*np.cos(a), 1.08*r*np.sin(a), name, fontsize=14,
                ha='center', va='center', fontweight='bold')
    ax.set_aspect('equal'); ax.set_xlim(-1.25*r, 1.25*r); ax.set_ylim(-1.25*r, 1.25*r)
    ax.axis('off')
    ax.set_title(title, fontsize=12)
    ax.legend(loc='lower right', fontsize=9)


def prism(ax, rho_of_theta, length, color, label):
    """Surface of a prism along the hydrostatic axis."""
    theta = np.linspace(0, 2*np.pi, 241)
    xi = np.array([-length, length])
    TH, XI = np.meshgrid(theta, xi)
    S = cyl_to_principal(rho_of_theta(TH), TH, XI)
    ax.plot_surface(S[0], S[1], S[2], color=color, alpha=0.45, linewidth=0)
    ax.plot([], [], color=color, lw=6, alpha=0.6, label=label)


def hexagon_2d(ax, sy):
    hx = np.array([1, 1, 0, -1, -1, 0, 1])*sy
    hy = np.array([0, 1, 1, 0, -1, -1, 0])*sy
    ax.plot(hx, hy, color=GREEN, lw=2.4, label='Tresca hexagon')


def ellipse_2d(ax, sy):
    t = np.linspace(0, 2*np.pi, 400)
    a, b = np.sqrt(2.0)*sy, np.sqrt(2.0/3.0)*sy      # axes at 45 degrees
    x, y = a*np.cos(t), b*np.sin(t)
    c = np.cos(np.pi/4)
    ax.plot(c*(x - y), c*(x + y), color=BLUE, lw=2.4, label='von Mises ellipse')


def circle_pi(ax, rho, color, label, ls='-'):
    t = np.linspace(0, 2*np.pi, 400)
    ax.plot(rho*np.cos(t), rho*np.sin(t), color=color, lw=2.4, ls=ls, label=label)


def hexagon_pi(ax, sy):
    t = np.linspace(0, 2*np.pi, 721)
    rho = rho_tresca(t, sy)
    ax.plot(rho*np.cos(t), rho*np.sin(t), color=GREEN, lw=2.4, label='Tresca hexagon')


# ================================================================ Tresca
def tresca_3d(sy=1.0, schematic=True):
    ax = new_3d()
    prism(ax, lambda th: rho_tresca(th, sy), 2.2*sy, GREEN, 'Tresca (hexagonal prism)')
    finish_3d(ax, 2.4*sy, 'Tresca yield surface', schematic)


def tresca_2d(sy=1.0, schematic=True):
    ax = new_2d()
    hexagon_2d(ax, sy)
    finish_2d(ax, 1.5*sy, 'Tresca, plane stress (σ₃ = 0)', schematic)


def tresca_pi(sy=1.0, schematic=True):
    ax = new_2d()
    hexagon_pi(ax, sy)
    finish_pi(ax, 1.45*rho_mises(sy), 'Tresca in the π-plane')


# ============================================================= von Mises
def mises_3d(sy=1.0, schematic=True):
    ax = new_3d()
    prism(ax, lambda th: np.full_like(th, rho_mises(sy)), 2.2*sy, BLUE,
          'von Mises (cylinder)')
    finish_3d(ax, 2.4*sy, 'von Mises yield surface', schematic)


def mises_2d(sy=1.0, schematic=True):
    ax = new_2d()
    ellipse_2d(ax, sy)
    finish_2d(ax, 1.5*sy, 'von Mises, plane stress (σ₃ = 0)', schematic)


def mises_pi(sy=1.0, schematic=True):
    ax = new_2d()
    circle_pi(ax, rho_mises(sy), BLUE, 'von Mises circle, ρ = √(2/3) σ_y')
    finish_pi(ax, 1.45*rho_mises(sy), 'von Mises in the π-plane')


# ======================================================== Drucker-Prager
def drucker_3d(eta=1.0, schematic=True, cbar=1.0):
    ax = new_3d()
    xi_apex = np.sqrt(3.0)*cbar/eta
    theta = np.linspace(0, 2*np.pi, 181)
    xi = np.linspace(-3.0*cbar, xi_apex, 40)
    TH, XI = np.meshgrid(theta, xi)
    S = cyl_to_principal(rho_drucker(XI, eta, cbar), TH, XI)
    ax.plot_surface(S[0], S[1], S[2], color=ORANGE, alpha=0.5, linewidth=0)
    ax.plot([], [], color=ORANGE, lw=6, alpha=0.6,
            label=f'Drucker-Prager cone, η = {eta:g}')
    finish_3d(ax, 2.6*cbar, 'Drucker-Prager yield surface', schematic)


def drucker_2d(eta=1.0, schematic=True, cbar=1.0):
    """Plane stress section: sqrt(J2) = k - alpha I1 with sigma3 = 0."""
    ax = new_2d()
    k, alpha = cbar/np.sqrt(2.0), eta/(3.0*np.sqrt(2.0))
    s = np.linspace(-4*cbar, 3*cbar, 500)
    S1, S2 = np.meshgrid(s, s)
    J2 = (S1**2 - S1*S2 + S2**2)/3.0
    ax.contour(S1, S2, np.sqrt(J2) + alpha*(S1 + S2) - k, levels=[0.0],
               colors=ORANGE, linewidths=2.4)
    ax.plot([], [], color=ORANGE, lw=2.4, label=f'Drucker-Prager, η = {eta:g}')
    finish_2d(ax, 3.2*cbar, 'Drucker-Prager, plane stress (σ₃ = 0)', schematic)


def drucker_pi(eta=1.0, schematic=True, cbar=1.0):
    """pi-plane sections at three hydrostatic levels (radius grows in compression)."""
    ax = new_2d()
    for xi, ls in [(0.0, '-'), (-cbar, '--'), (-2*cbar, ':')]:
        circle_pi(ax, rho_drucker(xi, eta, cbar), ORANGE, f'ξ = {xi:g}', ls)
    finish_pi(ax, 1.6*cbar, f'Drucker-Prager in the π-plane, η = {eta:g}')


# ==================================================== Tresca + von Mises
def both_3d(sy=1.0, schematic=True):
    ax = new_3d()
    prism(ax, lambda th: rho_tresca(th, sy), 2.2*sy, GREEN, 'Tresca (hexagonal prism)')
    prism(ax, lambda th: np.full_like(th, rho_mises(sy)), 2.2*sy, BLUE,
          'von Mises (cylinder)')
    finish_3d(ax, 2.4*sy, 'Tresca inside von Mises', schematic)


def both_2d(sy=1.0, schematic=True):
    ax = new_2d()
    hexagon_2d(ax, sy)
    ellipse_2d(ax, sy)
    finish_2d(ax, 1.5*sy, 'Tresca and von Mises, plane stress (σ₃ = 0)', schematic)


def both_pi(sy=1.0, schematic=True):
    ax = new_2d()
    hexagon_pi(ax, sy)
    circle_pi(ax, rho_mises(sy), BLUE, 'von Mises circle')
    finish_pi(ax, 1.45*rho_mises(sy), 'Tresca and von Mises in the π-plane')


# ================================================================= menus
CRITERIA = {1: ('Tresca', 'tresca'), 2: ('von Mises', 'mises'),
            3: ('Drucker-Prager', 'drucker'), 4: ('Tresca + von Mises', 'both')}
VIEWS = {1: ('3D principal stress space', '3d'),
         2: ('2D plane stress (σ₃ = 0)', '2d'),
         3: ('π-plane (deviatoric stresses)', 'pi')}

FUNCTIONS = {
    ('tresca', '3d'): tresca_3d, ('tresca', '2d'): tresca_2d, ('tresca', 'pi'): tresca_pi,
    ('mises', '3d'): mises_3d, ('mises', '2d'): mises_2d, ('mises', 'pi'): mises_pi,
    ('drucker', '3d'): drucker_3d, ('drucker', '2d'): drucker_2d, ('drucker', 'pi'): drucker_pi,
    ('both', '3d'): both_3d, ('both', '2d'): both_2d, ('both', 'pi'): both_pi,
}


def draw(criterion, view, value=None, save=None):
    """value = None -> schematic plot (normalized, no tick numbers)."""
    func = FUNCTIONS[(criterion, view)]
    if value is None:
        func()                              # defaults: sy = 1 / eta = 1, schematic
    else:
        func(value, schematic=False)
    if save:
        plt.savefig(save, dpi=150, bbox_inches='tight', pad_inches=0.35)
        print(f'saved {save}')
    else:
        plt.show()


def ask_choice(title, options):
    print(f'\n{title}')
    for k, (name, _) in options.items():
        print(f'  {k}. {name}')
    while True:
        raw = input('Enter a number: ').strip()
        if raw.isdigit() and int(raw) in options:
            return options[int(raw)][1]
        print(f'  Please enter one of: {", ".join(str(k) for k in options)}')


def ask_positive(prompt):
    """A positive number, or empty for a schematic plot."""
    while True:
        raw = input(f'{prompt} (press Enter for a schematic plot): ').strip()
        if raw == '':
            return None
        try:
            v = float(raw)
        except ValueError:
            print('  That is not a number. Try again.')
            continue
        if v < 0:
            print('  That is a negative number. Enter a positive number.')
        elif v == 0:
            print('  Zero is not allowed. Enter a positive number.')
        else:
            return v


def run_cli():
    print('Plasticity yield criteria visualizer')
    criterion = ask_choice('Which criterion?', CRITERIA)
    view = ask_choice('Which view?', VIEWS)
    if criterion == 'drucker':
        value = ask_positive('Friction parameter η (e.g. 0.5 or 1)')
    else:
        value = ask_positive('Yield stress σ_y (any units, e.g. 250)')
    draw(criterion, view, value)


def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog

    root = tk.Tk()
    root.title('Yield Criteria Visualizer')
    root.resizable(False, False)
    frm = ttk.Frame(root, padding=16); frm.grid()
    pad = dict(padx=6, pady=3)

    ttk.Label(frm, text='Criterion', font=('', 11, 'bold')).grid(
        row=0, column=0, sticky='w', **pad)
    crit = tk.StringVar(value='both')
    for i, (name, key) in enumerate(CRITERIA.values()):
        ttk.Radiobutton(frm, text=name, value=key, variable=crit).grid(
            row=1 + i, column=0, sticky='w', padx=18)

    ttk.Label(frm, text='View', font=('', 11, 'bold')).grid(
        row=0, column=1, sticky='w', **pad)
    view = tk.StringVar(value='3d')
    for i, (name, key) in enumerate(VIEWS.values()):
        ttk.Radiobutton(frm, text=name, value=key, variable=view).grid(
            row=1 + i, column=1, sticky='w', padx=18)

    ttk.Label(frm, text='Constant  (σ_y, or η for Drucker-Prager)',
              font=('', 11, 'bold')).grid(row=5, column=0, columnspan=2,
                                          sticky='w', pady=(12, 0), padx=6)
    value = tk.StringVar(value='')
    ttk.Entry(frm, textvariable=value, width=12, justify='right').grid(
        row=6, column=0, sticky='w', padx=18)
    ttk.Label(frm, text='leave empty for a schematic plot (no tick numbers)',
              foreground='#666').grid(row=6, column=1, sticky='w')

    status = ttk.Label(frm, text='', foreground='#b00')
    status.grid(row=8, column=0, columnspan=2, sticky='w', **pad)

    def get_value():
        raw = value.get().strip()
        if raw == '':
            return None
        try:
            v = float(raw)
        except ValueError:
            status.config(text='The constant must be a number.'); return False
        if v <= 0:
            status.config(text='The constant must be a positive number.'); return False
        status.config(text='')
        return v

    def do_plot():
        v = get_value()
        if v is not False:
            draw(crit.get(), view.get(), v)

    def do_save():
        v = get_value()
        if v is False:
            return
        f = filedialog.asksaveasfilename(defaultextension='.png',
                                         filetypes=[('PNG', '*.png'), ('PDF', '*.pdf')])
        if f:
            draw(crit.get(), view.get(), v, save=f)
            plt.close('all')

    ttk.Button(frm, text='Plot', command=do_plot).grid(
        row=7, column=0, sticky='ew', padx=18, pady=(12, 4))
    ttk.Button(frm, text='Save as image…', command=do_save).grid(
        row=7, column=1, sticky='ew', padx=18, pady=(12, 4))
    root.mainloop()


if __name__ == '__main__':
    if '--cli' in sys.argv:
        run_cli()
    else:
        try:
            run_gui()
        except ImportError:
            print('tkinter is not available here, using the question mode instead.\n')
            run_cli()
