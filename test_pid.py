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


#bonne valeur du pid, erreur à 5%
Kp = 0.001
Ki = 0.000
Kd = 0.0005
L = []

start = time.perf_counter()
PID = PIDController(Kp, Ki, Kd, 0) #0 pour l'angle attendue
x0 = -3 #l'angle qu'on a
x = x0
dt = 0.01
L.append(x0)
for i in range(10):
    x = PID.compute(x, dt)
    L.append(x)
    print(x)
end = time.perf_counter()

print(f"temps exec : {end-start} secondes")




plt.plot(L, marker='o', linestyle='-', label='Angle (process variable)')

# Piste pour l'axe X : afficher tous les indices
plt.xticks(range(len(L)))

# Piste pour la clarté : ajouter une ligne horizontale pour la consigne (setpoint)
plt.axhline(y=0, color='r', linestyle='--', label='Setpoint')

plt.axhline(y=x0/10, color='r', linestyle='-', label='lim +')
plt.axhline(y=-x0/10, color='r', linestyle='-', label='lim -')


plt.xlabel('Itérations')
plt.ylabel('Angle')
plt.title('Convergence du PID')
plt.legend()
plt.grid(True)
plt.show()