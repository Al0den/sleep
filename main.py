import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.integrate import solve_ivp

class FatigueModel:
    def __init__(self, alpha_w=0.05, alpha_s=0.3, p_f=0, p_max=1.5, sleep_start=0, sleep_end=3, days=7, circadian_amplitude=0.1, circadian_period=24, phase_offset=16, inertia_decay=1.0, inertia_scale=1, initial_fatigue=1):
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
        self.initial_fatigue = initial_fatigue

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
        y0 = [self.initial_fatigue, 0.0] 

        solution = solve_ivp(self.fatigue_derivative, t_span, y0, t_eval=t_eval, method='RK45')

        self.time = solution.t
        self.fatigue = solution.y[0]
        self.inertia = solution.y[1]
        self.circadian_cycle = self.circadian_rhythm(self.time)

    def plot(self):
        ax.clear()
        circadian_ax.clear()
        for day in range(self.days):
            sleep_start_time = day * self.hours_in_day + self.sleep_start
            sleep_end_time = day * self.hours_in_day + self.sleep_end
            if self.sleep_start < self.sleep_end:
                ax.axvspan(sleep_start_time, sleep_end_time, color='gray', alpha=0.3, label='Sleep Period' if day == 0 else "")
            else:  
                ax.axvspan(sleep_start_time, day * self.hours_in_day + self.hours_in_day, color='gray', alpha=0.3, label='Sleep Period' if day == 0 else "")
                ax.axvspan(day * self.hours_in_day, sleep_end_time, color='gray', alpha=0.3)

        ax.plot(self.time, self.fatigue, label='Fatigue Level')
        ax.plot(self.time, self.inertia, label='Sleep Inertia', linestyle='--')
        ax.axhline(self.p_f, color='red', linestyle='--', label='Baseline Fatigue ($p_f$)')
        ax.axhline(self.p_max, color='blue', linestyle='--', label='Max Fatigue ($p_{max}$)')
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Fatigue/Inertia Level')
        ax.set_title('Fatigue Levels Over 7 Days with Circadian Rhythm and Sleep Inertia')
      
        ax.grid()

        circadian_ax.plot(self.time, self.circadian_cycle, label='Circadian Cycle', color='purple')
        circadian_ax.set_xlabel('Time (hours)')
        circadian_ax.set_ylabel('Circadian Rhythm')
        circadian_ax.set_title('Circadian Cycle')
        circadian_ax.grid()

        fig.canvas.draw_idle()

# Interactive Slider Functionality
def update(val):
    model.alpha_w = s_alpha_w.val
    model.alpha_s = s_alpha_s.val
    model.sleep_start = s_sleep_start.val
    model.sleep_end = s_sleep_end.val
    model.circadian_amplitude = s_circadian_amplitude.val
    model.circadian_period = s_circadian_period.val
    model.phase_offset = s_phase_offset.val
    model.inertia_decay = s_inertia_decay.val
    model.inertia_scale = s_inertia_scale.val
    model.initial_fatigue = s_initial_fatigue.val
    model.simulate()
    model.plot()

if __name__ == "__main__":
    model = FatigueModel(sleep_start=0, sleep_end=4)
    model.simulate()

    fig, (ax, circadian_ax) = plt.subplots(1, 2, figsize=(16, 5))
    plt.subplots_adjust(left=0.1, bottom=0.6)
    model.plot()

    # Define sliders
    ax_alpha_w = plt.axes([0.25, 0.45, 0.65, 0.03])
    ax_alpha_s = plt.axes([0.25, 0.40, 0.65, 0.03])
    ax_sleep_start = plt.axes([0.25, 0.35, 0.65, 0.03])
    ax_sleep_end = plt.axes([0.25, 0.30, 0.65, 0.03])
    ax_circadian_amplitude = plt.axes([0.25, 0.25, 0.65, 0.03])
    ax_circadian_period = plt.axes([0.25, 0.20, 0.65, 0.03])
    ax_phase_offset = plt.axes([0.25, 0.15, 0.65, 0.03])
    ax_inertia_decay = plt.axes([0.25, 0.1, 0.65, 0.03])
    ax_inertia_scale = plt.axes([0.25, 0.05, 0.65, 0.03])
    ax_initial_fatigue = plt.axes([0.25, 0.0, 0.65, 0.03])

    s_alpha_w = Slider(ax_alpha_w, 'Alpha W', 0.01, 0.2, valinit=model.alpha_w)
    s_alpha_s = Slider(ax_alpha_s, 'Alpha S', 0.1, 0.5, valinit=model.alpha_s)
    s_sleep_start = Slider(ax_sleep_start, 'Sleep Start', 0, 23, valinit=model.sleep_start)
    s_sleep_end = Slider(ax_sleep_end, 'Sleep End', 0, 23, valinit=model.sleep_end)
    s_circadian_amplitude = Slider(ax_circadian_amplitude, 'Circadian Amp', 0.05, 0.5, valinit=model.circadian_amplitude)
    s_circadian_period = Slider(ax_circadian_period, 'Circadian Period', 20, 30, valinit=model.circadian_period)
    s_phase_offset = Slider(ax_phase_offset, 'Phase Offset', 0, 24, valinit=model.phase_offset)
    s_inertia_decay = Slider(ax_inertia_decay, 'Inertia Decay', 0.5, 2.0, valinit=model.inertia_decay)
    s_inertia_scale = Slider(ax_inertia_scale, 'Inertia Scale', 0.5, 2.0, valinit=model.inertia_scale)
    s_initial_fatigue = Slider(ax_initial_fatigue, 'Initial Fatigue', 0, 2, valinit=model.initial_fatigue)

    # Connect sliders to update function
    s_alpha_w.on_changed(update)
    s_alpha_s.on_changed(update)
    s_sleep_start.on_changed(update)
    s_sleep_end.on_changed(update)
    s_circadian_amplitude.on_changed(update)
    s_circadian_period.on_changed(update)
    s_phase_offset.on_changed(update)
    s_inertia_decay.on_changed(update)
    s_inertia_scale.on_changed(update)
    s_initial_fatigue.on_changed(update)

    plt.show()
