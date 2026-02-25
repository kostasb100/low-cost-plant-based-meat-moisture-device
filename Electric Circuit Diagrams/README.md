# Description of the Developed Moisture Measurement Device Circuit

## The circuit consists of the following main parts:
1) Raspberry Pi 4 Model B microcontroller
2) Halogen lamp drive circuit
3) LED illumination circuits (2 circuits)
4) Load cell and its AD converter circuit

## Below are the detailed explanations of these parts:

1) The microcontroller is powered by a 5 V / 3 A DC power supply. It can also be powered by a power bank (mobile battery) with the same specifications.

2) One pin of the 4.8 V / 2.4 A halogen lamp LA1 (National, Halogen Miniature Lamp MB-48M5H, https://www.monotaro.com/p/5776/7265/) is connected to a DC power supply set to 4.8 V. The other pin is connected to the drain pin of an N-channel MOSFET Q1 (IRLB8721PbF, International Rectifier, https://akizukidenshi.com/catalog/g/g106024/), which acts as a voltage switch powered by a HIGH (3.3 V) signal delivered from GPIO4. R1 (100 ohm) is a gate resistor that controls the switching speed of the MOSFET. R2 (10 k ohm) is a gate-source resistor used to ensure that the MOSFET remains turned off (gate-source voltage set to 0 V) when no signal is applied to the gate pin. When no voltage is applied to the gate pin, the MOSFET behaves as an open circuit. When a 3.3 V signal is applied, it allows drain current to flow from drain to source (ground), thereby turning on the halogen lamp.

3) Two white LEDs are each connected in series with 220 ohm resistors (R3, R4) to limit the current flow. They are connected to pins GPIO07 and GPIO08 so that they can be controlled by the microcontroller.

4) A 500 g micro type load cell U2 (SC616C, Sensorcon, https://akizukidenshi.com/catalog/g/g112532/) is connected to an AD converter U1 (AE-HX711-SIP, https://akizukidenshi.com/catalog/g/g112370/), which is based on an HX711 chip. The VDD pin of the AD converter is connected to a 5 V power supply. Its DAT pin is connected to a voltage divider circuit consisting of R5 (20 k ohms) and R6 (10 k ohms) so that only a 3.33 V signal is delivered to the GPIO17 pin (without this, the signal would reach 5 V and potentially damage the microcontroller). The CLK pin is connected to GPIO27. The analog signal (changes in resistance of the load cell) is delivered from the load cell to the AD converter, which converts this signal into a digital signal. The digital signal is then processed by the microcontroller, which outputs a weight measurement.

