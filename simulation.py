import numpy as np
import matplotlib
matplotlib.use('Agg') # For headless environments
import matplotlib.pyplot as plt
import os

# Physical Constants
G = 6.67430e-11 # Gravitational constant (m^3 kg^-1 s^-2)
EARTH_MASS = 5.972e24 # Earth's mass (kg)
EARTH_RADIUS = 6.371e6 # Earth's radius (m)

def calculate_gravity(mass, height_above_surface):
    """
    Calculate the gravitational force on an object at a certain height.
    F = G * (M * m) / r^2
    Where r is Earth's radius + height_above_surface.
    """
    r_total = EARTH_RADIUS + height_above_surface
    force = G * (EARTH_MASS * mass) / (r_total ** 2)
    return force

def check_lift(gravity_force, opposing_force):
    """
    Check if the applied opposing force is greater than gravity.
    """
    return opposing_force > gravity_force

def generate_graph(mass, input_height, input_opposing_force):
    """
    Generates a matplotlib graph showing Gravity vs Opposing Force
    over different heights, and saves it to static/img/graph.png.
    """
    # Create heights from 0 to max(100, input_height * 2)
    max_height = max(100, input_height * 2)
    heights = np.linspace(0, max_height, 100)
    
    gravity_forces = []
    for h in heights:
        gravity_forces.append(calculate_gravity(mass, h))
        
    opposing_forces = [input_opposing_force] * 100 # Assuming constant opposing force
    
    plt.figure(figsize=(8, 5))
    plt.plot(heights, gravity_forces, label='Gravitational Force (N)', color='#0d6efd', linewidth=2)
    plt.plot(heights, opposing_forces, label='Opposing Force (N)', color='#dc3545', linestyle='--', linewidth=2)
    
    # Highlight the input point
    plt.scatter([input_height], [calculate_gravity(mass, input_height)], color='#0d6efd', zorder=5)
    plt.scatter([input_height], [input_opposing_force], color='#dc3545', zorder=5)
    
    plt.title('Force Analysis over Distance (Height)')
    plt.xlabel('Height above Ground (m)')
    plt.ylabel('Force (Newtons)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    
    # Ensure directory exists
    static_img_dir = os.path.join(os.path.dirname(__file__), 'static', 'img')
    os.makedirs(static_img_dir, exist_ok=True)
    
    graph_path = os.path.join(static_img_dir, 'graph.png')
    plt.savefig(graph_path)
    plt.close()
    
    return 'img/graph.png' # Relative path for HTML
