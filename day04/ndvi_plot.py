import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show
import matplotlib.patheffects as pe
from matplotlib_scalebar.scalebar import ScaleBar

plt.rcParams.update(
    {
        "figure.facecolor": "black",
        "text.color": "white",
        "font.family": "monospace",
        "font.weight": "bold",
        "font.size": 18,
    }
)


with rasterio.open("northdevon_ndvi_2.tiff") as src:

    fig, ax = plt.subplots(figsize=(15, 15))
    
    #plt.style.use("dark_background")

    show((src), ax=ax, cmap="RdYlGn")

    plt.axis("off")
    ax.set_aspect("equal")
    ax.set_title(
        "North Devon - NDVI from Sentinel 2",
        loc="left",
        x=0.02,
    )
    ax.add_artist(
        ScaleBar(dx=1, color="white", box_color="black", location="lower left")
    )
    ax.text(
        0.15,
        0.01,
        "Contains OS data © Crown copyright 2022\nSentinel-2 (ESA) image courtesy of the Copernicus SciHub",
        verticalalignment="bottom",
        horizontalalignment="left",
        transform=ax.transAxes,
        color="white",
        fontsize=8,
    )

    plt.savefig("output.png", bbox_inches="tight", pad_inches=0.2)
    plt.show()
