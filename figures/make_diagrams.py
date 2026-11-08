import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

out_dirs = [
    os.path.join("d:\\1. project\\FloodGuard", "figures"),
    os.path.join("d:\\1. project\\FloodGuard", "report", "figures")
]
for d in out_dirs:
    os.makedirs(d, exist_ok=True)

# Set high quality font & line styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#000000'
plt.rcParams['axes.linewidth'] = 1.4
plt.rcParams['text.color'] = '#000000'

def save_fig(fig, filename):
    plt.tight_layout()
    for d in out_dirs:
        filepath = os.path.join(d, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Generated UML Diagram: {filename}")

def get_ellipse_border(xc, yc, w, h, target_x, target_y):
    a = w / 2.0
    b = h / 2.0
    dx = target_x - xc
    dy = target_y - yc
    if dx == 0 and dy == 0:
        return float(xc), float(yc)
    theta = np.arctan2(dy, dx)
    t = 1.0 / np.sqrt((np.cos(theta)/a)**2 + (np.sin(theta)/b)**2)
    return float(xc + t * np.cos(theta)), float(yc + t * np.sin(theta))

def draw_human_actor(ax, x, y, label, sublabel="«human actor»", scale=1.15):
    r = 0.26 * scale
    head = plt.Circle((x, y + 0.44 * scale), r, facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=6)
    ax.add_patch(head)
    ax.plot([x, x], [y + 0.18 * scale, y - 0.38 * scale], color='#000000', lw=1.8, zorder=6)
    ax.plot([x - 0.34 * scale, x + 0.34 * scale], [y - 0.02 * scale, y - 0.02 * scale], color='#000000', lw=1.8, zorder=6)
    ax.plot([x, x - 0.28 * scale], [y - 0.38 * scale, y - 0.85 * scale], color='#000000', lw=1.8, zorder=6)
    ax.plot([x, x + 0.28 * scale], [y - 0.38 * scale, y - 0.85 * scale], color='#000000', lw=1.8, zorder=6)
    ax.text(x, y - 1.05 * scale, label, fontsize=11.0, fontweight='bold', ha='center', va='top', color='#000000')
    if sublabel:
        ax.text(x, y - 1.50 * scale, sublabel, fontsize=9.5, style='italic', ha='center', va='top', color='#333333')
    return (x, y - 0.02 * scale)

def draw_device_actor(ax, x, y, label, sublabel="«device»", w=2.8, h=1.25):
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.6, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect)
    ax.text(x, y + 0.28, sublabel, fontsize=9.5, style='italic', ha='center', va='center', color='#000000', zorder=7)
    ax.text(x, y - 0.18, label, fontsize=10.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=7)
    return (x, y)

def draw_timer_actor(ax, x, y, label="Bộ Định Thời Timer", sublabel="«internal timer»", w=2.8, h=1.25):
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.6, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect)
    ax.text(x, y + 0.28, sublabel, fontsize=9.5, style='italic', ha='center', va='center', color='#000000', zorder=7)
    ax.text(x, y - 0.18, label, fontsize=10.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=7)
    return (x, y)

def draw_subsystem_box(ax, x, y, w, h, title):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.8, edgecolor='#000000', facecolor='#ffffff', zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.3, y + h - 0.40, "«system boundary»", fontsize=10.0, style='italic', color='#444444')
    ax.text(x + 0.3, y + h - 0.85, title, fontsize=12.5, fontweight='bold', color='#000000')

def draw_ellipse(ax, x, y, w, h, text, fontsize=10.5):
    ellipse = patches.Ellipse((x, y), w, h, facecolor='#ffffff', edgecolor='#000000', lw=1.5, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, text, fontsize=fontsize, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)
    return (x, y, w, h)

def draw_assoc_line(ax, pt_from, e_to):
    xc, yc, w, h = e_to
    pt_target = get_ellipse_border(xc, yc, w, h, pt_from[0], pt_from[1])
    ax.plot([pt_from[0], pt_target[0]], [pt_from[1], pt_target[1]], color='#000000', lw=1.3, zorder=2)

def draw_include(ax, e_from, e_to, label="«include»"):
    p_from = get_ellipse_border(e_from[0], e_from[1], e_from[2], e_from[3], e_to[0], e_to[1])
    p_to   = get_ellipse_border(e_to[0], e_to[1], e_to[2], e_to[3], e_from[0], e_from[1])

    ax.annotate("", xy=p_to, xytext=p_from,
                arrowprops=dict(arrowstyle="->", lw=1.4, linestyle="--", color="#000000",
                                shrinkA=0, shrinkB=0), zorder=4)

    dx = p_to[0] - p_from[0]
    dy = p_to[1] - p_from[1]
    L = np.hypot(dx, dy)
    if L == 0:
        return
    angle = np.degrees(np.arctan2(dy, dx))
    nx, ny = -dy / L, dx / L
    offset = 0.24
    tx = (p_from[0] + p_to[0]) / 2.0 + offset * nx
    ty = (p_from[1] + p_to[1]) / 2.0 + offset * ny

    ax.text(tx, ty, label, fontsize=10.0, style='italic', color='#000000',
            rotation=angle, rotation_mode='anchor',
            ha='center', va='bottom', zorder=6)

def draw_extend(ax, e_from, e_to, label="«extend»"):
    p_from = get_ellipse_border(e_from[0], e_from[1], e_from[2], e_from[3], e_to[0], e_to[1])
    p_to   = get_ellipse_border(e_to[0], e_to[1], e_to[2], e_to[3], e_from[0], e_from[1])

    ax.annotate("", xy=p_to, xytext=p_from,
                arrowprops=dict(arrowstyle="->", lw=1.4, linestyle="--", color="#000000",
                                shrinkA=0, shrinkB=0), zorder=4)

    dx = p_to[0] - p_from[0]
    dy = p_to[1] - p_from[1]
    mx = (p_from[0] + p_to[0]) / 2.0
    my = (p_from[1] + p_to[1]) / 2.0

    if dx >= 0:
        tx = mx - 0.3
        ty = my + 0.12
        ha = 'right'
    else:
        tx = mx + 0.3
        ty = my + 0.12
        ha = 'left'

    ax.text(tx, ty, label, fontsize=10.0, style='italic', color='#000000',
            ha=ha, va='center', zorder=6)

def draw_generalization(ax, e_from, e_to, label=""):
    p_from = get_ellipse_border(e_from[0], e_from[1], e_from[2], e_from[3], e_to[0], e_to[1])
    p_to   = get_ellipse_border(e_to[0], e_to[1], e_to[2], e_to[3], e_from[0], e_from[1])

    dx = p_to[0] - p_from[0]
    dy = p_to[1] - p_from[1]
    L = np.hypot(dx, dy)
    if L == 0:
        return
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux

    tri_len = 0.42
    tri_w = 0.26

    bx = p_to[0] - tri_len * ux
    by = p_to[1] - tri_len * uy

    v1 = (bx + tri_w * nx, by + tri_w * ny)
    v2 = (bx - tri_w * nx, by - tri_w * ny)

    ax.plot([p_from[0], bx], [p_from[1], by], color='#000000', lw=1.4, zorder=4)
    tri = patches.Polygon([p_to, v1, v2], closed=True, facecolor='#ffffff', edgecolor='#000000', lw=1.4, zorder=5)
    ax.add_patch(tri)

    if label:
        offset = 0.25
        tx = (p_from[0] + bx) / 2.0 + offset * nx
        ty = (p_from[1] + by) / 2.0 + offset * ny
        angle = np.degrees(np.arctan2(dy, dx))
        ax.text(tx, ty, label, fontsize=9.5, style='italic', color='#000000',
                rotation=angle, rotation_mode='anchor', ha='center', va='bottom', zorder=6)

def make_overall_uml():
    make_overall_uml_bw()

if __name__ == "__main__":
    from make_diagrams_bw import *
    print("Re-running make_diagrams_bw from make_diagrams...")
    make_overall_uml_bw()
    make_uc01_bw()
    make_uc02_bw()
    make_uc03_bw()
    make_uc04_bw()
    make_uc05_bw()
    make_uc06_bw()
    make_uc07_bw()
    make_uc08_bw()
    make_uc09_bw()
    make_uc10_bw()
