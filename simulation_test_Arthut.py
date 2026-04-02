#pip install datetime
import rocketpy
import datetime
from rocketpy.utilities import apogee_by_mass, liftoff_speed_by_mass



demain = datetime.date.today() + datetime.timedelta(days= 1) #mettre la date de la simulation à demain
date_info = (demain.year, demain.month, demain.day, 12)  # Hour given in UTC time

env = rocketpy.Environment(latitude= 48.866667, longitude=2.333333, elevation= 60, date = date_info) #définuir la position, et l'atlitude

env.set_atmospheric_model(type = "Windy", file = "ICONEU") #modèle de forecast en utilisant windy, disponible en europe.
# env.info()
oxidizer_liq = rocketpy.Fluid(name = "Flui_test_liquide", density = 1220) #notre oxidizant liquide
oxidizer_gaz = rocketpy.Fluid(name = 'test_fluide_gaz', density = 1.9277) #notre oxidisant gaz

tank_shape = rocketpy.CylindricalTank(radius= 0.15, height = 1.0) #forme du tank, dans ce cas cylindrical de hauteur 1m et diametre 30 cm.


tank_oxidizer = rocketpy.MassFlowRateBasedTank( #le conteneur du carbu liquide
name = 'Tank_test',
geometry = tank_shape,
flux_time= 20.0,
liquid = oxidizer_liq,
gas = oxidizer_gaz,
initial_liquid_mass= 1.5,
initial_gas_mass= 0,
liquid_mass_flow_rate_in= 0,
liquid_mass_flow_rate_out= (1.5-0.01)/20.0, #il faut mettre une valeur un peu en dessous de la masse initial du liquide, d'où le -0.01
# liquid_mass_flow_rate_out = (tank_oxidizer.initial_liquid_mass - 0.01)/tank_oxidizer.flux_time,
gas_mass_flow_rate_in= 0,
gas_mass_flow_rate_out=0,
)



MoteurTest = rocketpy.HybridMotor( #valeurs un peu aléatoires pour voir ce que ça fait, et les modifier pour observer.
thrust_source= 350,
dry_mass= 1.5,
dry_inertia = (0.125, 0.125, 0.002),
nozzle_radius= 0.11,
grain_number= 8,
grain_separation= 0,
grain_outer_radius= 0.0575,
grain_initial_inner_radius= 0.025,
grain_initial_height= 0.1775,
grain_density= 900,
grains_center_of_mass_position=0.410,
center_of_dry_mass_position= 0.200,
nozzle_position= -0.6,
burn_time= 20.0,
throat_radius=  0.04)

MoteurTest.add_tank(tank_oxidizer, position= 1.160)

# MoteurTest.all_info()



fusee_essai = rocketpy.Rocket( #valeur un peu aléatoire, encore pour voir ce que la simulation fait.
    radius= 0.17,
    mass = 5,
    inertia = (6.321, 6.321, 0.034), #aucne idée de ce que ceci fait exactement
    power_on_drag= "./test_PowerOnDrag.csv",
    power_off_drag= "./test_powerOffDrag.csv",
    center_of_mass_without_motor= 0,
    coordinate_system_orientation= "tail_to_nose"
    )

fusee_essai.add_motor(MoteurTest, position= -0.9)

coiffe = fusee_essai.add_nose(length=0.5, kind = 'tangent', position = 1.278) #tangent kind of cone looks the best

fin_groupe = fusee_essai.add_trapezoidal_fins(
    n = 4,
    span = 0.40,
    root_chord= 0.5,
    tip_chord= 0.09,
    position = -0.8,
    cant_angle= 15)

tail = fusee_essai.add_tail(
    top_radius= 0.22,
    bottom_radius= 0.1,
    position = -1.3,
    length= 0.2)



def parachute_tiré(p, h, y):
    if y[2] < 600 and y[5] < 0: #y[2] est la hauteur, est y[5] est la vitesse sur l'axe z, donc la vitesse verticale. --> ca fait qui le parachute se déploie si la hauteur est inférieure à 1200m et que la vitesse verticale est négative
        return True
    else:
        return False
    

parachute = fusee_essai.add_parachute(
    cd_s = 5.0,
    name = "parachute",
    trigger = parachute_tiré,
    sampling_rate= 200,
    lag = 3.0,
    noise = (0, 20, 0.5))


fusee_essai.draw() #dessiner pour voir ce à quoi elle ressemble, avant d'ajouter tout le bazar.

"""
Fin de la définition de la fusée.
"""



#fusee_essai.plots.all() #soyons fous et dessinons tous ce qu'on peut dessiner
#fusee_essai.plots.static_margin() #il faut une valeure positive entre 1.5 et 2 --> plus c'est élevé plus la fusée sera stable, mais si c'est trop élevé la simulation ne marchera aps

#fusee_essai.all_info()





"""
Début de la simulation.
"""



'''
vol_simu = rocketpy.Flight(
    rocket = fusee_essai, environment = env, rail_length = 4.0, inclination = 80, heading=  90)

#vol_simu.info()
#vol_simu.plots.trajectory_3d()
vol_simu.all_info()

'''

### Analysis of the simulation:

#apogee_by_mass(vol_simu, min_mass = 5, max_mass = 20, points = 20, plot = True)


#liftoff_speed_by_mass(flight = vol_simu, min_mass = 5, max_mass = 20, points= 20, plot = True)