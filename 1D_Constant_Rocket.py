# 1D Rocket Program
# Drag off
import numpy as np
import matplotlib.pyplot as plt

mdry = 1.5
mprop = 0.5
tb = 2.0
T0 = 40.0
dt = 0.01 
m0 = mdry + mprop
g = 9.81
tmax = 30.0
rho = 1.225
Cd = 0.75
D = 0.075
A = np.pi * (D / 2) ** 2

compare_on = False
drag_on = False
graph_on = False

drag_inp = input("Include drag? yes or no\n> ").lower()
if drag_inp == "yes":
    drag_on = True
    compare_on = (input("Compare drag with no drag? yes or no\n> ").lower() == "yes")
elif drag_inp == "no":
    pass
else:
    raise ValueError("Please enter yes or no")
graph_inp = input("Show graphs? yes or no\n> ").lower()
if graph_inp == "yes":
    graph_on = True
elif graph_inp == "no":
    pass
else:
    raise ValueError("Please enter yes or no")


def simulate(include_drag: bool):
    t = np.arange(0, tmax + dt, dt)
    h = np.zeros_like(t)
    v = np.zeros_like(t)
    a = np.zeros_like(t)
    m = np.zeros_like(t)
    T = np.zeros_like(t)
    F_drag = np.zeros_like(t)
    apogee_found = False
    t_apogee = None
    h_apogee = None
    t_land = None
    v_land = None
    land_i = None
    mdot = mprop / tb

    def mass(t_i, mdot):
        if t_i < tb:
            return m0 - mdot * t_i
        else:
            return mdry
    
    def thrust(t_i):
        if t_i < tb:
            return T0
        else:
            return 0.0
    
    for i in range(1, len(t)):
        m_i = mass(t[i-1], mdot)
        m[i-1] = m_i
        T_i = thrust(t[i-1])
        T[i-1] = T_i

        if include_drag:
            F_drag[i-1] = -0.5 * rho * Cd * A * v[i-1] * np.abs(v[i-1])
        a[i-1] = (T[i-1] + F_drag[i-1]) / m[i-1] - g
        v[i] = v[i-1] + a[i-1] * dt
        h[i] = h[i-1] + v[i] * dt

        if (not apogee_found) and (v[i-1] > 0) and (v[i] <= 0):
            apogee_found = True
            alpha = v[i-1] / (v[i-1] - v[i]) 
            t_apogee = t[i-1] + alpha * dt
            h_apogee = h[i-1] + alpha * (h[i] - h[i-1])
        
        if apogee_found and (h[i-1] > 0) and (h[i] <= 0):
            land_i = i - 1
            alpha = -h[i-1] / (h[i] - h[i-1])
            t_land = t[i-1] + alpha * dt
            v_land = v[i-1] + alpha * (v[i] - v[i-1])
            h[i] = 0.0
            end = i + 1
            t = t[:end]; h = h[:end]; v = v[:end]; a = a[:end]
            m = m[:end]; T = T[:end]; F_drag = F_drag[:end]
            break
    
        m[-1] = mass(t[-1], mdot)
        T[-1] = thrust(t[-1])

    if land_i is None:
        raise RuntimeError("No landing detected. Increase tmax or check parameters.")
    if t_apogee is None:
        raise RuntimeError("No apogee detected. Check thrust/mass or dt.")
    
    if include_drag:
        F_drag[-1] = -0.5 * rho * Cd * A * v[-1] * np.abs(v[-1])
    a[-1] = (T[-1] + F_drag[-1]) / m[-1] - g

    burn_i = min(np.searchsorted(t, tb, side="left"), len(t)-1)

    return {
        "t": t,
        "h": h,
        "v": v,
        "a": a,
        "m": m,
        "T": T,
        "F_drag": F_drag,
        "burn_i": burn_i,
        "t_apogee": t_apogee,
        "h_apogee": h_apogee,
        "t_land": t_land,
        "land_i": land_i,
        "v_land": v_land
    }


def summarize(val):
    h = val["h"]
    v = val["v"]
    burn_i = val["burn_i"]
    return {
        "v_burn": v[burn_i],
        "t_apogee": val["t_apogee"],
        "h_apogee": val["h_apogee"],
        "t_land": val["t_land"],
        "vmax_up": np.max(v),
        "vmax_down": val["v_land"],
        "h_max": np.max(h),
        "Fdrag_max": np.max(np.abs(val["F_drag"]))
    }

val = None
val_nodrag = None
val_drag = None
info = None
info_nodrag = None
info_drag = None

if compare_on:
    val_nodrag = simulate(False)
    val_drag = simulate(True)

    info_nodrag = summarize(val_nodrag)
    info_drag = summarize(val_drag)

    print("\n\t\t\t\tRocket 1 (No Drag)\t\tRocket 2 (Drag)")
    print(f"Burnout Velocity:\t\t{info_nodrag['v_burn']:.2f} m/s\t\t\t{info_drag['v_burn']:.2f} m/s")
    print(
        f"Apogee Height and Time:\t\t"
        f"{info_nodrag['h_apogee']:.2f} m @"
        f" {info_nodrag['t_apogee']:.2f} s\t\t{info_drag['h_apogee']:.2f} m @ {info_drag['t_apogee']:.2f} s")
    print(f"Landing Time:\t\t\t{info_nodrag['t_land']:.2f} s\t\t\t\t{info_drag['t_land']:.2f} s")
    print(f"Max Upward Speed:\t\t{info_nodrag['vmax_up']:.2f} m/s\t\t\t{info_drag['vmax_up']:.2f} m/s")
    print(f"Impact Velocity:\t\t{info_nodrag['vmax_down']:.2f} m/s\t\t\t{info_drag['vmax_down']:.2f} m/s")
    print(f"Max Drag Force:\t\t\t0.00 N\t\t\t\t{info_drag['Fdrag_max']:.2f} N")

else:
    val = simulate(drag_on)
    info = summarize(val)

    print(f"\nBurnout Velocity:\t\t{info['v_burn']:.2f} m/s")
    print(f"Apogee Height and Time:\t\t{info['h_apogee']:.2f} m @ {info['t_apogee']:.2f} s")
    print(f"Landing Time:\t\t\t{info['t_land']:.2f} s")
    print(f"Max Upward Speed:\t\t{info['vmax_up']:.2f} m/s")
    print(f"Impact Velocity:\t\t{info['vmax_down']:.2f} m/s")
    print(f"Max Drag Force:\t\t\t{info['Fdrag_max']:.2f} N") if drag_on else None


def plot_altitude(val, label=None, mark_events=True):
    t = val["t"]
    h = val["h"]
    burn_i = val["burn_i"]
    t_apogee = val["t_apogee"]
    h_apogee = val["h_apogee"]
    t_land = val["t_land"]
    land_i = val["land_i"]

    end = land_i + 2
    plt.plot(t[:end], h[:end], label=label)
    
    if mark_events:
        plt.scatter(t[burn_i], h[burn_i])
        plt.scatter(t_apogee, h_apogee)
        plt.scatter(t_land, 0.0)
        plt.annotate("Burnout", (t[burn_i], h[burn_i]), textcoords="offset points", xytext=(10,10))
        plt.annotate("Apogee", (t_apogee, h_apogee), textcoords="offset points", xytext=(10,3))
        plt.annotate("Landing", (t_land, 0), textcoords="offset points", xytext=(10,10))


def plot_velocity(val, label=None, mark_events=True):
    t = val["t"]
    v = val["v"]
    land_i = val["land_i"]
    t_apogee = val["t_apogee"]

    end = land_i + 2
    plt.plot(t[:end], v[:end], label=label)
    
    
    if mark_events:
        plt.scatter(t_apogee, 0.0)
        plt.annotate("Apogee", (t_apogee, 0.0), textcoords="offset points", xytext=(10,10))


def plot_acceleration(val, label=None, mark_events=True):
    t = val["t"]
    a = val["a"]
    burn_i = val["burn_i"]
    land_i = val["land_i"]

    end = land_i + 2
    plt.plot(t[:end], a[:end], label=label)

    if mark_events:
        plt.scatter(t[burn_i], a[burn_i])
        plt.annotate("Burnout", (t[burn_i], a[burn_i]), textcoords="offset points", xytext=(10,10))

if graph_on:

    # Altitude vs Time
    plt.figure()
    if compare_on:
        plot_altitude(val_nodrag, label="No Drag", mark_events=False)
        plot_altitude(val_drag, label="Drag", mark_events=False)
        plt.legend()

    else:
        plot_altitude(val, mark_events=True)

    plt.xlabel("Time (s)")
    plt.ylabel("Altitude (m)")
    plt.title("Altitude vs Time")
    plt.grid(True)
    plt.savefig("altitude.png", dpi=250, bbox_inches="tight")
    plt.show(block=True)

    # Velocity vs Time
    plt.figure()
    if compare_on:
        plot_velocity(val_nodrag, label="No Drag", mark_events=False)
        plot_velocity(val_drag, label="Drag", mark_events=False)
        plt.legend()
    else:
        plot_velocity(val, mark_events=True)

    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.title("Velocity vs Time")
    plt.grid(True)
    plt.savefig("velocity.png", dpi=250, bbox_inches="tight")
    plt.show(block=True)

    # Acceleration vs Time
    plt.figure()
    if compare_on:
        plot_acceleration(val_nodrag, label="No Drag", mark_events=False)
        plot_acceleration(val_drag, label="Drag", mark_events=False)
        plt.legend()
    else:
        plot_acceleration(val, mark_events=True)
        
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s^2)")
    plt.title("Acceleration vs Time")
    plt.grid(True)
    plt.savefig("acceleration.png", dpi=250, bbox_inches="tight")
    plt.show(block=True)
