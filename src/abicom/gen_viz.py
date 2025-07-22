import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.lines as mlines
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import pandas as pd
import io
from datetime import datetime


def format_date_axis():
    """Format the date axis with a specific format and auto-locator."""
    date_format = mdates.DateFormatter('%b-%y')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=15))
    plt.xticks(size=16, rotation=30)


def format_y_axis(ax):
    """Format the y-axis labels as percentage and set gridlines."""
    def custom_formatter(x, pos):
        return f"-{abs(x):,.0f}%" if x < 0 else f"{x:,.0f}%"
    
    ax.yaxis.set_major_formatter(FuncFormatter(custom_formatter))
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    # Add gridlines every 5% on the y-axis
    yticks = np.arange(np.floor(ax.get_ylim()[0] / 5) * 5, np.ceil(ax.get_ylim()[1] / 5) * 5 + 5, 5)
    ax.set_yticks(yticks)
    ax.tick_params(axis='y', labelsize=20)  # Increase the font size for y-ticks


def add_title(ax, label_comb):
    """Add the plot title and subtitle."""
    ax.text(
        x=-0.03, y=1.25, s=f"Defasagem média {label_comb}", fontsize=36, fontweight="bold", ha="left", transform=ax.transAxes
    )
    ax.text(
        x=-0.03, y=1.18, s="% em relação ao PPI. Fonte: ABICOM", fontsize=16, ha="left", transform=ax.transAxes
    )
    ax.text(
        x=-0.03, y=1.13, s="@EconDataViz", fontsize=13, fontweight='heavy', ha="left", transform=ax.transAxes
    )


def add_legend(ax):
    """Add legend with color-coded labels."""
    legend_handles = [
        mlines.Line2D([], [], color='blue', linewidth=3.5, label='Defasagem diária'),
        Rectangle((0, 0), 1, 1, facecolor='red', edgecolor='red', label='Zona de reajuste', alpha=0.3)
    ]
    ax.legend(handles=legend_handles, loc='center', bbox_to_anchor=(0.5, 1.08), ncol=2, frameon=False, prop={'size': 16})


def annotate_last_value(ax, df, combustivel):
    """Annotate the last value of the chosen 'combustivel'."""
    last_comb_value = df[f"{combustivel}"].values[-1]
    ax.annotate(
        f'{last_comb_value:.0f}%', 
        (df[f"{combustivel}"].index[-1], df[f"{combustivel}"].values[-1]), 
        fontsize=20, 
        color='red' if last_comb_value < 0 else 'green', 
        weight='bold'
    )


def gen_graph(df, combustivel):
    label_comb = combustivel.split('_')[0].upper()

    # Create the figure
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)
    fig, ax = plt.subplots(figsize=figsize_inches, dpi=dpi)

    # Plot the line
    sns.lineplot(data=df, y=f'{combustivel}', x=df.index, color='blue', linewidth=3.5, legend=False, ax=ax)

    # Add horizontal line at y=0
    ax.hlines(y=0, xmin=df.index[0], xmax=df.index[-1], linestyles='dashed', alpha=0.7, color='black', linewidth=3)

    # Format the x and y axes
    format_date_axis()
    format_y_axis(ax)

    # Set y-axis limits and fill between
    ymin, ymax = ax.get_ylim()
    reajuste = -20
    ax.set_ylim(bottom=min(ymin, reajuste), top=ymax)
    ax.fill_between(df.index, reajuste, ymin, color='red', alpha=0.3)

    # Add title and legend
    add_title(ax, label_comb)
    add_legend(ax)

    # Annotate last value
    annotate_last_value(ax, df, combustivel)

    # Remove borders and ticks
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Set x-axis limits
    ax.set_xlim(left=df.index[0], right=df.index[-1])

    # Remove axis labels (x and y titles)
    ax.set_xlabel('')
    ax.set_ylabel('')

    # Finalize plot
    plt.tight_layout(rect=(0, 0, 1.1, 1))
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)

    return img_buffer

def gen_text(df, combustivel):
    df['year_ma'] = df[f'{combustivel}'].dropna().rolling(252).mean()
    df = df[[f'{combustivel}', 'year_ma']]
    today = datetime.today()
    # Define the Unicode characters for the red and green circles
    red_circle = "\U0001F534"
    green_circle = "\U0001F7E2"

    # Check the condition and create the text
    text = (
        f'{red_circle if df[combustivel].values[-1] < 0 else green_circle} Defasagem média {combustivel.split("_")[0].upper()} em {today.strftime("%d/%m/%Y")}: {int(df[combustivel].values[-1])} %.\n'
        f'Defasagem média anual: {df["year_ma"].values[-1]:.2f} %.\n'
        'Fonte: ABICOM'
      )

    return text