import matplotlib.pyplot as plt
import numpy as np
import matplotlib.lines as mlines
from io import BytesIO

def wrangle(df):
    # Define the patterns and their corresponding names
    def map_column(col):
        col_lower = col.lower()  # Convert column name to lowercase for case-insensitive matching
        if 'mês' in col_lower or 'mensal' in col_lower:
            return 'Variação mensal'
        elif '12 meses' in col_lower:
            return 'Variação acumulada em 12 meses'
        else:
            return col  # Return the original column name if no pattern matches

    # Apply the mapping function to each column name
    df.columns = [map_column(col) for col in df.columns]

    df = df.iloc[-13:,]
    
    return df

def gen_chart(df, name):
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)
    fig = plt.figure(figsize=figsize_inches, dpi=dpi)
    fig.patch.set_facecolor('#F7F7F7')

    bar_width = 0.4
    x_positions = np.arange(len(df))
    plt.xlim(-0.7, len(df) -0.3)

    plt.bar(x_positions - bar_width/2, df['Variação mensal'], width=bar_width, label='Valor MM', color='royalblue')
    plt.bar(x_positions + bar_width/2, df['Variação acumulada em 12 meses'], width=bar_width, label='Valor 12MM', color='orange')

    plt.xticks(ticks=x_positions, labels=[x.strftime("%b/%y") for x in df.index], size=14, color='darkslategray')
    plt.ylabel('')
    plt.yticks([])

    for index, (value_mm, value_12mm) in enumerate(zip(df['Variação mensal'], df['Variação acumulada em 12 meses'])):
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

    plt.figtext(0.01, 0.05, 'Fonte: IBGE.', fontsize=14, color='darkslategray')

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

