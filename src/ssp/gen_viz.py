import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from io import BytesIO


def gen_viz(df):
    # Data preparation
    data = df.iloc[-13:,]

    # Set up figure and axes
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)
    fig, ax = plt.subplots(figsize=figsize_inches, dpi=dpi)

    # Bar plot parameters
    bar_width = 0.4
    x_positions = np.arange(len(data))

    # Plotting bars
    ax = sns.barplot(data=data, x='data', y='estado', color='royalblue', ax=ax)
    sns.barplot(data=data, x='data', y='capital', color='darkgreen', ax=ax)

    # Adjust x-axis limits
    plt.xlim(-0.7, len(data) - 0.3)

    # Increase xticks font size
    plt.tick_params(axis='x', which='major', labelsize=14)

    # Annotations
    for index, (value_estado, value_capital) in enumerate(zip(data['estado'], data['capital'])):
        ax.text(x_positions[index], value_estado, f'{value_estado}', ha='center', va='top', fontsize=14, color='white')
        ax.text(x_positions[index], value_capital, f'{value_capital}', ha='center', va='top', fontsize=14, color='white')

    # Title and subtitle
    plt.text(
        x=0, 
        y=1.05,  
        s="Total de roubos em São Paulo", 
        fontsize=36, 
        fontweight="bold",
        ha="left",
        transform=fig.transFigure  
    )
    plt.text(
        x=0, 
        y=1.00,  
        s="(em nº de ocorrências). Fonte: SSP", 
        fontsize=16, 
        ha="left",
        transform=fig.transFigure  
    )

    # Customize plot appearance
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    plt.yticks([])
    plt.tick_params(axis='x', length=0, width=0)
    ax.set_ylabel('')
    ax.set_xlabel('')

    # Legend
    legend_handles = [
        mlines.Line2D([], [], marker='s', markersize=15, linestyle='None', color='w', markerfacecolor='royalblue', label='Estado'),
        mlines.Line2D([], [], marker='s', markersize=15, linestyle='None', color='w', markerfacecolor='darkgreen', label='Capital')
    ]
    plt.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, frameon=False, prop={'size': 16})

    # Final adjustments
    plt.subplots_adjust(left=0.0, right=1)
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)  # Move the cursor to the beginning of the BytesIO object

    # Return the BytesIO object
    return img_buffer