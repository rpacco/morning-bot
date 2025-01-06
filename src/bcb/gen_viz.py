import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.lines as mlines
from matplotlib.ticker import FuncFormatter
from io import BytesIO
import numpy as np


def billions(x, pos):
    """The two args are the value and tick position"""
    return f'R${x/1e3:.1f}B'

def viz_fiscais(df, name):
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)

    df = df.loc['2023':].copy()
    df['month'] = df.index.strftime('%b/%y')

    # Set up the matplotlib figure
    fig, ax1 = plt.subplots(figsize=figsize_inches, dpi=dpi)
    fig.patch.set_facecolor('#F7F7F7')

    # Create the barplot for monthly data on the first y-axis
    bars = sns.barplot(x='month', y='MoM', data=df, color='steelblue', legend=False, alpha=0.6, ax=ax1)

    # Create a second y-axis for the TTM data
    ax2 = ax1.twinx()

    # Create the lineplot for TTM data on the second y-axis
    sns.lineplot(x='month', y='YoY', data=df, color='darkblue', marker='o', legend=False, ax=ax2)


    # Rotate x-axis labels by 90 degrees
    for tick in ax1.get_xticklabels():
        tick.set_rotation(90)
        tick.set_ha('center')  # Center-align the label text

    # Manually add y-axis labels at the top
    ax1.yaxis.label.set_visible(False)  # Hide default label
    ax1.xaxis.label.set_visible(False)
    ax2.yaxis.label.set_visible(False)  # Hide default label

    # Add custom labels at the top
    ax1.text(0, 1.05, 'Último mês\n(bilhões R$)', transform=ax1.transAxes, ha='right', va='center', color='steelblue', fontsize=11)
    ax2.text(1, 1.05, 'Últimos 12 meses\n(bilhões R$)', transform=ax2.transAxes, ha='left', va='center', color='darkblue', fontsize=11)

    # Setting the ticks color to match the plot
    ax1.tick_params(axis='y', labelcolor='steelblue', labelsize=12)
    ax2.tick_params(axis='y', labelcolor='darkblue', labelsize=12)

    # Format y-axis labels as currency in billions
    formatter = FuncFormatter(billions)
    ax1.yaxis.set_major_formatter(formatter)
    ax2.yaxis.set_major_formatter(formatter)

    # Adjust tick locations for clarity (optional)
    ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    plt.figtext(
        0.5, 0.98, f'{name}', ha='center',
        fontsize=44, fontweight='demibold', color='darkslategray', family='serif'
    )

    plt.figtext(0.98, 0.03, 'Fonte: BCB.', fontsize=14, color='darkslategray', ha='right')

    legend_handles = [
        mlines.Line2D([], [], marker='s', markersize=15, linestyle='None', color='w', markerfacecolor='steelblue', label='Mensal'),
        mlines.Line2D([], [], marker='s', markersize=15, linestyle='None', color='w', markerfacecolor='darkblue', label='Acumulado 12 meses')
    ]

    plt.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 1.08), ncol=2, frameon=False, prop={'size': 14})

    plt.subplots_adjust(top=1.1, bottom=0.15, left=0, right=1)
    plt.tight_layout()

    # plt.savefig(f'{name}.jpg', dpi=dpi, bbox_inches='tight')
    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)  # Move the cursor to the beginning of the BytesIO object

    # Return the BytesIO object
    return img_buffer


def viz_pct(df, name):
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)
    fig = plt.figure(figsize=figsize_inches, dpi=dpi)
    fig.patch.set_facecolor('#F7F7F7')

    df = df.iloc[-13:,]

    bar_width = 0.4
    x_positions = np.arange(len(df))
    plt.xlim(-0.7, len(df) -0.3)

    plt.bar(x_positions - bar_width/2, df['MoM'], width=bar_width, label='Valor MM', color='royalblue')
    plt.bar(x_positions + bar_width/2, df['YoY'], width=bar_width, label='Valor 12MM', color='orange')

    plt.xticks(ticks=x_positions, labels=[x.strftime("%b/%y") for x in df.index], size=14, color='darkslategray')
    plt.ylabel('')
    plt.yticks([])

    for index, (value_mm, value_12mm) in enumerate(zip(df['MoM'], df['YoY'])):
        plt.text(index - bar_width/2, value_mm, f'{value_mm:.2f}', ha='center', va='bottom' if value_mm >= 0 else 'top', fontsize=12, color='darkslategray')
        plt.text(index + bar_width/2, value_12mm, f'{value_12mm:.2f}', ha='center', va='bottom' if value_12mm >= 0 else 'top', fontsize=12, color='darkslategray')

    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_horizontalalignment('center')

    plt.figtext(
        0.5, 0.98, f'{name}', ha='center',
        fontsize=44, fontweight='demibold', color='darkslategray', family='serif'
    )

    plt.grid(True, axis='y', color='gainsboro', linewidth=1.5)

    ax.spines['top'].set(edgecolor='gainsboro', linewidth=2)
    ax.spines['right'].set(edgecolor='gainsboro', linewidth=2)
    ax.spines['left'].set(edgecolor='gainsboro', linewidth=2)
    ax.spines['bottom'].set(edgecolor='gainsboro', linewidth=2)

    plt.figtext(0.01, 0.05, 'Fonte: Banco Central do Brasil.', fontsize=14, color='darkslategray')

    legend_handles = [
        mlines.Line2D([], [], marker='s', markersize=15, linestyle='None', color='w', markerfacecolor='royalblue', label='% MoM'),
        mlines.Line2D([], [], marker='s', markersize=15, linestyle='None', color='w', markerfacecolor='orange', label='% YoY')
    ]

    plt.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, frameon=False, prop={'size': 16})

    plt.tight_layout()
    plt.subplots_adjust(top=0.9, bottom=0.15)

    # plt.savefig(f'{name}.jpg', dpi=dpi, bbox_inches='tight')
    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)  # Move the cursor to the beginning of the BytesIO object

    # Return the BytesIO object
    return img_buffer