import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import adjustText
from io import BytesIO
from google.cloud import logging as gcp_logging

def chart_viz(df, name, logger: gcp_logging.Logger):
    try:
        df = df.iloc[-60:, ]
        dpi = 100
        figsize_inches = (1024 / dpi, 762 / dpi)
        fig = plt.figure(figsize=figsize_inches, dpi=dpi)
        colors = sns.color_palette('mako', n_colors=len(df.columns))

        for i, col in enumerate(df.columns):
            sns.lineplot(data=df[col], color=colors[i], linewidth=3, dashes=False, label=col)

        ax = plt.gca()
        ax.patch.set_facecolor('#f2f2f2')

        date_format = mdates.DateFormatter('%b-%Y')
        plt.gca().xaxis.set_major_formatter(date_format)

        first_index = df.index[0]
        last_index = df.index[-1]
        xticks = pd.date_range(start=first_index, end=last_index, periods=30)

        plt.xticks(xticks, [date.strftime('%b-%Y') for date in xticks], rotation=90)
        plt.xlabel('')

        plt.figtext(
            0.5, 0.99, f'{name}', ha='center',
            fontsize=26, fontweight='demibold', color='darkslategray'
        )

        plt.figtext(0.96, 0.08, 'Fonte:\nFGV-Ibre.', fontsize=12, color='darkslategray', ha='center')
        plt.ylabel('')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.tick_params(axis='both', length=0, width=0)
        ax.spines['bottom'].set_color('gray')
        plt.grid(axis='y', linestyle='--', alpha=0.5, color='gray')

        x_lim = ax.get_xlim()
        ax.set_xlim(x_lim[0], x_lim[1] + (x_lim[1] - x_lim[0]) * 0.05)

        texts = []
        for i, col in enumerate(df.columns):
            last_value = df[col].iloc[-1]
            annotation = plt.text(last_index, last_value, f'{last_value:.2f}', ha='left', va='center', color=colors[i], weight='bold')
            texts.append(annotation)

        adjustText.adjust_text(texts, ax=ax, expand=(1.2, 1.2))

        handles, labels = ax.get_legend_handles_labels()
        legend_handles = [
            Line2D([0], [0], marker='s', markersize=15, linestyle='None', color='w', markerfacecolor=colors[i], label=col)
            for i, col in enumerate(df.columns)
        ]

        plt.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=len(df.columns), frameon=False, fontsize=14)
        plt.tight_layout()
        plt.subplots_adjust(top=0.9, bottom=0.15, left=0, right=1)

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='jpg', bbox_inches='tight', dpi=dpi)
        img_buffer.seek(0)

        logger.log_text(f'{name} chart created successfully!', severity="INFO")
        return img_buffer
    
    except Exception as e:
        logger.log_text(f"Error creating chart for {name}: {str(e)}", severity="ERROR")
        raise  # Re-raise the exception if you want it to be handled by the caller, or handle it here if you don't