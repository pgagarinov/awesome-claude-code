import panel as pn
import numpy as np

pn.extension()


def sine_plot(freq, amp, phase):
    """Generate a sine wave plot with the given parameters."""
    x = np.linspace(0, 4 * np.pi, 500)
    y = amp * np.sin(freq * x + phase)

    fig = pn.pane.Matplotlib(tight=True)
    import matplotlib.pyplot as plt

    fig_obj, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y, color="#1f77b4", linewidth=2)
    ax.set_ylim(-5.5, 5.5)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"y = {amp:.1f} sin({freq:.1f}x + {phase:.1f})")
    ax.grid(True, alpha=0.3)
    fig.object = fig_obj
    plt.close(fig_obj)
    return fig


freq_slider = pn.widgets.FloatSlider(name="Frequency", start=0.1, end=5.0, value=1.0, step=0.1)
amp_slider = pn.widgets.FloatSlider(name="Amplitude", start=0.1, end=5.0, value=1.0, step=0.1)
phase_slider = pn.widgets.FloatSlider(name="Phase", start=0.0, end=2 * np.pi, value=0.0, step=0.1)

interactive_plot = pn.bind(sine_plot, freq=freq_slider, amp=amp_slider, phase=phase_slider)

sidebar = pn.Column("## Controls", freq_slider, amp_slider, phase_slider)
main = pn.Column("## Sine Wave Explorer", interactive_plot)

template = pn.template.FastListTemplate(
    title="Panel Sine Wave App",
    sidebar=[sidebar],
    main=[main],
)

template.servable()
