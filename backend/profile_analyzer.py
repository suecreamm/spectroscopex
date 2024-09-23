import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.font_manager as fm
import math
from scipy.optimize import curve_fit
from io import BytesIO
import base64
from plotter import angle_to_q, process_q_values

plt.switch_backend('Agg')

def gaussian(x, a, x0, sigma):
    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

def lorentzian(x, a, x0, gamma):
    return a * gamma ** 2 / ((x - x0) ** 2 + gamma ** 2)

def fwhm_gaussian(sigma, scale):
    return 2 * np.sqrt(2 * np.log(2)) * sigma * scale

def fwhm_lorentzian(gamma, scale):
    return 2 * gamma * scale


def fit_and_plot_profiles(explist, exptitles, method='mean', col_nums=2, profile_axis='x', fit_function='gauss', num_xticks=5, num_yticks=5):
    def process_index(profile):
        try:
            if isinstance(profile.index, pd.RangeIndex):
                return profile  # RangeIndex는 이미 숫자형이므로 처리 불필요
            str_index = profile.index.astype(str)
            numeric_part = str_index.str.extract('(\d+\.?\d*)')[0]
            numeric_index = pd.to_numeric(numeric_part, errors='coerce')
            if numeric_index.isna().any():
                print(f"Warning: Some index values couldn't be converted to numeric")
                profile = profile[~numeric_index.isna()]
                numeric_index = numeric_index.dropna()
            profile.index = numeric_index
            return profile
        except Exception as e:
            print(f"Error processing index: {str(e)}")
            return profile

    num_dfs = len(explist)
    row_nums = math.ceil(num_dfs / col_nums)
    fit_func = gaussian if fit_function == 'gauss' else lorentzian
    fwhm_func = fwhm_gaussian if fit_function == 'gauss' else fwhm_lorentzian

    fig, axes = plt.subplots(row_nums, col_nums, figsize=(16, row_nums * 5))
    
    # Flatten axes array only if it's an ndarray
    if isinstance(axes, np.ndarray):
        axes = axes.flatten()
    else:
        axes = [axes]  # If it's not an array, ensure it's a list

    peak_positions = []
    fwhm_values = []

    for i, (df, title) in enumerate(zip(explist, exptitles)):
        ax = axes[i]
        if profile_axis == 'x':
            if method == 'mean':
                profile = df.mean(axis=0)
            elif method == 'median':
                profile = df.median(axis=0)
            else:
                raise ValueError("Method must be 'mean' or 'median'")
            profile = process_index(profile)
            x_label = 'Columns'
            y_label = 'Intensity'
        else:  # y-profile
            if method == 'mean':
                profile = df.mean(axis=1)
            elif method == 'median':
                profile = df.median(axis=1)
            else:
                raise ValueError("Method must be 'mean' or 'median'")
            profile = process_index(profile)
            x_label = 'Rows'
            y_label = 'Intensity'

        try:
            x_data = np.arange(len(profile))
            y_data = profile.values
            
            # NaN 값 제거
            valid_mask = ~np.isnan(y_data)
            x_data = x_data[valid_mask]
            y_data = y_data[valid_mask]

            if len(x_data) < 3:
                raise ValueError("Not enough valid data points for fitting")

            scale = profile.index[1] - profile.index[0] if len(profile.index) > 1 else 1

            max_index = np.argmax(y_data)
            max_value = y_data[max_index]

            initial_guess = [max_value, max_index, len(y_data) / 10 if fit_function == 'gauss' else len(y_data) / 20]

            popt, _ = curve_fit(fit_func, x_data, y_data, p0=initial_guess)

            if np.any(np.isnan(popt)) or np.any(np.isinf(popt)):
                raise ValueError("Invalid fitting results")

            x0_index = int(round(popt[1]))
            if 0 <= x0_index < len(profile.index):
                x0 = profile.index[x0_index]
            else:
                raise ValueError("x0 index out of bounds")

            peak_positions.append(x0)
            fwhm_value = fwhm_func(popt[2], scale)
            fwhm_values.append(fwhm_value)

            ax.plot(profile.index, fit_func(x_data, *popt), 'r--', label=f'Fit: x0={x0:.2f}, FWHM={fwhm_value:.5f}')

            fwhm_start = x0 - fwhm_value / 2
            fwhm_end = x0 + fwhm_value / 2

            ax.axvline(x=fwhm_start, color='r', linestyle=':', linewidth=1)
            ax.axvline(x=fwhm_end, color='r', linestyle=':', linewidth=1)

        except Exception as e:
            print(f"Error in fitting for {title}: {str(e)}")
            peak_positions.append(None)
            fwhm_values.append(None)
        
        ax.scatter(profile.index, y_data, label='Profile', alpha=0.7)
        ax.set_title(f'{title} - {profile_axis.upper()}-profile', fontsize=24)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.legend(fontsize=20)

        formatted_xticklabels = [f'{x:.1f}' if isinstance(x, (int, float)) else str(x) for x in profile.index]
        x_ticks = np.linspace(0, len(profile.index) - 1, num_xticks, dtype=int)
        ax.set_xticks([profile.index[j] for j in x_ticks])
        ax.set_xticklabels([formatted_xticklabels[j] for j in x_ticks], rotation=90, ha="right", fontsize=18)

        y_ticks = np.linspace(min(y_data), max(y_data), num_yticks)
        ax.set_yticks(y_ticks)
        ax.tick_params(axis='y', labelsize=16)

    # Remove unused axes if any
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    #plt.tight_layout()
    
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    plt.close()
    img_bytes.seek(0)

    return peak_positions, fwhm_values, img_bytes



def generate_profile_data(explist, exptitles, profile_axis, method='mean'):
    try:
        peak_positions, fwhm_values, img_bytes = fit_and_plot_profiles(
            explist, exptitles, method=method, 
            col_nums=2, profile_axis=profile_axis, fit_function='gauss'
        )

        response_data = {
            'image': img_bytes,
            'peak': [None if pd.isna(pos) else pos for pos in peak_positions],
            'fwhm': [None if pd.isna(fwhm) else fwhm for fwhm in fwhm_values]
        }

        return response_data
    except Exception as e:
        raise


def plot_intensity_profiles_with_heatmap(explist, exptitles, gauss_y=None, value=75, window_size=0, plot='x',
                                         aggregation='mean', x_min=None, x_max=None, y_min=None, y_max=None,
                                         figsize=(5, 5), title_fontsize=16, label_fontsize=12, tick_fontsize=10,
                                         cmap='inferno', font_family='sans-serif', font_style='normal', font_weight='normal',
                                         apply_log=True, q_conversion=False, x_label=None, 
                                         width_ratio=(3.5, 1), vertical=True, hide_ticks=True, lgnd=False):
    """
    Plot intensity profiles and heatmaps for multiple experiments.
    """
    font_prop = fm.FontProperties(family=font_family, style=font_style, weight=font_weight)
    
    num_exp = len(explist)
    fig, axs = plt.subplots(num_exp, 2, figsize=(figsize[0], figsize[1] * num_exp), 
                            gridspec_kw={'width_ratios': width_ratio})
    
    if num_exp == 1:
        axs = axs.reshape(1, -1)

    def filter_dataframe_by_range(df, x_min, x_max, y_min, y_max):
        columns_as_float = df.columns.astype(float)
        index_as_float = df.index.astype(float)
        
        x_mask = pd.Series(True, index=columns_as_float)
        y_mask = pd.Series(True, index=index_as_float)
        
        if x_min is not None:
            x_mask &= columns_as_float >= x_min
        if x_max is not None:
            x_mask &= columns_as_float <= x_max
        if y_min is not None:
            y_mask &= index_as_float >= y_min
        if y_max is not None:
            y_mask &= index_as_float <= y_max
        
        filtered_df = df.loc[y_mask, x_mask]
        return filtered_df

    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    for idx, (df, title) in enumerate(zip(explist, exptitles)):
        ax1, ax2 = axs[idx]

        # Filter the dataframe based on provided x_min, x_max, y_min, y_max
        df = filter_dataframe_by_range(df, x_min, x_max, y_min, y_max)

        Z = df.values
        if Z.size == 0:
            print(f"Warning: No data in the specified range for {title}")
            continue

        if apply_log and np.issubdtype(Z.dtype, np.number):
            Z = np.log1p(Z)

        columns = df.columns.astype(float)
        energy_losses = df.index.astype(float)

        if q_conversion and gauss_y is not None:
            E0 = gauss_y[idx]
            angles = columns * np.pi / 180
            q_values = np.array([angle_to_q(angle, E0, 0) for angle in angles])
            processed_q_values = process_q_values(q_values)
        else:
            processed_q_values = columns

        extent = [np.min(processed_q_values), np.max(processed_q_values),
                  np.min(energy_losses), np.max(energy_losses)]

        # Plot heatmap
        im = ax1.imshow(Z, aspect='auto', origin='lower', extent=extent, cmap=cmap)

        ax1.set_title(f"{title}, E0 = {E0:.6f} eV" if q_conversion and gauss_y is not None else title, 
                      fontsize=title_fontsize, fontproperties=font_prop)

        if x_label is not None:
            ax1.set_xlabel(x_label, fontsize=label_fontsize, fontproperties=font_prop)
        else:
            ax1.set_xlabel('q (Å⁻¹)' if q_conversion and gauss_y is not None else 'Angle (degree)', 
                           fontsize=label_fontsize, fontproperties=font_prop)

        ax1.set_ylabel('Loss Energy (eV)', fontsize=label_fontsize, fontproperties=font_prop)

        for label in ax1.get_xticklabels() + ax1.get_yticklabels():
            label.set_fontproperties(font_prop)

        ax1.tick_params(axis='both', which='major', labelsize=tick_fontsize)

        # Plot intensity profile
        if plot == 'x':
            nearest_value = find_nearest(processed_q_values, value)
            window_start = nearest_value - window_size / 2
            window_end = nearest_value + window_size / 2
            window_cols = processed_q_values[(processed_q_values >= window_start) & (processed_q_values <= window_end)]
            
            if window_size > 0:
                if aggregation == 'mean':
                    intensity_values = df.loc[:, window_cols].mean(axis=1)
                elif aggregation == 'median':
                    intensity_values = df.loc[:, window_cols].median(axis=1)
                else:
                    raise ValueError("Invalid aggregation method. Use 'mean' or 'median'.")
            else:
                intensity_values = df.loc[:, nearest_value]

            y_values = energy_losses
            if vertical:
                ax2.plot(intensity_values, y_values, label=f"{title}")
                ax2.set_xlabel("Intensity\n(Arb. Units)")
                ax2.set_ylabel("Loss Energy (eV)")
            else:
                ax2.plot(y_values, intensity_values, label=f"{title}")
                ax2.set_xlabel("Loss Energy (eV)")
                ax2.set_ylabel("Intensity\n(Arb. Units)")
            
            if window_size > 0:
                ax1.axvspan(window_start, window_end, color='y', alpha=0.2)
            print(f"Using x_value: {nearest_value} with window size: {window_size} for {title}")
            
        elif plot == 'y':
            nearest_value = find_nearest(energy_losses, value)
            window_start = nearest_value - window_size / 2
            window_end = nearest_value + window_size / 2
            window_rows = energy_losses[(energy_losses >= window_start) & (energy_losses <= window_end)]
            
            if window_size > 0:
                if aggregation == 'mean':
                    intensity_values = df.loc[window_rows, :].mean(axis=0)
                elif aggregation == 'median':
                    intensity_values = df.loc[window_rows, :].median(axis=0)
                else:
                    raise ValueError("Invalid aggregation method. Use 'mean' or 'median'.")
            else:
                intensity_values = df.loc[nearest_value, :]

            x_values = processed_q_values
            if vertical:
                ax2.plot(intensity_values, x_values, label=f"{title}")
                ax2.set_xlabel("Intensity (Arb. Units)")
                ax2.set_ylabel('q (Å⁻¹)' if q_conversion and gauss_y is not None else 'Angle (degree)')
            else:
                ax2.plot(x_values, intensity_values, label=f"{title}")
                ax2.set_xlabel('q (Å⁻¹)' if q_conversion and gauss_y is not None else 'Angle (degree)')
                ax2.set_ylabel("Intensity (Arb. Units)")
            
            if window_size > 0:
                ax1.axhspan(window_start, window_end, color='y', alpha=0.2)
            print(f"Using y_value: {nearest_value} with window size: {window_size} for {title}")

        ax2.set_title(f'{title} Intensity Profile', fontsize=title_fontsize, fontproperties=font_prop)
        ax2.tick_params(axis='both', which='major', labelsize=tick_fontsize)
        for label in ax2.get_xticklabels() + ax2.get_yticklabels():
            label.set_fontproperties(font_prop)

        if vertical and hide_ticks:
            ax2.set_xticks([])
            ax2.set_yticks([])

        if lgnd:
            ax2.legend()

        ax2.grid(False)

    plt.tight_layout()
    
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png', bbox_inches='tight')
    img_bytes.seek(0)
    plt.close(fig)
    
    return img_bytes