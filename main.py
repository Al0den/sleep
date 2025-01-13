import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class FatigueModel:
    def __init__(self, alpha_w=0.05, alpha_s=0.2, p_f=0, p_max=1.5, sleep_start=0, sleep_end=3, days=7, circadian_amplitude=0.1, circadian_period=24, phase_offset=16, inertia_decay=1.0, inertia_scale=1):
        self.alpha_w = alpha_w  
        self.alpha_s = alpha_s  
        self.p_f = p_f          
        self.p_max = p_max      
        self.sleep_start = sleep_start 
        self.sleep_end = sleep_end      
        self.days = days
        self.hours_in_day = 24
        self.total_hours = self.hours_in_day * self.days

        self.circadian_amplitude = circadian_amplitude
        self.circadian_period = circadian_period
        self.phase_offset = phase_offset

        self.inertia_decay = inertia_decay
        self.inertia_scale = inertia_scale

    def circadian_rhythm(self, t):
        return self.circadian_amplitude * np.sin(2 * np.pi * (t - self.phase_offset) / self.circadian_period)

    def fatigue_derivative(self, t, y):
        p, h = y  
        current_hour = t % self.hours_in_day  

        circadian_effect = self.circadian_rhythm(t)

        if self.sleep_start <= current_hour < self.sleep_end or (self.sleep_end < self.sleep_start and (current_hour < self.sleep_end or current_hour >= self.sleep_start)):
            dp_dt = -self.alpha_s * (p - self.p_f) + circadian_effect + self.inertia_scale * h
            dh_dt = -self.inertia_decay * (h - 0.1 * (p - self.p_f))
        else:  
            dp_dt = +self.alpha_w * (self.p_max - p) + circadian_effect + self.inertia_scale * h
            dh_dt = -self.inertia_decay * h

        return [dp_dt, dh_dt]

    def simulate(self):
        t_span = (0, self.total_hours)
        t_eval = np.linspace(0, self.total_hours, int(self.total_hours * 10))  
        y0 = [0.5, 0.0] 

        solution = solve_ivp(self.fatigue_derivative, t_span, y0, t_eval=t_eval, method='RK45')

        self.time = solution.t
        self.fatigue = solution.y[0]
        self.inertia = solution.y[1]

    def plot(self):
        plt.figure(figsize=(10, 6))


        for day in range(self.days):
            sleep_start_time = day * self.hours_in_day + self.sleep_start
            sleep_end_time = day * self.hours_in_day + self.sleep_end
            if self.sleep_start < self.sleep_end:
                plt.axvspan(sleep_start_time, sleep_end_time, color='gray', alpha=0.3, label='Sleep Period' if day == 0 else "")
            else:  
                plt.axvspan(sleep_start_time, day * self.hours_in_day + self.hours_in_day, color='gray', alpha=0.3, label='Sleep Period' if day == 0 else "")
                plt.axvspan(day * self.hours_in_day, sleep_end_time, color='gray', alpha=0.3)

        plt.plot(self.time, self.fatigue, label='Fatigue Level')
        plt.plot(self.time, self.inertia, label='Sleep Inertia', linestyle='--')
        plt.axhline(self.p_f, color='red', linestyle='--', label='Baseline Fatigue ($p_f$)')
        plt.axhline(self.p_max, color='blue', linestyle='--', label='Max Fatigue ($p_{max}$)')
        plt.xlabel('Time (hours)')
        plt.ylabel('Fatigue/Inertia Level')
        plt.title('Fatigue Levels Over 7 Days with Circadian Rhythm and Sleep Inertia')
        plt.legend()
        plt.grid()
        plt.show()

if __name__ == "__main__":
    model = FatigueModel(sleep_start=0, sleep_end=4) 
    model.simulate()
    model.plot()
