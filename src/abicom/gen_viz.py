import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import datetime
from io import BytesIO
from adjustText import adjust_text
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines

# Formatting y-axis labels
def currency_formatter(x, pos):
    return f'{x:.2f}'  # Format numbers as currency

def wrangle(df: pd.DataFrame, combustivel: str):
    df = df.dropna()
    df['year_ma'] = round(df[combustivel].rolling(252).mean(), 2)
    df = df[[combustivel, 'year_ma']]
    
    return df

def filter_values(values):
    filtered_indices = []
    previous_indices = []
    for index in values.index:
        if not previous_indices or all((index - prev_index).days > 30 for prev_index in previous_indices):
            filtered_indices.append(index)
            previous_indices.append(index)
    return values.loc[filtered_indices]

def gen_graph(df, combustivel):
    label_comb = combustivel.split('_')[0].upper()

    # Slice the DataFrame to exclude the last 20 rows
    df_filtered = df.iloc[:-20]
    # Find the 5 largest and smallest values from the filtered DataFrame
    nlargest = df_filtered[f'{combustivel}'].nlargest(5)
    nsmallest = df_filtered[f'{combustivel}'].nsmallest(5)
    nlargest = filter_values(nlargest)
    nsmallest = filter_values(nsmallest)

    # Create the figure
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)
    fig = plt.figure(figsize=figsize_inches, dpi=dpi)

    # Plot the lines
    ax = sns.lineplot(data=df, y=f'{combustivel}', x=df.index, color='blue', linewidth=2, legend=False)
    sns.lineplot(data=df, y='year_ma', x=df.index, color='green' if df['year_ma'].iloc[-1] >= 0 else 'salmon', linewidth=1.5, legend=False)

    # Set y-axis limits
    reajuste = -20
    ymin, ymax = ax.get_ylim()
    if ymin < reajuste:
        ymin = ymin
    else:
        ymin = -22
    ax.set_ylim(bottom=ymin, top=ymax)
    plt.fill_between(df.index, reajuste, ymin, color='red', alpha=0.3)

    # Add horizontal line
    plt.hlines(y=0, xmin=df.index[0], xmax=df.index[-1], linestyles='dashed', alpha=0.2)
    # Format x-axis
    date_format = mdates.DateFormatter('%b-%y')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=15))
    plt.xticks(size=12)
    plt.xlabel('')

    # Add title and subtitle
    plt.text(
        x=-0.03, 
        y=1.25,  
        s=f"Defasagem média {label_comb}", 
        fontsize=36, 
        fontweight="bold",
        ha="left",
        transform=plt.gca().transAxes  
    )
    plt.text(
        x=-0.03, 
        y=1.18,  
        s=f"% em relação ao PPI. Fonte: ABICOM", 
        fontsize=16, 
        ha="left",
        transform=plt.gca().transAxes  
    )

    # Format y-axis
    def custom_formatter(x, pos):
        return f"-{abs(x):,.0f}%" if x < 0 else f"{x:,.0f}%"
    ax.yaxis.set_major_formatter(FuncFormatter(custom_formatter))
    plt.ylabel('')
    plt.yticks(size=14)

    # Annotate last values
    last_comb_value = ax.annotate(
        f'{df[f"{combustivel}"].values[-1]:.0f}%', 
        (df[f"{combustivel}"].index[-1], df[f"{combustivel}"].values[-1]), 
        fontsize=12, 
        color='black', 
        weight='bold'
    )
    last_ma_value = ax.annotate(
        f'{df["year_ma"].values[-1]:.1f}%', 
        (df["year_ma"].index[-1], df["year_ma"].values[-1]), 
        fontsize=12, 
        color='green' if df["year_ma"].values[-1] > 0 else 'red', 
        weight='bold'
    )
    adjust_text([last_comb_value, last_ma_value], only_move={'text': 'y'})
    last_ma_value.set_position((last_ma_value.get_position()[0] + 7, last_ma_value.get_position()[1]))
    last_comb_value.set_position((last_comb_value.get_position()[0] + 7, last_comb_value.get_position()[1]))

    # Annotate smallest and largest values
    for value, date in zip(nsmallest.values, nsmallest.index):
        ax.annotate(f'{value:.0f}%', (date, value), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=12, color='black', weight='bold')
    for value, date in zip(nlargest.values, nlargest.index):
        ax.annotate(f'{value:.0f}%', (date, value), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=12, color='black', weight='bold')

    # Add legend
    legend_handles = [
        mlines.Line2D([], [], color='blue', linewidth=2, label=f'Defasagem diária'),
        mlines.Line2D([], [], color='green' if df['year_ma'].iloc[-1] >= 0 else 'salmon', linewidth=1.5, label='Média anual'),
        Rectangle((0, 0), 1, 1, facecolor='red', edgecolor='red', label='Zona de reajuste', alpha=0.3)
    ]
    plt.legend(handles=legend_handles, loc='center', bbox_to_anchor=(0.5, 1.1), ncol=3, frameon=False, prop={'size': 14})

    # Remove borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Remove ticks
    plt.tick_params(axis='x', length=0, width=0)
    # Set x-axis to start at y=0
    ax.set_xlim(left=df.index[0], right=df.index[-1])
    # Finalize plot
    plt.tight_layout(rect=(0, 0, 1.1, 1))

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)

    return img_buffer

def gen_text(df, combustivel):
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