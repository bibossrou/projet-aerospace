#pip install datetime
import rocketpy
import datetime


env = rocketpy.Environment(latitude= 48.866667, longitude=2.333333, elevation= 60) #définuir la position, et l'atlitude

demain = datetime.date.today() + datetime.timedelta(days= 1) #mettre la date de la simulation à demain


env.set_atmospheric_model(type = "standard_atmosphere") #modèles stancdard --> pas de vent
# env.info()
oxidizer_liq = rocketpy.Fluid(name = "Flui_test_liquide", density = 1220) #notre oxidizant liquide
oxidizer_gaz = rocketpy.Fluid(name = 'test_fluide_gaz', density = 1.9277) #notre oxidisant gaz

tank_shape = rocketpy.CylindricalTank(radius= 0.20, height = 1.0) #forme du tank, dans ce cas cylindrical de hauteur 1m et diametre 40 cm.


tank_oxidizer = rocketpy.MassFlowRateBasedTank( #le conteneur du carbu liquide
name = 'Tank_test',
geometry = tank_shape,
flux_time= 10.0,
liquid = oxidizer_liq,
gas = oxidizer_gaz,
initial_liquid_mass= 5.0,
initial_gas_mass= 0,
liquid_mass_flow_rate_in= 0,
liquid_mass_flow_rate_out= (5.0-0.250)/10,
gas_mass_flow_rate_in= 0,
gas_mass_flow_rate_out=0,
)



MoteurTest = rocketpy.HybridMotor(
thrust_source= 1000,
dry_mass= 2,



)



