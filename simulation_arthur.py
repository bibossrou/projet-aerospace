import rocketpy
import datetime
import numpy as np
# Assure-toi que la classe PIDController dans test_pid gère le temps 't'
from test_pid import * # ==========================================
# 1. INITIALISATION DU CONTRÔLEUR TVC (Optimisé pour 11kg)
# ==========================================
# gains divisés par 2 par rapport à tes tests précédents pour éviter les oscillations sur une fusée plus légère
my_controller = PIDController(Kp=20, Ki=10, Kd=15, setpoint=90) 

def tvc_axis_controller(t, state):
    # Safety: On ne fait rien sur le rail pour éviter d'user les servos
    if t < 0.2: 
        return (0, 0, 1)

    # state[3] est l'angle d'inclinaison (theta) en radians
    theta_deg = np.degrees(state[3])
    
    # Calcul de la commande via le PID
    beta = my_controller.compute(theta_deg, t) 
    
    # Saturation physique (Gimbal limité à +/- 5 degrés)
    beta_limited = np.clip(beta, -5, 5)
    
    # Conversion en vecteur unitaire pour l'axe du moteur (déviation plan XZ)
    rad_beta = np.radians(beta_limited)
    return (np.sin(rad_beta), 0, np.cos(rad_beta))

# ==========================================
# 2. CONFIGURATION DE L'ENVIRONNEMENT
# ==========================================
env = rocketpy.Environment()
url = "http://weather.uwyo.edu/cgi-bin/sounding?region=samer&TYPE=TEXT%3ALIST&YEAR=2019&MONTH=02&FROM=0500&TO=0512&STNM=83779"
env.set_atmospheric_model(type="wyoming_sounding", file=url)


# ==========================================
# 3. RÉSERVOIR ET MOTEUR HYBRIDE
# ==========================================
oxidizer_liq = rocketpy.Fluid(name="Flui_test_liquide", density=1220)
oxidizer_gaz = rocketpy.Fluid(name='test_fluide_gaz', density=1.9277)
# Tank légèrement réduit pour gagner du poids
tank_shape = rocketpy.CylindricalTank(radius=0.15, height=0.8) 

tank_oxidizer = rocketpy.MassFlowRateBasedTank(
    name='Tank_test',
    geometry=tank_shape,
    flux_time=10.0,
    liquid=oxidizer_liq,
    gas=oxidizer_gaz,
    initial_liquid_mass=4.0, # Masse liquide réduite
    initial_gas_mass=0,
    liquid_mass_flow_rate_out=(4.0 - 0.200) / 10,
    liquid_mass_flow_rate_in=0,
    gas_mass_flow_rate_in=0,
    gas_mass_flow_rate_out=0
)

# Configuration Moteur standard pour TVC
# Configuration Moteur standard pour TVC
MoteurTest = rocketpy.HybridMotor(
    thrust_source=400,
    dry_mass=1.5,
    dry_inertia=(0.08, 0.08, 0.001),
    nozzle_radius=0.08,
    grain_number=6,
    grain_separation=0.005, # AJOUTÉ : 5mm de séparation entre les grains
    grain_outer_radius=0.05,
    grain_initial_inner_radius=0.02,
    grain_initial_height=0.15,
    grain_density=900,
    grains_center_of_mass_position=0.35,
    center_of_dry_mass_position=0.15,
    nozzle_position=-0.5,
    burn_time=10,
    throat_radius=0.03
)

# Injection critique du TVC
MoteurTest.axis = tvc_axis_controller 
MoteurTest.add_tank(tank_oxidizer, position=0.8)

# ==========================================
# 4. LA FUSÉE (Allégée et Optimisée)
# ==========================================
fusee_essai = rocketpy.Rocket(
    radius=0.18, # Diamètre réduit pour l'aéro
    mass=11, # NOUVELLE MASSE CIBLE
    inertia=(4.5, 4.5, 0.02), # Inerties recalculées pour 11kg
    power_on_drag=0.35, # Meilleur Cx
    power_off_drag=0.4,
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose"
)

fusee_essai.add_motor(MoteurTest, position=-0.7)
fusee_essai.add_nose(length=0.4, kind='tangent', position=1.1)

# Ailerons réduits (moins de traînée, moins de perturbation TVC)
fusee_essai.add_trapezoidal_fins(n=4, span=0.25, root_chord=0.35, tip_chord=0.08, position=-0.6, cant_angle=0)

# ==========================================
# 5. PARACHUTE ET SIMULATION
# ==========================================
def parachute_trigger(p, h, y):
    return True if y[2] < 1000 and y[5] < 0 else False # Déploiement à 1000m
    
fusee_essai.add_parachute(cd_s=4.0, name="parachute", trigger=parachute_trigger, sampling_rate=200, lag=1.5)

vol_simu = rocketpy.Flight(
    rocket=fusee_essai,
    environment=env,
    rail_length=5.0,
    inclination=87, # Plus verticale pour aider le TVC au départ
    heading=90
)

# ==========================================
# 6. AFFICHAGE DES RÉSULTATS
# ==========================================

fusee_essai.draw()
vol_simu.info()
# Les plots essentiels pour vérifier le TVC
vol_simu.plots.trajectory_3d()
vol_simu.plots.angular_kinematics_data() # Vérifie si omega_1 s'amortit vers 0