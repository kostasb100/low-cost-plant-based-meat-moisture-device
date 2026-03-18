Below is an explanation of each component that the measurement device consists of. It is recommended to 3D print the components and assemble them in numerical order.
Some components may not be fully optimized, and their parameters may require further adjustment.

Every component was printed using a Creality K1 3D printer and black 1.75~mm diameter PLA filament (Creality Ender, 3D PLA BLACK 1.75~mm) and assembled using screws or adhesive.

## Camera stand components of the measurement device (CS1-CS7)
CS1: Component that serves as the main base of the device. The two holes in the middle are used for S2. The small hole at the bottom of the wall is used to pass through the wires of the load cell to the HX711 weight scale module.

CS2 and CS3: Components used to protect the sample inside the measurement device from outside light. CS3 has a hole in the wall so that the lamp stand can be placed at an angle.

CS4 and CS5: Components used as the stand for the Raspberry Pi Camera Module 3 NoIR, which is inserted using component CS6. The two holes at the sides of the camera opening are used for LEDs. These holes can be covered using two CS5 components.

CS6: Component onto which the camera can be screwed.

CS7: Component that can be glued to the surface of CS4 and is used to stabilize the camera stand with screws (two of these components are needed).

## Lamp stand components of the measurement device (L1-L10)

L1: The base component onto which the lamp stand is built. It has multiple evenly spaced cavities into which infrared transmittance filter frames, Fresnel lens frames, and the light source circuit can be inserted.

L2 and L3: Components used as walls for L1. The holes are used for CS7.

L4: Component that serves as the back wall of the lamp stand and can be slid in and out. The small hole at the bottom is used to pass through wires used to drive the lamp source (positive and negative of the 4.8 V power supply, and a wire for the GPIO pin that turns the logic MOSFET on).

L5: Cover lid component of the lamp stand, which can be easily placed and removed.

L6 and L9: Components used to make the Fresnel lens frame. “Frame” here refers to a component made by attaching L6 to L9 (or L7 to L10) in such a way that an optical component, such as a disk, can be inserted into it. This frame is then inserted into L1 at the distance desired by the user.

L7 and L10: Components used to make the infrared transmittance lens frame. The concept is the same as explained for L6 and L9.

L8: Plate onto which the infrared light source is screwed. The hole in the middle is sized to fit a plastic cap from a plastic PET bottle.

## Base components of the measurement device (B1-B4)
B1: Component into which the HX711 module breadboard circuit was placed. The hole on the right side of the wall was used to pass through wires used to power the module, the halogen lamp, and the LEDs through the Raspberry Pi 4B pins. Fours holes at the back are used to connect B1 to a hinge, allowing B2, B3, and B4, along with some of the camera stand components, to be moved in a rotational direction.

B2: Component used to connect B1 to a hinge and to B3 and B4.

B3: Component used to hold the Raspberry Pi 4 B microcontroller. The holes at the bottom of the plate are used to pass through wires to B1 and to pass the ribbon cable of the Raspberry Pi Camera Module 3 NoIR. The hole on the right side is used to pass through the power supply and monitor cables to the Raspberry Pi 4 B microcontroller.

B4: Component used as a lid for B3.

## Scale components of the measurement device (S1-S6)
S1 and S2: S1 is the upper plate of the scale. It is meant to be screwed onto the load cell, the other end of which should be screwed into S2 and connected to the camera stand (CS) plate CS1.

S3: A component that is connected to the screw holes at both ends of S1 (one component for the left side and one for the right side). It is used to hold the plastic cover sheet placed on top of the plant-based meat sample.

S4 and S5: Components that are to be inserted into S3 with the goal of adjusting the height of the plastic cover sheet.

S6: A component that is connected to S1 and used as a stand onto which the plant-based sample should be placed in order to dry mostly through the bottom surface.
