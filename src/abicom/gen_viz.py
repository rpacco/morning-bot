import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import datetime
from io import BytesIO
from adjustText import adjust_text

# Formatting y-axis labels
def currency_formatter(x, pos):
    return f'{x:.2f}'  # Format numbers as currency

def wrangle(df: pd.DataFrame, combustivel: str):
    df['year_ma'] = round(df[combustivel].rolling(252).mean(), 2)
    df = df[[combustivel, 'year_ma']].dropna(how='any')
    
    return df

def gen_graph(df, combustivel):
    label_comb = combustivel.split('_')[0].upper()
    
    # Slice the DataFrame to exclude the last 20 rows
    df_filtered = df.iloc[0:-20]

    # Find the 5 largest values from the filtered DataFrame
    nlargest = df_filtered[f'{combustivel}'].nlargest(5)
    largest_filtered_indices = []
    largest_previous_indices = []

    for index in nlargest.index:
        if not largest_previous_indices or all((index - prev_index).days > 30 for prev_index in largest_previous_indices):
            largest_filtered_indices.append(index)
            largest_previous_indices.append(index)

    nlargest = nlargest.loc[largest_filtered_indices]

    # Find the 5 smallest values from the filtered DataFrame
    nsmallest = df_filtered[f'{combustivel}'].nsmallest(5)
    smallest_filtered_indices = []
    smallest_previous_indices = []

    for index in nsmallest.index:
        if not smallest_previous_indices or all((index - prev_index).days > 30 for prev_index in smallest_previous_indices):
            smallest_filtered_indices.append(index)
            smallest_previous_indices.append(index)

    nsmallest = nsmallest.loc[smallest_filtered_indices]

    today = datetime.today().date()
    dpi = 100
    # Calculate the figure size in inches
    figsize_inches = (1024 / dpi, 762 / dpi)
    # Create the figure
    fig = plt.figure(figsize=figsize_inches, dpi=dpi)
    ax = sns.lineplot(data=df, y=f'{combustivel}', x=df.index, color='blue', linewidth=2, label=f'Defasagem {label_comb.lower()}')
    sns.lineplot(data=df, y='year_ma', x=df.index, color='green' if df['year_ma'].iloc[-1] >=0 else 'salmon', linewidth=1.5, label='Média móvel 252 dias')

    date_format = mdates.DateFormatter('%b-%Y')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=90, size=12)
    plt.xlabel('')
    plt.hlines(y=0, xmin=df.index[0], xmax=df.index[-1], linestyles='dashed', alpha=0.2)

    ax.set_title(f'Defasagem média {label_comb} (R$/L)', weight='bold', fontdict={'size': 26})
    plt.figtext(0.02, 0.95, 'Fonte: Abicom', fontsize=10, color='gray')

    def custom_formatter(x, pos):
        return f"-R${abs(x):,.2f}" if x < 0 else f"R${x:,.2f}"
    ax.yaxis.set_major_formatter(FuncFormatter(custom_formatter))
    plt.ylabel('')
    plt.yticks(size=14)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    last_comb_value = ax.annotate(
        f'{df[f"{combustivel}"].values[-1]:.2f}', 
        (df[f"{combustivel}"].index[-1], df[f"{combustivel}"].values[-1]), 
        # textcoords="offset points",
        # xytext=(5,0), 
        # ha='left', 
        fontsize=12, 
        color='black', 
        weight='bold'
    )
    last_ma_value = ax.annotate(
        f'{df["year_ma"].values[-1]:.2f}', 
        (df["year_ma"].index[-1], 
        df["year_ma"].values[-1]), 
        # textcoords="offset points", 
        # xytext=(5,0), 
        # ha='left', 
        fontsize=12, 
        color='green' if df["year_ma"].values[-1] > 0 else 'red', 
        weight='bold'
        )
    
    adjust_text([last_comb_value, last_ma_value], only_move={'text': 'y'})
    # Get the current x-coordinates of the annotations
    x_comb = last_comb_value.get_position()[0]
    x_ma = last_ma_value.get_position()[0]

    # Calculate the offset
    x_offset = 7

    # Set the new x-coordinates
    last_comb_value.set_position((x_comb + x_offset, last_comb_value.get_position()[1]))
    last_ma_value.set_position((x_ma + x_offset, last_ma_value.get_position()[1]))

    # Annotate the smallest values
    for value, date in zip(nsmallest.values, nsmallest.index):
        ax.annotate(f'{value:.2f}', (date, value), textcoords="offset points", xytext=(0, -10), ha='center', fontsize=12, color='red', weight='bold')

    # Annotate the largest values
    for value, date in zip(nlargest.values, nlargest.index):
        ax.annotate(f'{value:.2f}', (date, value), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=12, color='green', weight='bold')

    plt.tick_params(axis='both', length=0, width=0)
    ax.spines['bottom'].set_color('gray')

    plt.tight_layout()
    plt.legend()

    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)  # Move the cursor to the beginning of the BytesIO object

    # Return the BytesIO object
    return img_buffer

def gen_text(df, combustivel):
    today = datetime.today()
    # Define the Unicode characters for the red and green circles
    red_circle = "\U0001F534"
    green_circle = "\U0001F7E2"

    # Check the condition and create the text
    text = (
        f'{red_circle if df[combustivel].values[-1] < 0 else green_circle} Defasagem média {combustivel.split("_")[0].upper()} em {today.strftime("%d/%m/%Y")}: {df[combustivel].values[-1]:.2f} R$/L.\n'
        f'Média defasagem últimos 252 dias: {df["year_ma"].values[-1]:.2f} R$/L.\n'
        'Fonte: ABICOM'
      )

    return text