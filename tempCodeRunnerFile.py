import rocketpy
import datetime
import numpy as np
from test_pid import *

# 1. Initialisation du contrôleur
# Note : Pour un TVC, un setpoint à 90 (verticale) est correct si state[3] est l'inclinaison.
my_controller = PIDController(Kp=40, Ki=50, Kd=30, setpoint=90)

# 2. La fonction de contrôle "Gimbal"
# Elle doit retourner le vecteur directionnel du moteur (x, y, z)
def tvc_axis_controller(t, state):
    # state[3] est l'angle d'inclinaison (theta) en radians dans RocketPy
    theta_deg = np.degrees(state[3])
    
    # Calcul de l'angle de déviation (beta) via ton PID
    beta = my_controller.compute(theta_deg, t) 
    
    # Saturation physique : un gimbal dépasse rarement 5 à 10 degrés
    beta_limited = np.clip(beta, -5, 5)
    
    # Conversion en vecteur unitaire pour l'axe du moteur
    # On dévie dans le plan XZ (tangage)
    rad_beta = np.radians(beta_limited)
    return (np.sin(rad_beta), 0, np.cos(rad_beta))

# --- ENVIRONNEMENT ---
env = rocketpy.Environment()
url = "http://weather.uwyo.edu/cgi-bin/sounding?region=samer&TYPE=TEXT%3ALIST&YEAR=2019&MONTH=02&FROM=0500&TO=0512&STNM=83779"
env.set_atmospheric_model(type="wyoming_sounding", file=url)

# --- RÉSERVOIR ET FLUIDES ---
oxidizer_liq = rocketpy.Fluid(name="Flui_test_liquide", density=1220)
oxidizer_gaz = rocketpy.Fluid(name='test_fluide_gaz', density=1.9277)
tank_shape = rocketpy.CylindricalTank(radius=0.20, height=1.0)

tank_oxidizer = rocketpy.MassFlowRateBasedTank(
    name='Tank_test',
    geometry=tank_shape,
    flux_time=10.0,
    liquid=oxidizer_liq,
    gas=oxidizer_gaz,
    initial_liquid_mass=5.0,
    initial_gas_mass=0,
    # Débit liquide sortant (ton calcul actuel)
    liquid_mass_flow_rate_out=(5.0 - 0.250) / 10,
    # Arguments manquants à mettre à 0
    liquid_mass_flow_rate_in=0,
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=0
)

# On définit d'abord le moteur avec les arguments standards
MoteurTest = rocketpy.HybridMotor(
    thrust_source=1500,
    dry_mass=2,
    dry_inertia=(0.125, 0.125, 0.002),
    nozzle_radius=0.11,
    grain_number=8,
    grain_separation=0,
    grain_outer_radius=0.0575,
    grain_initial_inner_radius=0.025,
    grain_initial_height=0.1775,
    grain_density=900,
    grains_center_of_mass_position=0.410,
    center_of_dry_mass_position=0.200,
    nozzle_position=-0.6,
    burn_time=10,
    throat_radius=0.04
)

MoteurTest.axis = tvc_axis_controller

MoteurTest.add_tank(tank_oxidizer, position=1.0615)

# --- FUSÉE ---
fusee_essai = rocketpy.Rocket(
    radius=0.22,
    mass=15,
    inertia=(6.321, 6.321, 0.034),
    power_on_drag=0.4, # Valeur fixe pour éviter l'erreur si le CSV manque
    power_off_drag=0.4,
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose"
)

fusee_essai.add_motor(MoteurTest, position=-0.9)
fusee_essai.add_nose(length=0.5, kind='tangent', position=1.278)

# Attention : cant_angle=15 crée un roulis important, ce qui complique le job du TVC
fusee_essai.add_trapezoidal_fins(n=4, span=0.40, root_chord=0.5, tip_chord=0.09, position=-0.8, cant_angle=0)

# --- PARACHUTE ---
def parachute_trigger(p, h, y):
    return True if y[2] < 1200 and y[5] < 0 else False
    
fusee_essai.add_parachute(cd_s=5.0, name="parachute", trigger=parachute_trigger, sampling_rate=200, lag=1.5)

# --- SIMULATION ---
vol_simu = rocketpy.Flight(
    rocket=fusee_essai,
    environment=env,
    rail_length=5.0,
    inclination=85,
    heading=90
)

vol_simu.info()
vol_simu.plots.trajectory_3d() # Pour voir la "tête" de la trajectoire
vol_simu.plots.angular_kinematics_data() # Pour voir les vitesses et accélérations angulaires