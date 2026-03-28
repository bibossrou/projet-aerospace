'''import rocketpy
import datetime
demain = datetime.date.today() + datetime.timedelta(days= 1) #mettre la date de la simulation à demain


env = rocketpy.Environment(latitude= 48.866667, longitude=2.333333, elevation= 60, date = demain) #définuir la position, et l'atlitude


env.set_atmospheric_model(type="Windy", file="ECMWF")
env_windy_ecmwf = env
env_windy_ecmwf.plots.all()'''

from rocketpy import Environment
import datetime

 #définuir la position, et l'atlitude
demain = datetime.date.today() + datetime.timedelta(days= 1) #mettre la date de la simulation à demain
date_info = (demain.year, demain.month, demain.day, 12)  # Hour given in UTC time
env = Environment(latitude= 48.866667, longitude=2.333333, elevation= 60, date = date_info)

env.set_atmospheric_model(type = "Windy", file = "ICONEU") #modèle de forecast en utilisant windy, disponible en europe.
print("Tomorrow's date:", date_info)

env.all_info()