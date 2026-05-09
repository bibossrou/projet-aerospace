import rocketpy 
import datetime
from rocketpy.utilities import apogee_by_mass, liftoff_speed_by_mass



demain = datetime.date.today() + datetime.timedelta(days= 1) #mettre la date de la simulation à demain
date_info = (demain.year, demain.month, demain.day, 12)  # Hour given in UTC time

env = rocketpy.Environment(latitude= 48.866667, longitude=2.333333, elevation= 0, date = date_info) #définuir la position, et l'atlitude

env.set_atmospheric_model(type = "Windy", file = "ICONEU") #modèle de forecast en utilisant windy, disponible en europe.
#env.set_atmospheric_model(type = 'custom_atmosphere', wind_u = 20, wind_v = 20)
env.max_expected_height = 4000 #hauteur maximum de 3000 mètres, ceci va diminuer le calcul fait, et l'arré^ter à 3'000 mètres.
#env.all_info()



## Calcul de l'inertie(on remercie claude bien comme il faut):

import numpy as np

# --- Geometry (from drawing, in meters) ---
R_out = 47.50 / 2 / 1000      # 23.75mm
R_in  = 15.88 / 2 / 1000      # 7.94mm  (core radius)
h_aft = 101.60 / 1000          # aft grain height
h_fwd = 212.47 / 1000          # fwd grain height

# --- Propellant mass (from .rse) ---
prop_mass_total = 0.840        # kg

# --- Grain volumes ---
V_aft = np.pi * (R_out**2 - R_in**2) * h_aft
V_fwd = np.pi * (R_out**2 - R_in**2) * h_fwd
V_total = V_aft + V_fwd

# --- Grain density ---
grain_density = prop_mass_total / V_total
print(f"Grain density: {grain_density:.2f} kg/m³")

# --- Individual grain masses ---
m_aft = grain_density * V_aft
m_fwd = grain_density * V_fwd

# --- Inertia for each grain (hollow cylinder) ---
def inertia(m, R_out, R_in, h):
    I33 = 0.5 * m * (R_out**2 + R_in**2)                        # axial
    I11 = (1/12) * m * (3*(R_out**2 + R_in**2) + h**2)          # transverse
    return I11, I33

I11_aft, I33_aft = inertia(m_aft, R_out, R_in, h_aft)
I11_fwd, I33_fwd = inertia(m_fwd, R_out, R_in, h_fwd)

# --- Total dry inertia (sum of both grains) ---
I11_total = I11_aft + I11_fwd
I33_total = I33_aft + I33_fwd


moteur_test = rocketpy.SolidMotor(
    thrust_source = "./Aerotech_K76WN-P.eng", #fichier .eng avec plus d'infos
        # --- Nozzle ---
    nozzle_radius=27.0 / 1000,       # 54mm hybrid nozzle → radius = 27mm (case fit)
    throat_radius=7.95/2 / 1000,       # Ø0.313 inches = 7.95mm diameter → radius = 3.975mm
    nozzle_position=-0.16,               # aft end reference

    # --- Grains (2 grains: 1 aft + 1 fwd) ---
    grain_number=2,
    grain_outer_radius=47.50 / 2 / 1000,        # 1.87" O.D. = 47.50mm → radius = 23.75mm
    grain_initial_inner_radius=15.88 / 2 / 1000, # 0.625" core = 15.88mm → radius = 7.94mm
    grain_initial_height=120.0 / 1000,           #  Average of aft (101.6mm) and fwd (212.47mm)
    grain_separation=5 / 1000,       #  Not specified in drawing, using typical 5mm default

    # --- Mass & Inertia (not in drawing) ---
    dry_mass=0.4379,                    
    dry_inertia=(I11_total, I11_total, I33_total),  

    # --- Center of mass positions (not in drawing) ---
    grains_center_of_mass_position=0.16,   
    center_of_dry_mass_position=0.16,      

    # --- Burn time (not in drawing) ---
    burn_time=20.576,                  

    grain_density=grain_density,      #calculer à partir de la masse total et du volume total des grains        

    coordinate_system_orientation="nozzle_to_combustion_chamber",
)

fusee_solide = rocketpy.Rocket( #valeur un peu aléatoire, encore pour voir ce que la simulation fait.
    radius= 0.125/2,
    mass = 4,
    inertia = (1.4545, 1.4545, 0.0138), #aucne idée de ce que ceci fait exactement
    power_on_drag= "./test_PowerOnDrag.csv",
    power_off_drag= "./test_powerOffDrag.csv",
    center_of_mass_without_motor= 0.874,
    coordinate_system_orientation= "tail_to_nose"
    )


fusee_solide.add_motor(moteur_test, position= -0.30) #-0.36 pour que ca soit bien casé bien comme il faut



fusee_solide.add_nose(length = 0.25, kind = "conical", position = 1.50)

def parachute_tiré(p, h, y):
    if y[2] < 300 and y[5] < 0: #y[2] est la hauteur, est y[5] est la vitesse sur l'axe z, donc la vitesse verticale. --> ca fait qui le parachute se déploie si la hauteur est inférieure à 1200m et que la vitesse verticale est négative
        return True
    else:
        return False
    

parachute_drogue = fusee_solide.add_parachute( #premier parachute, il va être déployé à l'apogee. 
    cd_s = 0.3,
    name = "drogue_parachute",
    trigger= "apogee" #il s'active à l'apogee
)

parachute = fusee_solide.add_parachute(
    cd_s = 10,
    name = "parachute_principal",
    trigger = parachute_tiré,
    sampling_rate= 100,
    lag = 1.0,
    noise = (0, 10, 0.3))

fusee_solide.add_tail( position= -0.38, length = 0.08, top_radius = 0.125/2, bottom_radius= (0.125/2)/2) #meme rayon en haut que celui de la fusee
fusee_solide.add_trapezoidal_fins( n = 4, span = 0.20, root_chord = 0.18, tip_chord = 0.02, position = -0.38 + 0.03 + 0.18, cant_angle = 4)
fusee_solide.draw() #dessiner pour voir ce à quoi elle ressemble, avant d'ajouter tout le bazar.

simulation_basique = rocketpy.Flight(rocket = fusee_solide, environment = env, inclination= 85, heading = 0, rail_length= 4)


simulation_basique.all_info()