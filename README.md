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

## Aim
In recent years, there has been increasing interest in the development of alternative proteins, such as plant-based meats. However, most development of such products is happening in developed countries like North America and Europe. This is largely because food development and analysis often require expensive facilities and equipment, such as spectrometers, which may not be available in developing countries or educational institutions with limited budgets. This lack of access not only prevents such countries and institutions from engaging in the field but may also hinder the global advancement of alternative protein research.

Moisture content is one of the most important parameters in plant-based meat products, as it directly influences texture, taste, and overall product quality and is typically evaluated using expensive devices such as spectrometers. This project investigates the feasibility of a low-cost, Raspberry Pi-based imaging device for the non-destructive, real-time measurement of a plant-based meat sample's moisture content, which could be used during the product development phase. It also examines the feasibility of using the same device to analyze changes in the sample's moisture content, size, and color over time, thereby further providing useful information about the sample's optical and physical properties.

## Theory
The proposed approach exploits the characteristic infrared light absorption of water, using illumination from a simple halogen light source and image acquisition with a Raspberry Pi camera. By relying on simple optical components and image-based analysis rather than specialized instrumentation, the device provides a practical alternative for initial characterization of plant-based meat products.

## Current Results
## Future Work
