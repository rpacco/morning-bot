import matplotlib.pyplot as plt
import numpy as np
import matplotlib.lines as mlines
from io import BytesIO

def wrangle(df):
    # Define the patterns and their corresponding names
    def map_column(col):
        col_lower = col.lower()
        if any(item in col_lower for item in ['12 meses', 'ano anterior']):
            return 'Variação acumulada em 12 meses'
        elif 'mês' in col_lower or 'mensal' in col_lower:
            return 'Variação mensal'
        else:
            return col  # Return the original column name if no pattern matches

    # Apply the mapping function to each column name
    df.columns = [map_column(col) for col in df.columns]

    df = df.iloc[-13:,]
    
    return df

def gen_chart(df, name, subtitle):
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)
    fig = plt.figure(figsize=figsize_inches, dpi=dpi)

    bar_width = 0.4
    x_positions = np.arange(len(df))
    plt.xlim(-0.7, len(df) -0.3)

    plt.bar(x_positions - bar_width/2, df['Variação mensal'], width=bar_width, label='Valor MM', color='royalblue')
    plt.bar(x_positions + bar_width/2, df['Variação acumulada em 12 meses'], width=bar_width, label='Valor 12MM', color='orange')

    plt.xticks(ticks=x_positions, labels=[x.strftime("%b/%y") for x in df.index], size=14, color='darkslategray')
    plt.ylabel('')
    plt.yticks([])
    plt.tick_params(axis='x', length=0, width=0)

    for index, (value_mm, value_12mm) in enumerate(zip(df['Variação mensal'], df['Variação acumulada em 12 meses'])):
        plt.text(index - bar_width/2, value_mm, f'{value_mm:.2f}', ha='center', va='bottom' if value_mm >= 0 else 'top', fontsize=12, color='darkslategray')
        plt.text(index + bar_width/2, value_12mm, f'{value_12mm:.2f}', ha='center', va='bottom' if value_12mm >= 0 else 'top', fontsize=12, color='darkslategray')

    ax = plt.gca()
    for label in ax.get_xticklabels():
        label.set_horizontalalignment('center')

    # Add title and subtitle
    plt.text(
        x=0, 
        y=1.18,  
        s=f"{name}", 
        fontsize=36, 
        fontweight="bold",
        ha="left",
        transform=plt.gca().transAxes  
    )
    plt.text(
        x=0, 
        y=1.13,  
        s=f"{subtitle}. Fonte: IBGE", 
        fontsize=16, 
        ha="left",
        transform=plt.gca().transAxes  
    )
    plt.text(
        x=0, 
        y=1.08,  
        s="@EconDataViz", 
        fontsize=13, 
        fontweight='heavy',
        ha="left",
        transform=plt.gca().transAxes  
    )

    # Remove borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    legend_handles = [
        mlines.Line2D([], [], marker='s', markersize=15, linestyle='None', color='w', markerfacecolor='royalblue', label='% MoM'),
        mlines.Line2D([], [], marker='s', markersize=15, linestyle='None', color='w', markerfacecolor='orange', label='% YoY')
    ]

    plt.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, frameon=False, prop={'size': 16})

    plt.tight_layout()
    plt.subplots_adjust(top=0.9, bottom=0.15)

    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)  # Move the cursor to the beginning of the BytesIO object

    # Return the BytesIO object
    return img_buffer

