Description of the Developed Moisture Measurement Device Circuit

The circuit consists of the following main parts:
1) Raspberry Pi 4 Model B microcontroller
2) Halogen lamp drive circuit
3) LED illumination circuits (2 circuits)
4) Load cell and its AD converter circuit

Below are the detailed explanations of these parts:

1) The microcontroller is powered by a 5 V / 3 A DC power supply. It can also be powered by a power bank (mobile battery) with the same specifications.

2) One pin of the  4.8V/2.4A halogen lamp (National, Halogen Miniature Lamp MB-48M5H, https://www.monotaro.com/p/5776/7265/) is connected to a 
DC power supply set to 4.8V.

3) Two white LEDs are connected separately to 220 ohm resistors to reduce current flow and to pins GPIO07 and GPIO08, so that they
can be controlled by a microcontroller.

4) A 500 g micro type load cell U2 (SC616C, Sensorcon, https://akizukidenshi.com/catalog/g/g112532/) is connected to an AD converter U1
(AE-HX711-SIP, https://akizukidenshi.com/catalog/g/g112370/) which is based on a HX711 chip.
