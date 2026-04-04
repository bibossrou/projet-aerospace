#pip install datetime
import rocketpy
import datetime
from rocketpy.utilities import apogee_by_mass, liftoff_speed_by_mass



demain = datetime.date.today() + datetime.timedelta(days= 1) #mettre la date de la simulation à demain
date_info = (demain.year, demain.month, demain.day, 12)  # Hour given in UTC time

env = rocketpy.Environment(latitude= 48.866667, longitude=2.333333, elevation= 0, date = date_info) #définuir la position, et l'atlitude

env.set_atmospheric_model(type = "Windy", file = "ICONEU") #modèle de forecast en utilisant windy, disponible en europe.
env.max_expected_height = 4000 #hauteur maximum de 3000 mètres, ceci va diminuer le calcul fait, et l'arré^ter à 3'000 mètres.
#env.all_info()
oxidizer_liq = rocketpy.Fluid(name = "Protoxide d'azote", density = 1223) #notre oxidizant liquide, du protoxide d'azote
oxidizer_gaz = rocketpy.Fluid(name = 'test_fluide_gaz', density = 1.80) #notre oxidisant gaz

tank_shape = rocketpy.CylindricalTank(radius= 0.04, height = 0.8) #forme du tank, dans ce cas cylindrical de hauteur 1m et diametre 30 cm.


tank_oxidizer = rocketpy.MassFlowRateBasedTank( #le conteneur du carbu liquide
name = 'Tank_test',
geometry = tank_shape,
flux_time= 8.4,
liquid = oxidizer_liq,
gas = oxidizer_gaz,
initial_liquid_mass= 0.315, #en utilisant les svaleurss du moteur en question.
initial_gas_mass= 0,
liquid_mass_flow_rate_in=0 ,
liquid_mass_flow_rate_out= (0.315-0.0000001)/8.4, #il faut mettre une valeur un peu en dessous de la masse initial du liquide, d'où le -0.01
# liquid_mass_flow_rate_out = (tank_oxidizer.initial_liquid_mass - 0.01)/tank_oxidizer.flux_time,
gas_mass_flow_rate_in= 0,
gas_mass_flow_rate_out=0,
)



MoteurTest = rocketpy.HybridMotor( #valeurs un peu aléatoires pour voir ce que ça fait, et les modifier pour observer --> utilisation du moteur G123_HP(à peu près ce que l'on cherche).
thrust_source= "./RATT_K240H.csv", #changer le nom du csv
interpolation_method= "linear",
dry_mass= (2.814-1.293),
dry_inertia = (0.105, 0.105, 0.00138), # Inertie centre de masse quand tout le carburant est recgargé, calculé en utilisant l'aide de différentes ia.    
nozzle_radius= 0.020, #approx 4 x pi x throat_radiuss^2.
grain_number= 6,
grain_separation= 0,
grain_outer_radius= 0.058,
grain_initial_inner_radius= 0.048,
grain_initial_height= (0.908/8),
grain_density= 900,
grains_center_of_mass_position=0.380,
center_of_dry_mass_position= 0.220,
nozzle_position= -0.10,
burn_time= 8.4,
throat_radius=  0.01)

MoteurTest.add_tank(tank_oxidizer, position= 1.150)

#MoteurTest.all_info()
#MoteurTest.plots.all()
MoteurTest.plots.thrust()



fusee_essai = rocketpy.Rocket( #valeur un peu aléatoire, encore pour voir ce que la simulation fait.
    radius= 0.125/2,
    mass = 4,
   inertia = (0.585, 0.585, 0.008), #aucne idée de ce que ceci fait exactement
    power_on_drag= "./test_PowerOnDrag.csv",
    power_off_drag= "./test_powerOffDrag.csv",
    center_of_mass_without_motor= 0,
    coordinate_system_orientation= "tail_to_nose"
    )

fusee_essai.add_motor(MoteurTest, position= -0.6)

coiffe = fusee_essai.add_nose(length=0.25, kind = 'conical', position = 1.278) #tangent kind of cone looks the best

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
    length= 0.105)



def parachute_tiré(p, h, y):
    if y[2] < 300 and y[5] < 0: #y[2] est la hauteur, est y[5] est la vitesse sur l'axe z, donc la vitesse verticale. --> ca fait qui le parachute se déploie si la hauteur est inférieure à 1200m et que la vitesse verticale est négative
        return True
    else:
        return False
    

parachute_drogue = fusee_essai.add_parachute( #premier parachute, il va être déployé à l'apogee. 
    cd_s = 0.5,
    name = "drogue_parachute",
    trigger= "apogee" #il s'active à l'apogee
)

parachute = fusee_essai.add_parachute(
    cd_s = 10,
    name = "parachute",
    trigger = parachute_tiré,
    sampling_rate= 100,
    lag = 1.0,
    noise = (0, 20, 0.5))


fusee_essai.draw() #dessiner pour voir ce à quoi elle ressemble, avant d'ajouter tout le bazar.

"""
Fin de la définition de la fusée.
"""



#fusee_essai.plots.all() #soyons fous et dessinons tous ce qu'on peut dessiner
fusee_essai.plots.static_margin() #il faut une valeure positive entre 1.5 et 2 --> plus c'est élevé plus la fusée sera stable, mais si c'est trop élevé la simulation ne marchera aps

#fusee_essai.all_info()





"""
Début de la simulation.
"""




vol_simu = rocketpy.Flight(
    rocket = fusee_essai, environment = env, rail_length = 4.0, inclination = 90, heading=  270)

vol_simu.info()
vol_simu.plots.trajectory_3d()
#vol_simu.all_info()



### Analysis of the simulation:

#apogee_by_mass(vol_simu, min_mass = 7, max_mass = 15, points = 5, plot = True)


#liftoff_speed_by_mass(flight = vol_simu, min_mass = 7, max_mass = 15, points= 5, plot = True)