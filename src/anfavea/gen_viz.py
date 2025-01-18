import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import matplotlib.dates as mdates
import matplotlib.patches as mpatches


def viz_anfavea(df):
    # Create the figure
    data_plot = df.iloc[-12:,]

    dpi = 100
    figsize_inches = (1024 / dpi, 762 / dpi)
    fig, ax = plt.subplots(
            nrows=1,
            ncols=2,
            figsize=figsize_inches, 
            dpi=dpi
            )

    # Plot the data
    sns.barplot(data=data_plot, y=data_plot.index, x='Produção', ax=ax[0], color='royalblue')
    sns.barplot(data=data_plot, y=data_plot.index, x='Exportação', ax=ax[0], color='darkgreen')
    sns.barplot(data=data_plot, y=data_plot.index, x='Licenciamento Nacionais', ax=ax[1], color='royalblue')
    sns.barplot(data=data_plot, y=data_plot.index, x='Licenciamento Importados', ax=ax[1], color='darkgreen')

    # Remove y-axis label
    ax[0].set_ylabel('')

    # Format y-axis
    date_format = mdates.DateFormatter('%b-%y')
    for i, a in enumerate(ax):
        y_positions = range(len(data_plot.index))
        a.set_yticks(y_positions)
        a.set_yticklabels([x.strftime("%b/%y") for x in data_plot.index], size=12, color='darkslategray')
        if i > 0:
            a.tick_params(axis='y', which='both', length=0) # remove ticks
            a.set_ylabel('')

    # Remove x-axis
    for a in ax:
        a.set_xticks([])
        a.spines['bottom'].set_visible(False)

    # Add annotations
    min_x_norm = 0.08
    for i, a in enumerate(ax):
        x_min, x_max = a.get_xlim()
        y_min, y_max = a.get_ylim()
        for p in a.patches:
            width = p.get_width()
            if width > 0:
                x_norm = (p.get_x() + width - x_min) / (x_max - x_min)
                y_norm = (p.get_y() + p.get_height() / 2 - y_min) / (y_max - y_min)
                
                if x_norm < min_x_norm:
                    x_norm = min_x_norm
                
                a.text(x_norm, y_norm, f"{width/1000:,.1f}", 
                    ha='right', va='center', size=12, color='white', 
                    transform=a.transAxes)

    # Remove borders
    for a in ax:
        a.spines['top'].set_visible(False)
        a.spines['right'].set_visible(False)

    # Add title for each plot
    ax[0].set_title('Produção e Exportação', fontsize=18, fontweight='bold')
    ax[1].set_title('Licenciamentos', fontsize=18, fontweight='bold')
    ax[0].set_xlabel('')
    ax[1].set_xlabel('')

    # Add title and subtitle
    plt.text(
        x=-0.05, 
        y=1.05,  
        s="Estatísticas automobilísticas", 
        fontsize=36, 
        fontweight="bold",
        ha="left",
        transform=fig.transFigure  
    )
    plt.text(
        x=-0.05, 
        y=1.00,  
        s="em milhares de unidades. Fonte: ANFAVEA", 
        fontsize=16, 
        ha="left",
        transform=fig.transFigure  
    )

    # Add legend
    legend_handles = [
        mpatches.Patch(facecolor='royalblue', edgecolor='royalblue', label='Produção'),
        mpatches.Patch(facecolor='darkgreen', edgecolor='darkgreen', label='Exportação')
    ]
    ax[0].legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 0), ncols=1, frameon=False, prop={'size': 16})

    legend_handles = [
        mpatches.Patch(facecolor='royalblue', edgecolor='royalblue', label='Nacionais'),
        mpatches.Patch(facecolor='darkgreen', edgecolor='darkgreen', label='Importados')
    ]
    ax[1].legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 0), ncols=1, frameon=False, prop={'size': 16})

    plt.subplots_adjust(left=0.0, right=1)
    
    # Save the plot to a BytesIO object
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='jpg', bbox_inches='tight')
    img_buffer.seek(0)  # Move the cursor to the beginning of the BytesIO object

    return img_buffer