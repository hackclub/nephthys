import matplotlib.pyplot as plt
from numpy.typing import NDArray


def generate_pie_chart(
    y: NDArray, labels: list, colours: list, text_colour: str, bg_colour: str
):
    fig, ax = plt.subplots()
    result = ax.pie(
        y,
        labels=labels,
        colors=colours,
        autopct="%.1f%%",
        startangle=140,
        textprops=dict(color=text_colour),
    )

    texts, auto_texts = result.texts
    for text in texts:
        text.set_color(text_colour)
    for text in auto_texts:
        text.set_color("black")
        text.set_fontsize(10)

    ax.axis("equal")
    fig.patch.set_facecolor(bg_colour)

    return fig
