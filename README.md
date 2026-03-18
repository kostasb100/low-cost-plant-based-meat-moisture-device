# Low-Cost Plant-Based Meat Moisture Content Measurement Device Based on Raspberry Pi 4 B, Its Camera Module 3 NoIR, and a Halogen Lamp

This repository contains work conducted at the Optics and Photonics Laboratory at Niigata University by fourth-year Electronics, Information and Communication Engineering Program student Kostas Martynas Balciunas between 2025 and 2026 for his Bachelor's thesis. The purpose of this repository is to enable students and other individuals to recreate, use and potentially improve the moisture content measurement device that was developed during this period.

## The repository includes:
- Mechanical diagrams of the developed device  
- Software and programs used for the device and its measurement data analysis  
- Electrical circuit diagrams of the developed device  
- Additional materials to assist in recreating the device and the plant-based meat used

## Guide to those seeking to recreate the device:

1) Carefully read the Aim, Theory, Current Results, and Future Work sections of this README.md file.
2) Buy the necessary materials to build the measurement device (print the 3D model of the device and assemble the electrical circuits) and prepare the plant-based meat sample (other recipes for plant-based meat samples can also be used).
3) Set up your Raspberry Pi 4 B module (it may be possible to use other Raspberry Pi microcontrollers as well) and install the necessary libraries and software (refer to Programs).
4) Recreate the electrical circuits used in the measurement device (refer to Electrical Circuit Diagrams). Make sure they work as standalone circuits before connecting them to the microcontroller.
5) 3D print and construct the case for the measurement device (refer to Mechanical Diagrams). 3D printing the device is not necessary, since 2D diagrams are provided (Mechanical Diagrams/2D diagrams), and it is possible to recreate the device using cheaper materials such as cardboard or plywood. However, it is important to note that the precision of the measurement device may suffer due to the unevenness of individual components made by hand.
6) Install the electrical circuits and the Raspberry Pi Camera Module 3 NoIR into the case of the device.
7) Prepare the plant-based meat sample for the experiments (refer to Recipe of the plant-based meat used).
8) Conduct experiments and initial image processing using the user manual provided in the User Manual and Guide section of this repository.
9) Conduct comprehensive (batch) post-experiment image processing using Programs/Other Programs/apv_calculator.py.
10) Use other programs to visualize experiment results if necessary.
11) Learn, improve, and enjoy the process. If you notice any issues or make improvements, please contact the creator of this repository (Kostas Martynas Balciunas).

## For additional information, questions or possible please contact:

Graduate of Niigata University Kostas Martynas Balciunas (kostbal55@gmail.com)

Professor Samuel Choi, Optics and Photonics Laboratory, Niigata University Samuel Choi (schoi@eng.niigat-u.ac.jp)

## Aim of this project
Interest in alternative proteins such as plant-based meats has grown in recent years, but development remains concentrated in regions like North America and Europe due to the need for expensive facilities and equipment. This limits access for developing countries and institutions with restricted budgets, potentially hindering global progress in this field.

Moisture content is a key parameter affecting the texture, taste, and overall quality of plant-based meat products and is typically measured using costly equipment such as spectrometers. This project investigates the feasibility of a low-cost, Raspberry Pi-based imaging device for non-destructive, real-time moisture measurement during product development. It also explores the use of the same device to track changes in moisture content, size, and color over time, providing insight into the sample’s optical and physical properties.

## Basic theory behind the research

Water molecules are known to absorb electromagnetic radiation (light) over a wide range of the electromagnetic spectrum [1]. The relationship between wavelength and the corresponding absorption coeffcient is shown in Figure 1.

<p align="center">
  <img src="Images/water_absorption_spectrum.jpg" width="40%">
</p>

<p align="center">
  <em>Figure 1. The water absorption spectrum.</em>
</p>

In the UV region (100 nm to 400 nm), as well as in the mid-IR (3 µm to 50 µm) and far-IR (50 µm to 1000 µm) regions, water exhibits strong absorption. In the context of food analysis, such strong absorption limits measurements to very thin samples. If light of a particular wavelength entering a sample is absorbed by water to the point that the reflected intensity is very low, it becomes difficult to detect using low-cost equipment. In contrast, water absorption in the near-infrared (NIR;0.7 um to 3 um) region is signicantly weaker. As a result, sufficient transmitted intensity can be obtained even for thicker samples, enabling non-destructive analysis of whole plant-based meat products such as hamburger patties with minimal sample preparation. 

<p align="center">
  <img src="Images/water_absorption_nir.jpg" width="40%">
</p>

<p align="center">
  <em>Figure 2. Near-infrared spectra of pure water.</em>
</p>

More than 500 water absorption bands have been identied in the wavelength range from 400 to 2500 nm [2], only four main bands, located approximately at 970, 1190, 1450, and 1940 nm, are considered to contain signicant information about water structure (moisture)(Figure 2). Among these, the absorption band at approximately 970 nm is of particular importance to this research. Although its absorbance is lower than that of the other main bands, this wavelength
is relevant because some low-cost imaging sensors, such as the Raspberry Pi Camera Module 3 NoIR, are sensitive to wavelengths up to approximately 1000 nm [10]. This suggests that it may be possible to develop a low-cost device capable of detecting changes in light absorption caused by variations in the moisture content of a sample, thereby providing a means to estimate the sample's moisture content.

## Current Results
## Future Work

## References
[1] Muncan, J., Tsenkova, R. Aquaphotomics|From Innovative Knowledge to Integrative Platform
in Science and Technology. Molecules, 24(15), 2742. https://doi.org/10.3390/molecules24152742 , (2019).
[2] Tsenkova, R., Kovacs, Z., Kubota, Y. Aquaphotomics: Near Infrared Spectroscopy and
Water States in Biological Systems. Sub-cellular biochemistry, 71, 189{211, https://doi.org/10.1007/978-3-319-19060-0_8, (2015).

