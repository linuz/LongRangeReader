# LongRangeReader

Modifying an HID Prox or iCLASS long range RFID reader in order to wirelessly clone badges HID badges in the field. This will work with the **Maxirpox 5375** Prox long range reader or the **HID iCLASS R90** long range reader. Work is being done to support additional readers.

Hardware Needed

  * **Long Range Reader** - Maxiprox 5375 or R90
  * **Raspberry Pi Zero W** - The brains, will interpret and decode wiegand data from reader and will provide wireless
  * **Battery Source (18650)** - Must support 3A. Can be 12V or under. Will require a boost converter if under 12V
  * **DC - DC Boost Converter** - Used to set up battery voltage to 12V if the battery source is under 12V
  * **DC - DC Buck Converter** - Used to step down voltage to 5V for powering the Raspberry Pi Zero W
  * **Wire** - Appropriate gauge for power and wiegand data
