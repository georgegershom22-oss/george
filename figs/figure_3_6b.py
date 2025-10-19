"""
Figure 3.6B — Time–frequency TL fluctuation intensity
Left: high Ri (narrow conversion band). Right: marginal Ri (intermittent, broadband bursts).
"""

import numpy as np
import matplotlib.pyplot as plt
from house_style import *

def generate_tl_fluctuation_data(high_ri=True, time_range=(0, 60), n_time=200, n_freq=100):
    """Generate TL fluctuation intensity data for scalograms"""
    time = np.linspace(time_range[0], time_range[1], n_time)
    omega_n = np.linspace(OMEGA_N_RANGE[0], OMEGA_N_RANGE[1], n_freq)
    T, OmegaN = np.meshgrid(time, omega_n, indexing='ij')
    
    if high_ri:
        # High Ri: narrow conversion band, nearly time-steady
        # Create a thin horizontal ridge in the conversion band
        center_freq = 1.0
        freq_width = 0.1
        base_intensity = 0.1
        
        # Main ridge in conversion band
        ridge = np.exp(-((OmegaN - center_freq) / freq_width)**2)
        
        # Add slight waviness to the ridge
        time_modulation = 1 + 0.1 * np.sin(2 * np.pi * T / 20) * np.exp(-((OmegaN - center_freq) / (2 * freq_width))**2)
        
        # Add some background noise
        noise = 0.05 * np.random.randn(*T.shape)
        
        intensity = ridge * time_modulation + base_intensity + noise
        
    else:
        # Marginal Ri: intermittent broadband bursts
        base_intensity = 0.05
        
        # Persistent but less coherent band near ω/N ≈ 1
        persistent_band = 0.3 * np.exp(-((OmegaN - 1.0) / 0.3)**2)
        
        # Intermittent bursts - create several burst events
        n_bursts = 8
        burst_times = np.random.uniform(time_range[0], time_range[1], n_bursts)
        burst_durations = np.random.uniform(3, 8, n_bursts)
        burst_freq_spreads = np.random.uniform(0.2, 0.6, n_bursts)
        
        intermittent = np.zeros_like(T)
        for i in range(n_bursts):
            # Time envelope for this burst
            time_envelope = np.exp(-((T - burst_times[i]) / burst_durations[i])**2)
            
            # Frequency spread (broader than conversion band)
            freq_center = np.random.uniform(0.7, 1.3)
            freq_envelope = np.exp(-((OmegaN - freq_center) / burst_freq_spreads[i])**2)
            
            # Add some oblique streaks (intrusions)
            if np.random.random() > 0.5:
                # Create oblique pattern
                slope = np.random.uniform(-0.01, 0.01)
                oblique_factor = np.exp(-((OmegaN - (freq_center + slope * (T - burst_times[i]))) / (burst_freq_spreads[i] * 0.7))**2)
                freq_envelope = np.maximum(freq_envelope, 0.5 * oblique_factor)
            
            intermittent += time_envelope * freq_envelope
        
        # Add some random noise
        noise = 0.1 * np.random.randn(*T.shape)
        
        intensity = base_intensity + persistent_band + intermittent + noise
    
    # Ensure non-negative and clip to reasonable range
    intensity = np.clip(intensity, 0, 1)
    
    return time, omega_n, intensity

def create_figure_3_6b():
    """Create Figure 3.6B - Time-frequency TL fluctuation intensity (two panels)"""
    # Generate data for both panels
    time_high, omega_n, intensity_high = generate_tl_fluctuation_data(high_ri=True)
    time_marg, omega_n, intensity_marg = generate_tl_fluctuation_data(high_ri=False)
    
    # Create figure with two panels
    fig = create_figure()
    
    # Left panel (high Ri)
    ax_left = fig.add_subplot(121)
    colormap = get_heatmap_colormap()
    im_left = ax_left.imshow(intensity_high.T, 
                            extent=[time_high[0], time_high[-1], 
                                   OMEGA_N_RANGE[0], OMEGA_N_RANGE[1]], 
                            aspect='auto', origin='lower', cmap=colormap,
                            interpolation='bilinear')
    
    # Setup axes for left panel
    ax_left.set_xlim(0, 60)
    ax_left.set_xticks(np.arange(0, 61, 10))
    ax_left.set_xlabel('t (s)', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    setup_omega_n_axis(ax_left, xlabel=False)
    ax_left.set_ylabel('ω/N', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    
    # Add conversion window to left panel
    add_conversion_window(ax_left, y_range=OMEGA_N_RANGE)
    
    # Add annotation for left panel
    add_arrow_annotation(ax_left, 'narrow conversion-band modulation', 
                        xy=(30, 1.0), xytext=(30, 1.5), 
                        arrowprops=dict(arrowstyle='->', color='white', lw=2))
    
    # Add caption for left panel
    add_caption(ax_left, 'High Ri: fluctuation energy concentrated in a narrow conversion band.',
                position='bottom')
    
    # Right panel (marginal Ri)
    ax_right = fig.add_subplot(122)
    im_right = ax_right.imshow(intensity_marg.T, 
                              extent=[time_marg[0], time_marg[-1], 
                                     OMEGA_N_RANGE[0], OMEGA_N_RANGE[1]], 
                              aspect='auto', origin='lower', cmap=colormap,
                              interpolation='bilinear')
    
    # Setup axes for right panel
    ax_right.set_xlim(0, 60)
    ax_right.set_xticks(np.arange(0, 61, 10))
    ax_right.set_xlabel('t (s)', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    setup_omega_n_axis(ax_right, xlabel=False)
    ax_right.set_ylabel('ω/N', fontsize=AXIS_LABEL_SIZE, fontweight='normal')
    
    # Add conversion window to right panel
    add_conversion_window(ax_right, y_range=OMEGA_N_RANGE)
    
    # Add annotations for right panel
    add_arrow_annotation(ax_right, 'intermittent broadband bursts', 
                        xy=(25, 1.3), xytext=(25, 1.8), 
                        arrowprops=dict(arrowstyle='->', color='white', lw=2))
    add_arrow_annotation(ax_right, 'enhanced spread beyond conversion', 
                        xy=(45, 0.6), xytext=(45, 0.2), 
                        arrowprops=dict(arrowstyle='->', color='white', lw=2))
    
    # Add caption for right panel
    add_caption(ax_right, 'Marginal Ri: intermittent broadband activity indicates shear-mediated variability.',
                position='bottom')
    
    # Add shared colorbar on the right
    add_colorbar(fig, ax_right, im_right, 'TL fluctuation intensity (arb.)')
    
    # Adjust layout to add 40px gutter between panels
    plt.subplots_adjust(wspace=0.15)
    
    return fig

if __name__ == '__main__':
    fig = create_figure_3_6b()
    save_figure(fig, 'figure_3_6b')
    plt.show()