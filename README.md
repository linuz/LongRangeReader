# Long Range Reader

Modifying an HID Prox or iCLASS long range RFID reader in order to wirelessly clone badges HID badges in the field. This will work with the **Maxirpox 5375** Prox long range reader or the **HID iCLASS R90** long range reader. Work is being done to support additional readers.

Hardware Needed

  * **Long Range Reader** - Maxiprox 5375 or R90
  * **Raspberry Pi Zero W** - The brains, will interpret and decode wiegand data from reader and will provide wireless
  * **Battery Source (18650)** - Must support 3A. Can be 12V or under. Will require a boost converter if under 12V
  * **DC - DC Boost Converter** - Used to set up battery voltage to 12V if the battery source is under 12V
  * **DC - DC Buck Converter** - Used to step down voltage to 5V for powering the Raspberry Pi Zero W
  * **Wire** - Appropriate gauge for power and wiegand data

## Raspberry Pi Setup
  * Install Raspbian Lite on the Raspberry Pi Zero W
  * Run the ./setup.sh script from this project **as root**

## Hardware Setup
  * Connect battery source to DC Boost Converter, stepping up voltage to 12V DC
  * Connect DC Boost Converter output to long range reader Power and Ground (Refer to the reader's manual for information on where to plug the cables into the reader)
  * Connect the DC Buck Converter into the Boost Converter output, stepping down voltage to 5V DC
  * Connect Raspberry Pi Zero W to Buck Converter output. (**5V to Pin 02**, **Ground to Pin 06**)
  * Connect Weigand data cables from Long Range Reader to Raspberry Pi (**Data0 to Pin 8** (GPIO 14), **Data1 to Pin 10** (GPIO 15)
  
  ![Pin Out](https://www.element14.com/community/servlet/JiveServlet/previewBody/73950-102-11-339300/pi3_gpio.png)
  
  ## How to Use
  Once the hardware and software is set up, power on the long range reader. The Raspberry Pi should boot up and automatically set up a wireless network in AP mode named **LongRangeReader**. Connect to the WIFI network with a laptop or a phone using the details provided below. Visit the web page **http://192.168.3.1**. Any RFID cards scanned with the reader should automatically populate on the list hosted on the web page.

###  WIFI Details
    SSID: LongRangeReader
    WPA Key: accessgranted
    IP Address of LongRangeReader: 192.168.3.1
    
### Web page details
    http://192.168.3.1
   
