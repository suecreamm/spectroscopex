import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from io import BytesIO

def gaussian(x, a, x0, sigma):
    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

def lorentzian(x, a, x0, gamma):
    return a * gamma ** 2 / ((x - x0) ** 2 + gamma ** 2)

def fwhm_gaussian(sigma, scale):
    return 2 * np.sqrt(2 * np.log(2)) * sigma * scale

def fwhm_lorentzian(gamma, scale):
    return 2 * gamma * scale

def fit_and_plot_profiles(explist, exptitles, method='mean', col_nums=2, profile_axis='x', fit_function='gauss', num_xticks=5, num_yticks=5):
    num_dfs = len(explist)
    row_nums = math.ceil(num_dfs / col_nums)
    fit_func = gaussian if fit_function == 'gauss' else lorentzian
    fwhm_func = fwhm_gaussian if fit_function == 'gauss' else fwhm_lorentzian

    fig, axes = plt.subplots(row_nums, col_nums, figsize=(16, row_nums * 5))
    axes = axes.flatten() if num_dfs > 1 else [axes]

    peak_positions = []
    fwhm_values = []

    for i, (df, title) in enumerate(zip(explist, exptitles)):
        ax = axes[i]
        if method == 'mean':
            profile = df.mean(axis=0) if profile_axis == 'x' else df.mean(axis=1)
        elif method == 'median':
            profile = df.median(axis=0) if profile_axis == 'x' else df.median(axis=1)
        else:
            raise ValueError("Method must be 'mean' or 'median'")

        try:
            profile.index = pd.to_numeric(profile.index)
        except Exception as e:
            raise ValueError(f"Profile index must be numeric for fitting. {e}")

        x_data = np.arange(len(profile))
        y_data = profile.values
        scale = profile.index[1] - profile.index[0] if len(profile.index) > 1 else 1

        try:
            popt, _ = curve_fit(fit_func, x_data, y_data, p0=[max(y_data), np.argmax(y_data), 1])
            peak_positions.append(profile.index[int(round(popt[1]))])
            fwhm_value = fwhm_func(popt[2], scale)
            fwhm_values.append(fwhm_value)
        except Exception as e:
            print(f"Fitting failed for {title}: {e}")
            peak_positions.append(None)
            fwhm_values.append(None)
            continue

        ax.scatter(profile.index, y_data, label='Profile', alpha=0.7)
        x0_label = profile.index[int(round(popt[1]))]
        ax.plot(profile.index, fit_func(x_data, *popt), 'r--', label=f'Fit: x0={x0_label:.2f}, FWHM={fwhm_value:.5f}')

        fwhm_start = x0_label - fwhm_value / 2
        fwhm_end = x0_label + fwhm_value / 2

        ax.axvline(x=fwhm_start, color='r', linestyle=':', linewidth=1)
        ax.axvline(x=fwhm_end, color='r', linestyle=':', linewidth=1)

        ax.set_title(f'{title} - {profile_axis.upper()}-profile', fontsize=24)
        ax.set_xlabel('Columns' if profile_axis == 'x' else 'Index')
        ax.set_ylabel('Values')
        ax.legend(fontsize=20)

        # x축 레이블 형식 설정
        if profile_axis == 'x':
            formatted_xticklabels = [f'{x:.1f}' if isinstance(x, (int, float)) else str(x) for x in profile.index]
        else:
            formatted_xticklabels = [f'{x:.6f}' if isinstance(x, (int, float)) else str(x) for x in profile.index]

        x_ticks = np.linspace(0, len(profile.index) - 1, num_xticks, dtype=int)
        ax.set_xticks([profile.index[j] for j in x_ticks])
        ax.set_xticklabels([formatted_xticklabels[j] for j in x_ticks], rotation=90, ha="right", fontsize=18)

        y_ticks = np.linspace(min(y_data), max(y_data), num_yticks)
        ax.set_yticks(y_ticks)
        ax.tick_params(axis='y', labelsize=16)  # y축 폰트 크기 설정

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    plt.close()
    img_bytes.seek(0)

    return peak_positions, fwhm_values, img_bytes

def generate_profile_data(explist, exptitles, profile_axis, method='mean'):
    peak_positions, fwhm_values, img_bytes = fit_and_plot_profiles(
        explist, exptitles, method=method, 
        col_nums=2, profile_axis=profile_axis, fit_function='gauss'
    )
    
    return {
        'image': img_bytes,
        'peak': peak_positions,
        'fwhm': fwhm_values
    }