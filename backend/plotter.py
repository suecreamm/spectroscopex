import numpy as np
import matplotlib.font_manager as fm 
import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from io import BytesIO
import logging

plt.switch_backend('Agg')

# Gaussian and Lorentzian functions
def gaussian(x, a, x0, sigma):
    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

def lorentzian(x, a, x0, gamma):
    return a * gamma ** 2 / ((x - x0) ** 2 + gamma ** 2)

# Convert to float with error handling
def convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        return value


def create_plot(explist, exptitles, save2D=True, num_xticks=5, num_yticks=5, num_cols=2, apply_log=True):
    num_subplots = len(explist)
    num_rows = (num_subplots + num_cols - 1) // num_cols

    subplot_width = 4
    subplot_height = 5.4

    fig_width = subplot_width * num_cols
    fig_height = subplot_height * num_rows

    fig, axs = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height))

    if isinstance(axs, np.ndarray):
        axs = axs.flatten()
    else:
        axs = [axs]

    plt.subplots_adjust(hspace=0, wspace=0)
    im = None

    # 디버깅: 데이터가 유효한지 확인
    for i, (df, title) in enumerate(zip(explist, exptitles)):
        logging.debug(f"Creating plot for {title} with data shape: {df.shape}")

        if df.empty:
            logging.warning(f"DataFrame for {title} is empty, skipping plot.")
            continue

        Z = df.values
        
        if apply_log and np.issubdtype(Z.dtype, np.number):
            Z = np.log1p(Z)
        
        x = df.columns.astype(float)
        y = df.index.astype(float)

        ax = axs[i]
        im = ax.imshow(Z, aspect='auto', origin='lower', extent=[x.min(), x.max(), y.min(), y.max()], cmap='inferno')
        ax.set_title(title, fontsize=20)

        if i % num_cols == 0:
            ax.set_ylabel('Energy (eV)', fontsize=14)
        else:
            ax.set_yticklabels([])

        if i >= (num_rows - 1) * num_cols:
            ax.set_xlabel('Angle (degree)', fontsize=14)
        else:
            ax.set_xticklabels([])

    if im is not None:
        cbar_ax = fig.add_axes([0.92, 0.063, 0.02, 0.15])
        fig.colorbar(im, cax=cbar_ax, orientation='vertical')

    plt.tight_layout(rect=[0, 0, 0.9, 1])

    img_bytes = BytesIO()
    
    try:
        plt.savefig(img_bytes, format='png', bbox_inches='tight')
        logging.debug("Image saved successfully.")
    except Exception as e:
        logging.error(f"Error saving image: {str(e)}")
        raise
    finally:
        plt.close()

    img_bytes.seek(0)

    return img_bytes


def plot_x_profiles(explist, exptitles, method='mean', col_nums=4, plot=False):
    num_dfs = len(explist)
    row_nums = math.ceil(num_dfs / col_nums)

    gauss_peak_x = []
    lorentz_peak_x = []

    if plot:
        fig, axes = plt.subplots(row_nums, col_nums, figsize=(20, row_nums * 5))
        axes = axes.flatten() if num_dfs > 1 else [axes]

    for i, (df, title) in enumerate(zip(explist, exptitles)):
        if method == 'mean':
            profile = df.mean(axis=0)
        elif method == 'median':
            profile = df.median(axis=0)
        else:
            raise ValueError("Method must be 'mean' or 'median'")

        x_data = np.arange(len(profile))
        y_data = profile.values

        popt_gauss, _ = curve_fit(gaussian, x_data, y_data, p0=[max(y_data), np.argmax(y_data), 1])
        popt_lorentz, _ = curve_fit(lorentzian, x_data, y_data, p0=[max(y_data), np.argmax(y_data), 1])

        gauss_peak_x.append(profile.index[int(round(popt_gauss[1]))])
        lorentz_peak_x.append(profile.index[int(round(popt_lorentz[1]))])

        if plot:
            ax = axes[i]
            ax.plot(profile.index, y_data, label='Profile')
            ax.plot(profile.index, gaussian(x_data, *popt_gauss), 'r--', label=f'Gaussian Fit: a={popt_gauss[0]:.2f}, x0={popt_gauss[1]:.2f}, sigma={popt_gauss[2]:.2f}')
            ax.plot(profile.index, lorentzian(x_data, *popt_lorentz), 'g--', label=f'Lorentzian Fit: a={popt_lorentz[0]:.2f}, x0={popt_lorentz[1]:.2f}, gamma={popt_lorentz[2]:.2f}')
            ax.set_title(f'{title} - X-profile')
            ax.set_xlabel('Columns')
            ax.set_ylabel('Values')
            ax.legend()

            # x축 레이블 간격 설정 (5개의 레이블만 표시)
            max_xticks = 5
            x_ticks = np.linspace(0, len(profile.index) - 1, max_xticks, dtype=int)
            formatted_xticks = [profile.index[j] for j in x_ticks]
            formatted_xticklabels = [f'{x:.1f}' if isinstance(x, (int, float)) else str(x) for x in formatted_xticks]
            ax.set_xticks(formatted_xticks)
            ax.set_xticklabels(formatted_xticklabels, rotation=-90, ha="right")

    if plot:
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.show()

    return gauss_peak_x, lorentz_peak_x

def plot_y_profiles(explist, exptitles, method='mean', col_nums=4, plot=False):
    num_dfs = len(explist)
    row_nums = math.ceil(num_dfs / col_nums)

    gauss_peak_y = []
    lorentz_peak_y = []

    if plot:
        fig, axes = plt.subplots(row_nums, col_nums, figsize=(20, row_nums * 5))
        axes = axes.flatten() if num_dfs > 1 else [axes]

    for i, (df, title) in enumerate(zip(explist, exptitles)):
        if method == 'mean':
            profile = df.mean(axis=1)
        elif method == 'median':
            profile = df.median(axis=1)
        else:
            raise ValueError("Method must be 'mean' or 'median'")

        x_data = np.arange(len(profile))
        y_data = profile.values
        x_labels = profile.index

        popt_gauss, _ = curve_fit(gaussian, x_data, y_data, p0=[max(y_data), np.argmax(y_data), 1])
        popt_lorentz, _ = curve_fit(lorentzian, x_data, y_data, p0=[max(y_data), np.argmax(y_data), 1])

        gauss_peak_y.append(x_labels[int(round(popt_gauss[1]))])
        lorentz_peak_y.append(x_labels[int(round(popt_lorentz[1]))])

        if plot:
            ax = axes[i]
            ax.plot(x_labels, y_data, label='Profile')
            ax.plot(x_labels, gaussian(x_data, *popt_gauss), 'r--', label=f'Gaussian Fit: a={popt_gauss[0]:.2f}, x0={popt_gauss[1]:.2f}, sigma={popt_gauss[2]:.2f}')
            ax.plot(x_labels, lorentzian(x_data, *popt_lorentz), 'g--', label=f'Lorentzian Fit: a={popt_lorentz[0]:.2f}, x0={popt_lorentz[1]:.2f}, gamma={popt_lorentz[2]:.2f}')
            ax.set_title(f'{title} - Y-profile')
            ax.set_xlabel('Index')
            ax.set_ylabel('Values')
            ax.legend()
            plt.setp(ax.get_xticklabels(), rotation=-90, ha="left")

    if plot:
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout()
        plt.show()

    return gauss_peak_y, lorentz_peak_y

def origin_dataframes(explist, peak_x, peak_y, exptitles, save=False, filename=None):
    import os

    peak_x = [convert_to_float(x) for x in peak_x]
    peak_y = [convert_to_float(y) for y in peak_y]

    if save and filename:
        if not os.path.exists('origin'):
            os.makedirs('origin')

    shifted_explist = []

    for i, df in enumerate(explist):
        shift_df = df.copy()

        try:
            float_columns = df.columns.astype(float)
            new_columns = float_columns - peak_x[i]
        except ValueError:
            print(f"Error converting columns to float for DataFrame {i}, generating evenly spaced columns.")
            first_col = float(df.columns[0])
            last_col = float(df.columns[-1])
            total_cols = df.shape[1]
            new_columns = np.linspace(first_col - peak_x[i], last_col - peak_x[i], total_cols)

        try:
            float_index = df.index.astype(float)
            new_index = float_index - peak_y[i]
        except ValueError:
            print(f"Error converting index to float for DataFrame {i}, keeping original index.")
            new_index = df.index

        shift_df.columns = new_columns
        shift_df.index = new_index

        shifted_explist.append(shift_df)

        if save and filename:
            save_filename = f"origin/{filename}_{exptitles[i]}.csv"
            counter = 1
            while os.path.exists(save_filename):
                save_filename = f"origin/{filename}_{exptitles[i]}_{counter:03}.csv"
                counter += 1
            shift_df.to_csv(save_filename)

    return shifted_explist

def shift_and_preview(explist, exptitles, plot=True):
    gauss_peak_x_mean, _ = plot_x_profiles(explist, exptitles, method='mean', col_nums=4)
    gauss_peak_y_mean, _ = plot_y_profiles(explist, exptitles, method='mean', col_nums=4)

    explist_shifted_gauss = origin_dataframes(explist.copy(), gauss_peak_x_mean, gauss_peak_y_mean, exptitles, save=True, filename="gauss_shifted")

    img_bytes = None
    if plot:
        img_bytes = create_plot(explist_shifted_gauss, exptitles)

    return gauss_peak_x_mean, gauss_peak_y_mean, explist_shifted_gauss, img_bytes

def angle_to_q(angle, E0, E_loss):
    if E_loss < 0 or angle < 0:
        return np.nan

    hbar_eV = 6.582119569e-16  # eV*s
    m_e_eV = 0.5109989461e6 / (299792458**2)  # eV/(m/s)^2
    c = 299792458  # m/s

    k0 = np.sqrt(2 * m_e_eV * E0) / (hbar_eV * c)
    k1 = np.sqrt(2 * m_e_eV * (E0 - E_loss)) / (hbar_eV * c)

    q = np.sqrt(k0**2 + k1**2 - 2*k0*k1*np.cos(angle))

    return q  # Å^-1로 변환

def find_zero_indices(q_values, new_q_values, debugging=False):
    original_zeros = np.where(q_values == 0)[0]
    new_zeros = np.where(new_q_values == 0)[0]

    if debugging:
        print(f"Original q_values zero indices: {original_zeros}")
        print(f"New q_values zero indices: {new_zeros}")

    return original_zeros, new_zeros

def process_q_values(q_values, debugging=True):
    valid_q = q_values[~np.isnan(q_values) & ~np.isinf(q_values)]

    if debugging:
        print(f"Valid q values: {valid_q}")

    if len(valid_q) == 0:
        if debugging:
            print("No valid q values found, returning original q_values")
        return q_values

    positive_q = valid_q[valid_q > 0]
    if len(positive_q) == 0:
        if debugging:
            print("No positive q values found, returning original q_values")
        return q_values

    min_positive_q = np.min(positive_q)
    q_step = np.min(np.diff(np.sort(valid_q)))

    if debugging:
        print(f"Minimum positive q: {min_positive_q}")
        print(f"Calculated q_step: {q_step}")

    if q_step > 0:
        num_nan = np.sum(np.isnan(q_values))
        negative_q = np.arange(0, -num_nan * q_step, -q_step)[::-1]

        new_q_values = np.full_like(q_values, np.nan)
        new_q_values[:len(negative_q)] = negative_q
        new_q_values[len(negative_q):] = valid_q

        if debugging:
            print(f"Generated new_q_values (first 10): {new_q_values[:10]}")
            print(f"Generated new_q_values (last 10): {new_q_values[-10:]}")

        find_zero_indices(q_values, new_q_values, debugging=debugging)

        return new_q_values
    else:
        if debugging:
            print("q_step is not positive, returning original q_values")
        return q_values


def plot_data_with_q_conversion(explist, exptitles, gauss_y, num_cols=2,
                                q_min=None, q_max=None, E_min=None, E_max=None,
                                figsize=(6, 5), title_fontsize=20, label_fontsize=14,
                                cbar_pos=[0.92, 0.063, 0.02, 0.15], cmap='inferno',
                                font_family='sans-serif', font_style='normal', font_weight='normal',
                                num_ticks_x=5, num_ticks_y=5, tick_fontsize=12,
                                apply_log=True):  # apply_log 플래그 추가
    
    print(f"Received E0 values: {gauss_y}")

    # Set font properties
    font_prop = fm.FontProperties(family=font_family, style=font_style, weight=font_weight)

    num_subplots = len(explist)
    num_rows = (num_subplots + num_cols - 1) // num_cols

    fig_width, fig_height = figsize
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(fig_width*num_cols, fig_height*num_rows))
    if num_subplots > 1:
        axs = axs.flatten()
    else:
        axs = [axs]

    plt.subplots_adjust(hspace=0.05, wspace=0.05)

    for i, (df, title) in enumerate(zip(explist, exptitles)):
        Z = df.values
        
        if apply_log and np.issubdtype(Z.dtype, np.number):
            Z = np.log1p(Z)  # Optional log transformation

        angles = df.columns.astype(float) * np.pi / 180  # Convert angles to radians
        energy_losses = df.index.astype(float)  # Energy Loss in eV

        E0 = gauss_y[i]  # 리스트에서 값을 가져옵니다.
        if E0 is None or E0 <= 0:
            raise ValueError(f"Invalid E0 value: {E0} for experiment {title}")

        q_values = np.array([angle_to_q(angle, E0, 0) for angle in angles])

        processed_q_values = process_q_values(q_values)

        # Set extent with validation
        q_min_plot = q_min if q_min is not None else np.nanmin(processed_q_values)
        q_max_plot = q_max if q_max is not None else np.nanmax(processed_q_values)
        E_min_plot = E_min if E_min is not None else np.nanmin(energy_losses)
        E_max_plot = E_max if E_max is not None else np.nanmax(energy_losses)

        # Check for NaN or Inf and replace with default values
        if np.isnan(q_min_plot) or np.isinf(q_min_plot):
            q_min_plot = 0
        if np.isnan(q_max_plot) or np.isinf(q_max_plot):
            q_max_plot = 1
        if np.isnan(E_min_plot) or np.isinf(E_min_plot):
            E_min_plot = 0
        if np.isnan(E_max_plot) or np.isinf(E_max_plot):
            E_max_plot = 1

        extent = [q_min_plot, q_max_plot, E_min_plot, E_max_plot]

        ax = axs[i]
        im = ax.imshow(Z, aspect='auto', origin='lower', extent=extent, cmap=cmap)

        ax.set_title(f"{title}, E0 = {E0:.6f} eV", fontsize=title_fontsize, fontproperties=font_prop)
        ax.set_xlabel('q (Å⁻¹)', fontsize=label_fontsize, fontproperties=font_prop)
        ax.set_ylabel('Energy Loss (eV)', fontsize=label_fontsize, fontproperties=font_prop)

        # Set font properties for axis labels
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(font_prop)

        ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)

    # Remove unused subplots
    for j in range(num_subplots, len(axs)):
        fig.delaxes(axs[j])

    # Colorbar
    cbar_ax = fig.add_axes(cbar_pos)
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='vertical')
    cbar.ax.tick_params(labelsize=label_fontsize)
    for label in cbar.ax.get_yticklabels():
        label.set_fontproperties(font_prop)

    plt.tight_layout(rect=[0, 0, 0.9, 1])
    
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
    plt.close()
    img_bytes.seek(0)

    return img_bytes, explist