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

Water molecules are known to absorb electromagnetic radiation over a wide range of the electromagnetic spectrum [1]. The relationship between wavelength and the
corresponding absorption coecient is shown in Figure 2.







The proposed approach exploits the characteristic infrared light absorption of water, using illumination from a simple halogen light source and image acquisition with a Raspberry Pi camera. By relying on simple optical components and image-based analysis rather than specialized instrumentation, the device provides a practical alternative for initial characterization of plant-based meat products.

## Current Results
## Future Work

## References
[1] Muncan, J., Tsenkova, R. Aquaphotomics|From Innovative Knowledge to Integrative Platform
in Science and Technology. Molecules, 24(15), 2742. https://doi.org/10.3390/molecu
les24152742 , (2019).

