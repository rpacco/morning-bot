import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.lines as mlines
from matplotlib.ticker import FuncFormatter
from io import BytesIO
import numpy as np
from adjustText import adjust_text


def billions(x, pos):
    """The two args are the value and tick position"""
    return f'R${x/1e3:.1f}B'


def viz_fiscais(df, name, subtitle):
    df = df.iloc[-12:,].copy()
    df['month'] = df.index.strftime('%b/%y')
    
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)  

    # Set up the matplotlib figure
    fig, ax1 = plt.subplots(figsize=figsize_inches, dpi=dpi)

    # Create the barplot for monthly data on the first y-axis
    bars = sns.barplot(x='month', y='Monthly', data=df, color='steelblue', legend=False, alpha=0.6, ax=ax1)

    # Create a second y-axis for the TTM data
    ax2 = ax1.twinx()

    # Create the lineplot for TTM data on the second y-axis
    sns.lineplot(x='month', y='TTM', data=df, color='darkblue', marker='o', linestyle='--', legend=False, ax=ax2)

    # Rotate x-axis labels by 90 degrees
    for tick in ax1.get_xticklabels():
        tick.set_ha('center')  # Center-align the label text

    # Annotate the barplot
    texts = []
    for bar in bars.patches:
        height = bar.get_height()
        x_pos = bar.get_x() + bar.get_width() / 2
        text = ax1.text(x_pos, height, f'{height/1000:.2f}', 
                        ha='center', va= 'bottom' if height > 0 else 'top', color='steelblue', fontsize=10)
        texts.append(text)

    # Annotate the lineplot
    line_texts = []
    for i, (x, y) in enumerate(zip(df['month'], df['TTM'])):
        # Use ax2 for TTM data annotations
        text = ax2.text(i, y, f'{y/1000:.2f}', 
                        ha='center', va='bottom', fontsize=10)
        line_texts.append(text)

    # Create a smooth curve to guide the adjustment of the text labels
    x = np.linspace(0, len(df) - 1, 300)
    y = np.interp(x, range(len(df)), df['TTM'])

    # Adjust lineplot annotations to avoid overlap
    adjust_text(line_texts, x=x, y=y)

    # Manually add y-axis labels at the top
    ax1.yaxis.label.set_visible(False)  # Hide default label
    ax1.xaxis.label.set_visible(False)
    ax2.yaxis.label.set_visible(False)  # Hide default label

    # Add custom labels at the top
    ax1.text(0, 1.0, 'Último mês\n', transform=ax1.transAxes, ha='right', va='center', color='steelblue', fontsize=14)
    ax2.text(1, 1.0, 'Acumulado\n12 meses\n', transform=ax2.transAxes, ha='left', va='center', color='darkblue', fontsize=14)

    # Setting the ticks color to match the plot
    ax1.tick_params(axis='y', labelcolor='steelblue', labelsize=14)
    ax2.tick_params(axis='y', labelcolor='darkblue', labelsize=14)
    ax1.tick_params(axis='x', labelsize=14, rotation=30)
    ax2.tick_params(axis='x', labelsize=14, rotation=30)

    # Format y-axis labels as currency in billions
    formatter = FuncFormatter(billions)
    ax1.yaxis.set_major_formatter(formatter)
    ax2.yaxis.set_major_formatter(formatter)

    # Adjust tick locations for clarity (optional)
    ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # Remove borders
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # Add title and subtitle
    plt.text(
        x=-0.1, 
        y=1.2,  
        s=f"{name}", 
        fontsize=40, 
        fontweight="bold",
        ha="left",
        transform=plt.gca().transAxes  
    )
    plt.text(
        x=-0.1, 
        y=1.13,  
        s=f"{subtitle}. Fonte: BCB", 
        fontsize=18, 
        ha="left",
        transform=plt.gca().transAxes  
    )

    legend_handles = [
        mlines.Line2D([], [], marker='s', markersize=15, linestyle='None', color='w', alpha=0.6, markerfacecolor='steelblue', label='Mensal'),
        mlines.Line2D([], [], marker='o', markersize=8, linestyle='--', color='darkblue', markerfacecolor='darkblue', label='Acumulado 12 meses')
    ]

    plt.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=2, frameon=False, prop={'size': 16})

    # Show the plot
    plt.tight_layout()

    # plt.savefig(f'{name}.jpg', dpi=dpi, bbox_inches='tight')
    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)  # Move the cursor to the beginning of the BytesIO object

    # Return the BytesIO object
    return img_buffer


def viz_pct(df, name, subtitle):
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)
    fig = plt.figure(figsize=figsize_inches, dpi=dpi)

    df = df.iloc[-13:,]

    bar_width = 0.4
    x_positions = np.arange(len(df))
    plt.xlim(-0.7, len(df) -0.3)

    plt.bar(x_positions - bar_width/2, df['MoM'], width=bar_width, label='Valor MM', color='royalblue')
    plt.bar(x_positions + bar_width/2, df['YoY'], width=bar_width, label='Valor 12MM', color='orange')

    plt.xticks(ticks=x_positions, labels=[x.strftime("%b/%y") for x in df.index], size=14, color='darkslategray')
    plt.ylabel('')
    plt.yticks([])
    plt.tick_params(axis='x', length=0, width=0)

    for index, (value_mm, value_12mm) in enumerate(zip(df['MoM'], df['YoY'])):
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
        s=f"{subtitle}. Fonte: BCB", 
        fontsize=16, 
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


def viz_cambio(df, name, subtitle):
    last_date = df.index[-1].date().strftime('%d/%m/%Y')
    data = df.resample('ME').sum().iloc[-13:].reset_index()
    data.columns = ['date', 'valor']

    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)
    fig, ax = plt.subplots(figsize=figsize_inches, dpi=dpi)
    fig.patch.set_facecolor('#F7F7F7')

    sns.barplot(data=data, x='date', y='valor', hue='date', 
                palette=['firebrick' if x < 0 else 'mediumblue' for x in data['valor']], 
                legend=False, ax=ax)

    ax.set_frame_on(False)
    ax.set_xticks(range(len(data['date'])))
    ax.set_xticklabels(data['date'].dt.strftime('%b/%y'), ha='center', fontdict={'size':12})
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='x', which='both', length=0)
    ax.get_yaxis().set_visible(False)

    # Annotate bars
    for bar in ax.patches:
        height = bar.get_height()
        if height >= 0:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', 
                    ha='center', va='bottom', color='black', fontsize=13)
        else:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', 
                    ha='center', va='top', color='black', fontsize=13)
            
    ax.text(
        x=0.03,
        y=1.05,
        s=f"{name}", 
        fontsize=32, 
        fontweight="bold",
        ha="left",
        transform=ax.transAxes
    )
    ax.text(
        x=0.03, 
        y=1.01,
        s=f"acumulado até {last_date} {subtitle}. Fonte: BCB", 
        fontsize=12, 
        alpha=0.75,
        ha="left",
        transform=ax.transAxes
    )

    plt.tight_layout()
    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)  # Move the cursor to the beginning of the BytesIO object

    # Return the BytesIO object
    return img_buffer


def viz_externo(df, name, subtitle):
    df = df.iloc[-24:,].copy()
    df['month'] = df.index.strftime('%b/%y')
    
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)  

    # Set up the matplotlib figure
    fig, ax1 = plt.subplots(figsize=figsize_inches, dpi=dpi)

    # Adjust the plot margins to use all available space
    plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.2)

    # Create the barplot for monthly data with adjusted width
    palette = ['firebrick' if x < 0 else 'mediumblue' for x in df['MoM']]
    bars = sns.barplot(x='month', y='MoM', data=df, palette=palette, legend=False, ax=ax1)

    # Adjust bar width to occupy more space horizontally
    for bar in bars.patches:
        bar.set_width(0.85)  # Width of each bar, adjust as needed (0 to 1)

    # Define tolerance for considering a value as zero
    tolerance = 1e1

    # Annotate the barplot, handling zero explicitly with tolerance
    for bar in bars.patches:
        height = bar.get_height()
        x_pos = bar.get_x() + bar.get_width() / 2
        
        if abs(height) < tolerance:  # Check if height is effectively zero
            formatted_height = '0.00'
        else:
            formatted_height = f'{height/1000:.2f}'
        
        ax1.text(x_pos, height, formatted_height, 
                 ha='center', va='bottom' if height >= 0 else 'top', color='black', fontsize=11, fontweight='bold')

    # Remove y-axis labels and ticks, and adjust plot to use the space
    ax1.yaxis.set_visible(False)
    ax1.set_ylabel('', labelpad=-50)  # This pushes the plot to the left

    # Rotate x-axis labels by 30 degrees
    for tick in ax1.get_xticklabels():
        tick.set_rotation(30)
        tick.set_ha('center')  # Center-align the label text
        tick.set_fontsize(12)  # Increase the font size of xticklabels

    # Adjust x-axis to start at the first bar
    ax1.set_xlim(-0.5, len(df) - 0.5)
    ax1.set_xlabel('')

    # Add title and subtitle
    plt.text(
        x=0.0, 
        y=1.2,  
        s=f"{name}", 
        fontsize=40, 
        fontweight="bold",
        ha="left",
        transform=plt.gca().transAxes  
    )
    plt.text(
        x=0.0, 
        y=1.13,  
        s=f"{subtitle}. Fonte: BCB", 
        fontsize=18, 
        ha="left",
        transform=plt.gca().transAxes  
    )

    # Remove borders
    for spine in ax1.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)  # Move the cursor to the beginning of the BytesIO object

    # Return the BytesIO object
    return img_buffer