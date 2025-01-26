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
    df = df.iloc[-13:].copy()
    df['month'] = df.index.strftime('%b/%y')
    
    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)  

    fig, axs = plt.subplots(2, 1, figsize=figsize_inches, dpi=dpi, sharex=True)

    # Definir as colunas de interesse
    mom_cols = [col for col in df.columns if col.startswith('MoM_')]
    yoy_cols = [col for col in df.columns if col.startswith('YoY_')]
    
    # Definir os dataframes para cada tipo de dado
    mom_df = df[mom_cols + ['month']]
    yoy_df = df[yoy_cols + ['month']]

    # Definir as colunas primárias e de juros
    x_prim_mom = mom_cols[0]
    x_int_mom = mom_cols[1] if len(mom_cols) > 1 else None
    x_prim_yoy = yoy_cols[0]
    x_int_yoy = yoy_cols[1] if len(yoy_cols) > 1 else None

    # Configurar o título e subtítulo do gráfico
    fig.text(0.0, 1.2, name, fontsize=24, fontweight="bold")
    fig.text(0.0, 1.15, f"{subtitle}. Fonte: BCB", fontsize=14)

    # Função para plotar os gráficos
    def plot_graph(ax, df, x_prim, x_int, title):
        ax.set_title(title, fontsize=18)
        
        if x_int:
            sns.barplot(x='month', y=x_prim, data=df, ax=ax, bottom=0, color='skyblue', label='Resultado primário')
            
            bottom_int = pd.Series(np.where(df[x_prim] > 0, 0, df[x_prim]), index=df.index)
            sns.barplot(x='month', y=x_int, data=df, ax=ax, bottom=bottom_int, color='salmon', label='Juros nominais')
        else:
            sns.barplot(x='month', y=x_prim, data=df, ax=ax, bottom=0, color='skyblue', label='Resultado primário')
        
        ax.get_yaxis().set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.tick_params(axis='x', which='both', length=0)
        ax.tick_params(axis='y', which='both', length=0)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        # Adicionar anotações
        for i, month in enumerate(df['month']):
            y_pos_prim = df[x_prim].iloc[i]
            if abs(y_pos_prim) > 10.0:
                ax.text(i, y_pos_prim, f"{y_pos_prim:.1f}Bi", ha='center', va='bottom', color='black', fontsize=11)
            else:
                ax.text(i, 0, f"{y_pos_prim:.1f}Bi", ha='center', va='bottom' if y_pos_prim > 0 else 'top', color='black', fontsize=11)
            
            if x_int:
                y_pos_int = bottom_int.iloc[i] + df[x_int].iloc[i]
                if abs(df[x_int].iloc[i]) > 10.0:
                    ax.text(i, y_pos_int, f"{df[x_int].iloc[i]:.1f}Bi", ha='center', va='bottom', color='black', fontsize=11)
                else:
                    ax.text(i, 0, f"{df[x_int].iloc[i]:.1f}Bi", ha='center', va='bottom' if df[x_int].iloc[i] > 0 else 'top', color='black', fontsize=11)
        
        return ax

    # Plotar os gráficos
    axs[0] = plot_graph(axs[0], mom_df, x_prim_mom, x_int_mom, 'Mensal')
    axs[1] = plot_graph(axs[1], yoy_df, x_prim_yoy, x_int_yoy, 'Acumulado 12 meses')
    axs[0].legend(loc='lower left', bbox_to_anchor=(0, 1.15), ncol=2, frameon=False, fontsize=12)
    
    # Configurar o eixo x do segundo gráfico
    axs[1].set_xticks(range(len(mom_df)))
    axs[1].set_xticklabels(mom_df['month'], fontsize=12)
    axs[1].set_xlabel('')
    axs[1].legend_ = None
    
    # Ajustar o layout do gráfico
    plt.subplots_adjust(left=0, right=1, bottom=0.1, top=1)

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