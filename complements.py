import numpy as np
import streamlit as st
import plotly.express as px
from colour import SpectralShape, sd_blackbody, sd_to_XYZ, XYZ_to_xy
from colour.colorimetry import STANDARD_OBSERVERS_CMFS

# Wavelengths for visible spectrum
wavelengths = np.arange(380, 781, 5)

# Load standard observer CMFs
cmfs = STANDARD_OBSERVERS_CMFS["CIE 1931 2 Degree Standard Observer"].copy()
cmfs = cmfs.align(SpectralShape(380, 780, 5))

# Function to compute complementarity matrix
def compute_complement_map(white_temp):
    spd_white = sd_blackbody(white_temp, wavelengths)
    white_XYZ = sd_to_XYZ(spd_white, cmfs)
    white_xy = XYZ_to_xy(white_XYZ)

    complement_map = np.zeros((len(wavelengths), len(wavelengths)))

    for i, wl1 in enumerate(wavelengths):
        spd1 = np.zeros_like(wavelengths)
        spd1[i] = 1
        XYZ1 = sd_to_XYZ(dict(zip(wavelengths, spd1)), cmfs)

        for j, wl2 in enumerate(wavelengths):
            spd2 = np.zeros_like(wavelengths)
            spd2[j] = 1
            XYZ2 = sd_to_XYZ(dict(zip(wavelengths, spd2)), cmfs)

            mixed = XYZ1 + XYZ2
            mixed_xy = XYZ_to_xy(mixed)
            distance = np.linalg.norm(mixed_xy - white_xy)
            complement_map[i, j] = distance

    return complement_map

# Streamlit UI
st.title("Complementary Wavelength Explorer")
st.markdown("""
Adjust the white point temperature (in Kelvin) along the Planckian locus to see how it affects 
which pairs of monochromatic wavelengths combine to approximate white.
""")

white_temp = st.slider("White Point Temperature (K)", min_value=2000, max_value=10000, value=6500, step=100)
complement_data = compute_complement_map(white_temp)

# Convert matrix to long-form DataFrame for Plotly heatmap
import pandas as pd
heatmap_df = pd.DataFrame(complement_data, index=wavelengths, columns=wavelengths)
heatmap_long = heatmap_df.reset_index().melt(id_vars="index")
heatmap_long.columns = ["Wavelength 1 (nm)", "Wavelength 2 (nm)", "Distance"]

# Plot with Plotly
fig = px.imshow(
    complement_data,
    labels=dict(x="Wavelength 1 (nm)", y="Wavelength 2 (nm)", color="Distance from White"),
    x=wavelengths,
    y=wavelengths[::-1],  # Flip y-axis for visual parity
    color_continuous_scale="Viridis"
)
fig.update_layout(title=f"Complementarity Map at {white_temp}K")

st.plotly_chart(fig, use_container_width=True)
