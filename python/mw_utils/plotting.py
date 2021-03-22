"""
Module containing some plotting functions.
"""

import pandas as pd
import numpy as np
from typing import Optional

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cycler import cycler

plt.style.use("seaborn-colorblind")
PLT_COLOR = plt.rcParams["axes.prop_cycle"].by_key()["color"]
PLT_LINES = ["-", "--", ":", "-."]
PLT_CYCLER = cycler(color=PLT_COLOR * 2) + cycler(linestyle=PLT_LINES * 3)


def set_cycle(ax: plt.axes) -> plt.axes:
    """
    Sets colorblind- and bq-print friendly axes property cycle.
    Plotting styles are specified as follows:
    1. Set plotting styles for our disadvantaged colleagues
       using the seaborn-colorblind colorscheme

    2. Set line styles in order to be able to distinguish plot lines
       without relying on color or brightness information

    3. Combine colors and line styles in cycler
       in order to yield maximum distinguishability of plot lines

    Parameters
    ----------
    ax : matplotlib.axes
        Matplotlib axes object

    Returns
    -------
    Matplotlib axes object
    """
    ax.set_prop_cycle(PLT_CYCLER)
    return ax


def place_textbox(ax: plt.axes, title: str) -> None:
    """
    Places textbox in center of plot.

    Parameters
    ----------
    ax : matplotlib.axes
        Matplotlib axes object.
    title : str
        Text in the textbox.
    """
    props = dict(boxstyle="round", facecolor="white", alpha=0.7)
    _ = ax.text(
        0.5,
        0.92,
        title,
        horizontalalignment="center",
        transform=ax.transAxes,
        bbox=props,
    )


def shap_summary_plot(
    shap_df: pd.DataFrame,
    feature_df: Optional[pd.DataFrame] = None,
    title: Optional[str] = None,
    max_display: Optional[int] = 10,
    cmap: Optional[str] = "coolwarm",
) -> plt.figure:
    """
    Plots SHAP feature importance bars and feature influence in summary-dot plot.
    Based on https://github.com/slundberg/shap/shap/plots/_beeswarm.py
    TODO: This function needs refactoring!

    shap_values : DataFrame
        SHAP values as a dataframe with feature names as columns.
    feature_df : DataFrame (default=None)
        Sampled feature dataframe or None.
    max_display : int (default=10)
        Number of top features to display.
    cmap : str (default="coolwarm")
        Standard matplotlib colormap name to use for color-coding feature values
        in the summary plot.

    Returns
    -------
    matplotlib.figure.Figure
        Matplotlib figure object.
    """

    shap_values = shap_df.values
    shap_cols = shap_df.columns.tolist()

    shap_features = None if feature_df is None else feature_df.values

    feature_order = np.argsort(np.sum(np.abs(shap_values), axis=0))
    feature_order = feature_order[-min(max_display, len(feature_order)) :]
    importances = [np.abs(shap_values).mean(0)[i] for i in feature_order]
    feature_names = [shap_cols[i] for i in feature_order]

    _, axs = plt.subplots(1, 2, figsize=(10, 1 + max_display * 0.5), sharey=True)
    for ax in axs:
        ax.grid(axis="y", zorder=0, linestyle="--")
    axs[0].barh(feature_names, importances, height=0.5, zorder=3)

    for pos, i in enumerate(feature_order):

        shaps = shap_values[:, i]
        values = None if shap_features is None else shap_features[:, i]
        inds = np.arange(len(shaps))
        np.random.shuffle(inds)
        if values is not None:
            values = values[inds]
        shaps = shaps[inds]
        values = np.array(values, dtype=np.float64)
        nbins = 100
        quant = np.round(
            nbins * (shaps - np.min(shaps)) / (np.max(shaps) - np.min(shaps) + 1e-8)
        )
        inds = np.argsort(quant + np.random.randn(len(shaps)) * 1e-6)
        layer = 0
        last_bin = -1
        ys = np.zeros(len(shaps))
        for ind in inds:
            if quant[ind] != last_bin:
                layer = 0
            ys[ind] = np.ceil(layer / 2) * ((layer % 2) * 2 - 1)
            layer += 1
            last_bin = quant[ind]
        ys *= 0.36 / np.max(ys + 1)

        vmin = np.nanpercentile(values, 5)
        vmax = np.nanpercentile(values, 95)
        if vmin == vmax:
            vmin = np.nanpercentile(values, 1)
            vmax = np.nanpercentile(values, 99)
            if vmin == vmax:
                vmin = np.min(values)
                vmax = np.max(values)
        if vmin > vmax:
            vmin = vmax

        nan_mask = np.isnan(values)

        cvals = values[np.invert(nan_mask)].astype(np.float64)
        cvals_imp = cvals.copy()
        cvals_imp[np.isnan(cvals)] = (vmin + vmax) / 2.0
        cvals[cvals_imp > vmax] = vmax
        cvals[cvals_imp < vmin] = vmin

        scatter_kwargs = {
            "linewidth": 0.1,
            "zorder": 3,
            "alpha": 0.5,
            "rasterized": len(shaps) > 500,
        }

        # Plot importances without feature values:
        axs[1].scatter(
            shaps[nan_mask],
            pos + ys[nan_mask],
            color="gray",
            vmin=vmin,
            vmax=vmax,
            s=16,
            **scatter_kwargs,
        )

        # Plot importances with feature values:
        sp = axs[1].scatter(
            shaps[np.invert(nan_mask)],
            pos + ys[np.invert(nan_mask)],
            c=cvals,
            cmap=cmap,
            edgecolors="gray",
            **scatter_kwargs,
        )

        axs[1].set_yticks(range(max_display))
        axs[1].set_yticklabels(feature_names)

    if shap_features is not None:
        div = make_axes_locatable(axs[1])
        cax = div.append_axes("right", size="2%", pad=0.05)
        _ = plt.colorbar(sp, cax=cax, ticks=[])

    axs[0].set_xlabel("Feature Importance")
    axs[1].set_xlabel("Feature Influence")
    axs[1].axvline(linewidth=1, color="lightgray", linestyle="--")
    axs[1].yaxis.set_ticks_position("none")

    for _, spine in axs[0].spines.items():
        spine.set_zorder(10)

    _ = plt.suptitle(title)
    _ = plt.tight_layout()
    return plt.gcf()
