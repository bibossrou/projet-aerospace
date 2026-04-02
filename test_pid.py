import numpy as np
import matplotlib.pyplot as plt
import time

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.previous_error = 0
        self.integral = 0

    def compute(self, process_variable, dt):
            # Calculate error
            error = self.setpoint - process_variable
            
            # Proportional term
            P_out = self.Kp * error
            
            # Integral term
            self.integral += error * dt
            I_out = self.Ki * self.integral
            
            # Derivative term
            derivative = (error - self.previous_error) / dt
            D_out = self.Kd * derivative
            
            # Compute total output
            output = P_out + I_out + D_out
            
            # Update previous error
            self.previous_error = error
            
            return output

masse = 1     # Inertie de ton système

'''
#bonne valeur du pid, faible erreur mais trop lent
Kp = 1.5*masse
Ki = 0.5*masse
Kd = 15*masse
'''
'''
#bonne valeur du PID, réactif et erreur faible
Kp = 10*masse
Ki = 0.5*masse
Kd = 15*masse
'''
Kp = 40*masse
Ki = 50*masse
Kd = 30*masse


L = []

start = time.perf_counter()
PID = PIDController(Kp, Ki, Kd, 90) #0 pour l'angle attendue
x0 = 80 #l'angle qu'on a

L.append(x0)
# Initialisation physique
x = x0         # Position (angle)
vitesse = 0     # Vitesse angulaire

dt = 0.02

for i in range(500): # On augmente un peu car l'inertie ralentit tout
    # 1. Le PID calcule la FORCE à appliquer
    force = PID.compute(x, dt)
    
    # 2. Physique : Accélération = Force / Masse


    vent_constant = 0.1*i #m/s vent augmentant avec l'altitude

    acceleration = (force+vent_constant) / masse
    
    # 3. Physique : Vitesse = Vitesse + Accélération * dt
    vitesse += acceleration * dt

    
    # Simulation d'une rafale de vent à l'itération 50
    if i == 50:
        vitesse += 45.0  # On donne un gros coup de pouce soudain
        print(f"--- RAFALE DE VENT ! {vitesse} m/s ---")
    
    
    # 4. Physique : Position = Position + Vitesse * dt
    x += vitesse * dt
    print(x)
    L.append(x)

end =  time.perf_counter()
print(f"temps exec : {end-start} secondes")

plt.plot(L, marker='o', linestyle='-', label='Angle (process variable)')

# Piste pour l'axe X : afficher tous les indices
plt.xticks(range(len(L)))

# Piste pour la clarté : ajouter une ligne horizontale pour la consigne (setpoint)
plt.axhline(y=0, color='r', linestyle='--', label='Setpoint')

for k in range(1, 11):
    if k == 1:
        plt.axvline(x = k/dt, color='b', linestyle='--', label='repère (secondes)')

    else: plt.axvline(x = k/dt, color='b', linestyle='--')

plt.axhline(y=x0/20, color='r', linestyle='-', label='lim erreur 5%')
plt.axhline(y=-x0/20, color='r', linestyle='-')


plt.xlabel('Itérations')
plt.ylabel('Angle')
plt.title('Convergence du PID')
plt.legend()
plt.grid(False)
plt.show()