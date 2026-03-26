import numpy as np
import matplotlib.pyplot as plt


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

Kp = 0.0028
Ki = 0.002
Kd = 0.001

L = []

PID = PIDController(Kp, Ki, Kd, 0) #0 pour l'angle attendue
x = -3 #l'angle qu'on a
dt = 0.01
L.append(x)
for i in range(5):
    x = PID.compute(x, dt)
    L.append(x)
    print(x)

plt.plot(L, marker='o', linestyle='-', label='Angle (process variable)')

# Piste pour l'axe X : afficher tous les indices
plt.xticks(range(len(L)))

# Piste pour la clarté : ajouter une ligne horizontale pour la consigne (setpoint)
plt.axhline(y=0, color='r', linestyle='--', label='Setpoint')

plt.xlabel('Itérations')
plt.ylabel('Angle')
plt.title('Convergence du PID')
plt.legend()
plt.grid(True)
plt.show()