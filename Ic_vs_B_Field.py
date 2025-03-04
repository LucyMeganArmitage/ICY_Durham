import matplotlib.pyplot as plt
import numpy as np
import os
from numpy.polynomial import Polynomial
from scipy.optimize import curve_fit
from matplotlib import cm

path = "C:/Users/lucym/OneDrive/Documents/Durham_Labs"
all_files = [os.path.join(path, file).replace("\\", "/") for file in os.listdir(path) if file.startswith("real_deal") and file.endswith('.txt')]

# Function to parse field strength and angle from filenames
def parse_file_info(filename):
    # Extract field strength and angle from the filename
    base_name = os.path.basename(filename)
    parts = base_name.split('_')
    field_strength = float(parts[2].replace("point", "."))
    angle = int(parts[3].replace("deg.txt", ""))
    return field_strength, angle

def power_law(I, *params):
    """
    This function defines the power law that the data will fit to. In our case this is E = E_c * (I/I_c)^n.
    Parameters are I_c (critical current) and n. E_c is set to the critical electric field criterion. 
    """
    Ec = 100  # Electric field criterion (100 μV/cm)
    Ic, N = params
    I = np.abs(I) + 1e-9
    return Ec * (I / Ic)**N

def curve_fitting(xdata, ydata):
    """
    This function completes curve fitting using the power law. 
     
     returns:
    --------
    - I_c - critical current
    - n - exponent of (I/I_c)^n
    - popt - all parameters from scipy.optimize.curve_fit 
    """

    try:
        popt, pcov = curve_fit(power_law, xdata, ydata, p0=[xdata.mean(), 10]) # can add maxfev=5000
    except RuntimeError as e:
        print('Fit did not converge:', e)
        return np.nan, np.nan, [np.nan, np.nan]
    # Print Parameters
    for i in range(len(popt)):
        print(f'Parameter {i}: {popt[i]:.5f}) ± {np.sqrt(pcov[i][i]):.5f}')

    Ic = popt[0]
    N = popt[1]

    return Ic, N, popt

# Function to load and plot data
def load_and_plot_files(files, filter_angle=None, filter_field=None):
    plt.figure(figsize=(10, 6))
    angle_dict ={}

    for i, file in enumerate(files):
        try:
            # Parse field strength and angle
            field_strength, angle = parse_file_info(file)
            
            # Skip files if they don't match the filters
            if (filter_angle is not None and angle != filter_angle) or (filter_field is not None and field_strength != filter_field):
                continue
            
            # Load data from the file
            data = np.loadtxt(file, dtype=float, skiprows=11, usecols=(0, 1))
            xdata, ydata = data[:, 0], data[:, 1]
            critical_current_estimate = xdata[len(xdata)//2]

            mask = xdata < critical_current_estimate
            x_background = xdata[mask]
            y_background = ydata[mask]

            background_fit = Polynomial.fit(x_background, y_background, deg=1)

            # Subtract the linear fit and divide by voltage tap distance 
            y_fit_background = background_fit(xdata)
            y_corrected = (ydata - y_fit_background)/(12.89/1000)

            x_extended = np.linspace(xdata.min(), xdata.max(), 500)
            Ic, N, popt = curve_fitting(xdata, y_corrected)
            y_fit = power_law(x_extended, *popt)

            if angle not in angle_dict:
                angle_dict[angle] = {"field_strengths": [], "critical_currents": []}
            angle_dict[angle]["field_strengths"].append(field_strength)
            angle_dict[angle]["critical_currents"].append(Ic)

            #plt.plot(xdata, ydata, label='Field strength = {0:.2f}'.format(field_strength), color="blue")
            #plt.plot(xdata, y_fit_background, label="Background Fit", color="black", linestyle="--")
            
            #plt.scatter(field_strength, Ic, label='{0:.2f}deg'.format(angle), color='cyan')
            #plt.axhline(y=100, color='black', linestyle='--')
            #plt.axvline(x=Ic, color='black', linestyle='-')
            #plt.plot(x_extended, y_fit, color='black')
        
        except Exception as e:
            print(f"Could not process file {file}: {e}")
                # Plot the data

    # Plot data for each angle
    cmap = cm.get_cmap('YlOrRd', len(angle_dict))  # Replace 'viridis' with 'abbott' if you have it available
    colors = [cmap(i / len(angle_dict)) for i in range(len(angle_dict))]

    zero_deg_index = list(angle_dict.keys()).index(0)  # Assuming 0 degrees exists in angle_dict
    colors[zero_deg_index] = (1.0, 0.94, 0.67, 1.0)  # Custom yellow shade (RGBA format)

    sorted_angle_dict = dict(sorted(angle_dict.items()))

    for i, (angle, data) in enumerate(sorted_angle_dict.items()):
        field_strengths = np.array(data["field_strengths"])
        critical_currents = np.array(data["critical_currents"])

        # Sort the data by field strength
        sorted_indices = np.argsort(field_strengths)
        field_strengths = field_strengths[sorted_indices]
        critical_currents = critical_currents[sorted_indices]

        # Plot
        plt.plot(
            field_strengths,
            critical_currents,
            label=f"{angle}°",
            marker="o",
            linestyle="-", 
            color=colors[i], linewidth=3
        )
    plt.xlabel("Magnetic Field Strength [T]", fontsize = 14)
    plt.ylabel("Critical Current [A]", fontsize = 14)
    plt.legend(title="Angle of Applied Field", fontsize=14, title_fontsize=14)
    plt.tick_params(axis='both', which='major', labelsize=14)
    #plt.title("Voltage vs Current with Background Subtraction ")
    plt.grid()
    plt.show()
  
# Example usage:
# Plot all files with angle 90 degrees
#load_and_plot_files(all_files, filter_angle=40)

# # Plot all files with field strength 0.6
#load_and_plot_files(all_files, filter_field=0.6)

# # Plot all files without any filtering
load_and_plot_files(all_files)



  
#For just one file:
# file1 = 'real_deal_0point6_40deg.txt'

# xdata = np.loadtxt(file1, dtype=float, skiprows=11, usecols=0)
# ydata = np.loadtxt(file1, dtype=float, skiprows=11, usecols=1)

# print(xdata)

# #"C:\Users\lucym\OneDrive\Documents\Durham_Labs\real_deal_0point6_40deg.txt"
# # Plot a figure with error bars
# plt.figure()
# plt.plot(xdata, ydata)
# plt.xlabel("Current / A")
# plt.ylabel(f"Micro-Voltage / $\\mu V$")
# plt.show()