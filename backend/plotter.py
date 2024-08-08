import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from io import BytesIO

plt.switch_backend('Agg')


def gaussian(x, a, x0, sigma):
    return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

def lorentzian(x, a, x0, gamma):
    return a * gamma ** 2 / ((x - x0) ** 2 + gamma ** 2)

def convert_to_float(value):
    try:
        return float(value)
    except ValueError:
        return value


def create_plot(explist, exptitles, save2D=True, num_xticks=5, num_yticks=5, num_cols=2):
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

    for i, (df, title) in enumerate(zip(explist, exptitles)):
        Z = df.values
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

    cbar_ax = fig.add_axes([0.92, 0.063, 0.02, 0.15])
    fig.colorbar(im, cax=cbar_ax, orientation='vertical')

    plt.tight_layout(rect=[0, 0, 0.9, 1])

    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='png')
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
