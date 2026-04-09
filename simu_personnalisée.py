'''
=====================================
Objectif de ce code: uitlisant rocketpy, créer une simulisation personnable plus facilement. 
pour ça il va y avoir importation d'un csv cntenant les infos nécessaires: en commençant par le moteur.
ensuite il va y avoir ajout d'une fonction d'importation de csv pour définir la fussée(taille, poids, type de coiffe, etc...).
Avec ces ajouts il sera plus simple de modifier la simulation. L'idéal serait d'en faire une interface graphique, maiss flemmme pour le moment.
=====================================
'''


import rocketpy
import numpy as np #numpy pour la courbe de poussée
import pandas as pd #pandas pour les csv à types multiples
import datetime
"""
pour faire fonctionner le code, il faut avoir plusieurs csv: un pour les frottements avec le moteur actif(PowerOndrag), un pour les frottementss avec le moteur inactif(PowerOffdrag),
un pour la courbe de pousssée(un .csv, voir docu rocketpy) ou un fichier .eng(rempli le même role),
un avec les sspécificationss du moteur solide,
un avec les spécifications du moteur liquide,
un avec les spécifications générales,
et un avec les spécifications de la fusée.

Avec la subdivision entre moteur solide et moteur liquide c'est ainsi possible de faire un test full liquide, full solide ou hybride.
"""


### mettre en place l'environnement


demain = datetime.date.today() + datetime.timedelta(days= 1) #mettre la date de la simulation à demain
date_info = (demain.year, demain.month, demain.day, 12)  # Heure de demain, à 12h00
env = rocketpy.Environment(latitude= 46.336, longitude=6.465, elevation= 750, date = date_info) #définuir la position, et l'atlitude. ici à allinges, petit village d'où Arthur A1 viens
env.set_atmospheric_model(type = "Windy", file = "ICONEU") #modèle de forecast en utilisant windy, disponible en europe. Prévisions max ssur 7 jours

#env.info() --> checker les infos disponibles sur l'environnement.
### definiton des fonctions pour automatise els calculs:

def compute_dry_inertia(dry_mass, outer_radius, inner_radius, length):
    I_11 = (1/12) * dry_mass * (3 * (outer_radius**2 + inner_radius**2) + length**2)
    I_22 = I_11  # symmetry
    I_33 = 0.5 * dry_mass * (outer_radius**2 + inner_radius**2)
    return (I_11, I_22, I_33)

def compute_rocket_inertia(mass, outer_radius, inner_radius, length):
    I_11 = (1/12) * mass * (3 * (outer_radius**2 + inner_radius**2) + length**2)
    I_22 = I_11  # symmetry
    I_33 = 0.5 * mass * (outer_radius**2 + inner_radius**2)
    return (I_11, I_22, I_33)

### définition des variables
common_var = pd.read_csv("exemple_motor_general.csv").iloc[0] #donner des noms aux variables, plus simple ensuite

nom_moteur = common_var["motor_name"]
dry_mass = common_var["dry_mass"]
nozzle_radius = common_var["nozzle_radius"]
center_of_dry_mass_position = common_var["center_of_dry_mass_position"]
nozzle_position = common_var["nozzle_position"]
burn_time = common_var["burn_time"]
reshape_thrust_curve = common_var["reshape"]
interpolation_method = common_var["interpolation_method"]
coordinate_system_orientation = common_var["orientation"]
reference_pressure = common_var["reference_pressure"]
longeur_moteur = common_var["motor_length"]
motor_inner_radius = common_var["motor_inner_radius"]
motor_outer_radius = common_var["motor_outer_radius"]
if (common_var["I11"] + common_var["I22"] + common_var["I33"]) == 0:
    (I_11, I_22, I_33) = compute_dry_inertia(dry_mass= dry_mass, outer_radius= motor_outer_radius, inner_radius= motor_inner_radius, length= longeur_moteur)
    dry_inertia = (I_11, I_22, I_33)
else:
    dry_inertia = (common_var["I11"], common_var["I22"], common_var["I33"])


### définition des variables - moteur solide
solid_var = pd.read_csv("exemple_moteur_solide.csv").iloc[0]

grain_number = int(solid_var["grain_number"])
grain_density = solid_var["grain_density"]
grain_outer_radius = solid_var["grain_outer_radius"]
grain_initial_inner_radius = solid_var["grain_initial_inner_radius"]
grain_initial_height = solid_var["grain_initial_height"]
grain_separation = solid_var["grain_separation"]
grains_center_of_mass_position = solid_var["grains_center_of_mass_position"]
throat_radius = solid_var["throat_radius"]
thrust_curve_file = "./Contrail_G123-HP.csv"

### définition des variables - moteur liquide
liquid_var = pd.read_csv("exemple_moteur_liquide.csv").iloc[0]

oxidizer_name = liquid_var["oxidizer_name"]
oxidizer_density_liquid = liquid_var["oxidizer_density_liquid"]
oxidizer_density_gas = liquid_var["oxidizer_density_gas"]
tank_radius = liquid_var["tank_radius"]
tank_length = liquid_var["tank_length"]
initial_liquid_mass = liquid_var["initial_liquid_mass"]
initial_gas_mass = liquid_var["initial_gas_mass"]
liquid_mass_flow_rate_out = liquid_var["liquid_mass_flow_rate_out"]
flux_time = liquid_var["flux_time"]
tank_position = liquid_var["tank_position"]
#tank_shape = liquid_var["tank shape"] --> je l'ai enlevé du csv, on part sur des réservoir cylindricaux h24

### sélection du type de moteur
solid_csv = "exemple_moteur_solide.csv"   # mettre None si pas de partie solide
liquid_csv = "exemple_moteur_liquide.csv" # mettre None si pas de partie liquide

if solid_csv and not liquid_csv:
    # Moteur solide uniquement
    moteur = rocketpy.SolidMotor(
        thrust_source = thrust_curve_file,
        dry_mass = dry_mass,
        dry_inertia = dry_inertia,
        nozzle_radius = nozzle_radius,
        center_of_dry_mass_position = center_of_dry_mass_position,
        nozzle_position = nozzle_position,
        burn_time = burn_time,
        grain_number = grain_number,
        grain_density = grain_density,
        grain_outer_radius = grain_outer_radius,
        grain_initial_inner_radius = grain_initial_inner_radius,
        grain_initial_height = grain_initial_height,
        grain_separation = grain_separation,
        grains_center_of_mass_position = grains_center_of_mass_position,
        throat_radius = throat_radius,
        reshape_thrust_curve = reshape_thrust_curve,
        interpolation_method = interpolation_method,
        coordinate_system_orientation = coordinate_system_orientation,
        reference_pressure = reference_pressure,
    )

elif liquid_csv and not solid_csv:
    # Moteur liquide uniquement
    oxidant_liquide = rocketpy.Fluid(name = oxidizer_name, density = oxidizer_density_liquid)
    oxidant_gaz = rocketpy.Fluid(name = oxidizer_name + "_gaz", density = oxidizer_density_gas)
    tank_shape = rocketpy.CylindricalTank(radius = tank_radius, height = tank_length)
    tank = rocketpy.MassFlowRateBasedTank(
        name = oxidizer_name + "_tank",
        geometry = tank_shape,
        flux_time = flux_time,
        liquid = oxidant_liquide,
        gas = oxidant_gaz,
        initial_liquid_mass = initial_liquid_mass,
        initial_gas_mass = initial_gas_mass,
        liquid_mass_flow_rate_in = 0,
        liquid_mass_flow_rate_out = liquid_mass_flow_rate_out,
        gas_mass_flow_rate_in = 0,
        gas_mass_flow_rate_out = 0,
    )
    moteur = rocketpy.LiquidMotor(
        thrust_source = thrust_curve_file,
        dry_mass = dry_mass,
        dry_inertia = dry_inertia,
        nozzle_radius = nozzle_radius,
        center_of_dry_mass_position = center_of_dry_mass_position,
        nozzle_position = nozzle_position,
        burn_time = burn_time,
        reshape_thrust_curve = reshape_thrust_curve,
        interpolation_method = interpolation_method,
        coordinate_system_orientation = coordinate_system_orientation,
        reference_pressure = reference_pressure,
    )
    moteur.add_tank(tank, position = tank_position)

elif solid_csv and liquid_csv:
    # Moteur hybride
    oxidant_liquide = rocketpy.Fluid(name = oxidizer_name, density = oxidizer_density_liquid)
    oxidant_gaz = rocketpy.Fluid(name = oxidizer_name + "_gaz", density = oxidizer_density_gas)
    tank_shape = rocketpy.CylindricalTank(radius = tank_radius, height = tank_length)
    tank = rocketpy.MassFlowRateBasedTank(
        name = oxidizer_name + "_tank",
        geometry = tank_shape,
        flux_time = flux_time,
        liquid = oxidant_liquide,
        gas = oxidant_gaz,
        initial_liquid_mass = initial_liquid_mass,
        initial_gas_mass = initial_gas_mass,
        liquid_mass_flow_rate_in = 0,
        liquid_mass_flow_rate_out = liquid_mass_flow_rate_out-0.000000000001,
        gas_mass_flow_rate_in = 0,
        gas_mass_flow_rate_out = 0,
    )
    moteur = rocketpy.HybridMotor(
        thrust_source = thrust_curve_file,
        dry_mass = dry_mass,
        dry_inertia = dry_inertia,
        nozzle_radius = nozzle_radius,
        center_of_dry_mass_position = center_of_dry_mass_position,
        nozzle_position = nozzle_position,
        burn_time = burn_time,
        grain_number = grain_number,
        grain_density = grain_density,
        grain_outer_radius = grain_outer_radius,
        grain_initial_inner_radius = grain_initial_inner_radius,
        grain_initial_height = grain_initial_height,
        grain_separation = grain_separation,
        grains_center_of_mass_position = grains_center_of_mass_position,
        throat_radius = throat_radius,
        reshape_thrust_curve = reshape_thrust_curve,
        interpolation_method = interpolation_method,
        coordinate_system_orientation = coordinate_system_orientation,
        reference_pressure = reference_pressure,
    )
    moteur.add_tank(tank, position = tank_position)

else:
    raise ValueError("Aucun fichier moteur spécifié — définir solid_csv et/ou liquid_csv.")



'''
===================================
Fin de la définition du moteur, les 3 sont possibles.
===================================
'''



"""
Début de la définition de la fusée en elle même.
"""

fusee_essai = rocketpy.Rocket( #valeur un peu aléatoire, encore pour voir ce que la simulation fait.
    radius= 0.125/2,
    mass = 4,
   inertia = (0.585, 0.585, 0.008), #aucne idée de ce que ceci fait exactement
    power_on_drag= "./test_PowerOnDrag.csv",
    power_off_drag= "./test_powerOffDrag.csv",
    center_of_mass_without_motor= 0,
    coordinate_system_orientation= "tail_to_nose"
    )

fusee_essai.add_motor(moteur, position = -0.6)


fin_groupe = fusee_essai.add_trapezoidal_fins(
    n = 4,
    span = 0.15,
    root_chord= 0.2,
    tip_chord= 0.03,
    position = -0.4,
    cant_angle= 4)

tail = fusee_essai.add_tail(
    top_radius= 0.125/2,
    bottom_radius= (0.125+0.05)/2,
    position = -0.6,
    length= 0.15)
def parachute_tiré(p, h, y):
    if y[2] < 300 and y[5] < 0: #y[2] est la hauteur, est y[5] est la vitesse sur l'axe z, donc la vitesse verticale. --> ca fait qui le parachute se déploie si la hauteur est inférieure à 1200m et que la vitesse verticale est négative
        return True
    else:
        return False
    

    