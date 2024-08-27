import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from io import BytesIO
import base64

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

    plt.tight_layout()
    
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
