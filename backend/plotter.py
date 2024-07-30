import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

plt.switch_backend('Agg')


def plot(explist, exptitles, save2D=True, num_xticks=5, num_yticks=5, num_cols=2):
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