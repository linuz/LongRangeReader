#!/usr/bin/python
#############################################################################
# Long Range Reader Wiegand Listener/Decoder
# By: Dennis Linuz <dennismald@gmail.com>
#
#
#############################################################################

import pigpio

# The magic code to decode wiegand data from the wiegand data lines. Borrowed from http://abyz.co.uk/rpi/pigpio/examples.html
class decoder:
    def __init__(self, pi, gpio_0, gpio_1, callback, bit_timeout=5):
        """
        Instantiate with the pi, gpio for 0 (green wire), the gpio for 1
        (white wire), the callback function, and the bit timeout in
        milliseconds which indicates the end of a code.

        The callback is passed the code length in bits and the value.
        """

        self.pi = pi
        self.gpio_0 = gpio_0
        self.gpio_1 = gpio_1

        self.callback = callback

        self.bit_timeout = bit_timeout

        self.in_code = False

        self.pi.set_mode(gpio_0, pigpio.INPUT)
        self.pi.set_mode(gpio_1, pigpio.INPUT)

        self.pi.set_pull_up_down(gpio_0, pigpio.PUD_UP)
        self.pi.set_pull_up_down(gpio_1, pigpio.PUD_UP)

        self.cb_0 = self.pi.callback(gpio_0, pigpio.FALLING_EDGE, self._cb)
        self.cb_1 = self.pi.callback(gpio_1, pigpio.FALLING_EDGE, self._cb)

    def _cb(self, gpio, level, tick):
        """
        Accumulate bits until both gpios 0 and 1 timeout.
        """

        if level < pigpio.TIMEOUT:
            if self.in_code == False:
                self.bits = 1
                self.num = 0

                self.in_code = True
                self.code_timeout = 0
                self.pi.set_watchdog(self.gpio_0, self.bit_timeout)
                self.pi.set_watchdog(self.gpio_1, self.bit_timeout)
            else:
                self.bits += 1
                self.num = self.num << 1

            if gpio == self.gpio_0:
                self.code_timeout = self.code_timeout & 2  # clear gpio 0 timeout
            else:
                self.code_timeout = self.code_timeout & 1  # clear gpio 1 timeout
                self.num = self.num | 1

        else:
            if self.in_code:
                if gpio == self.gpio_0:
                    self.code_timeout = self.code_timeout | 1  # timeout gpio 0
                else:
                    self.code_timeout = self.code_timeout | 2  # timeout gpio 1
                if self.code_timeout == 3:  # both gpios timed out
                    self.pi.set_watchdog(self.gpio_0, 0)
                    self.pi.set_watchdog(self.gpio_1, 0)
                    self.in_code = False
                    self.callback(self.bits, self.num)

    def cancel(self):
        """
        Cancel the Wiegand decoder.
        """

        self.cb_0.cancel()
        self.cb_1.cancel()


if __name__ == "__main__":
    import time
    import pigpio
    import lrr_wiegand_listener
    import os
    import csv

    print "Starting Wiegand listener..."

    CARDS_CSV_FILE = "cards.csv"
    id_num = 0

    # Command for using expect script on sattilite device to automagically write cloned RFID cards
    # Currently broken, will hang up the script, not allowing for more than 2 cards to be processed at any one time
    def cmdProxmark(wiegand_hex):
        os.system('ssh -t dennis@192.168.3.10 "/home/dennis/proxmark.exp /dev/ttyACM0 lf ' + wiegand_hex + '"')

    # Creates CSV file if one doesn't exist. Will also grab the ID of the last record
    def validateCSV(file):
        global id_num
        if not os.path.exists(file):
            print "[!] No cards.csv found! Creating one..."
            with open(file, 'w') as csvfile:
                fieldnames = ['id', 'bit_length', 'wiegand_binary', 'wiegand_hex', 'iclass_std_enc_hex', 'fac_code',
                              'card_num', 'card_num_no_fac']
                csvwriter = csv.DictWriter(csvfile, lineterminator='\n', fieldnames=fieldnames)
                csvwriter.writeheader()
            print "[*] cards.csv created!"
        else:
            with open(file, 'r') as csvfile:
                if not ("wiegand_binary" in csvfile.readline()):
                    print "[!] Invalid CSV file!"
                    quit()
        # Get ID of last record
        with open(file, 'r') as csvfile:
            for lastrow in csv.reader(csvfile): pass
            id_num = lastrow[0]
            if not (id_num.isdigit()):
                id_num = 0


    # Add scanned cards to CSV file
    def addCardsToCSV(bits, wiegand_binary, wiegand_hex, enc_hex, fac_code, card_num, card_num_no_fac):
        global id_num
        if fac_code == "-1": fac_code = "NA"
        if card_num == "-1": card_num = "NA"
        if card_num_no_fac == "-1": card_num_no_fac = "NA"
        validateCSV(CARDS_CSV_FILE)
        id_num = int(id_num) + 1
        with open(CARDS_CSV_FILE, 'a+') as csvfile:
            csvwriter = csv.writer(csvfile, lineterminator='\n')
            csvwriter.writerow(
                [id_num, bits, wiegand_binary, wiegand_hex, enc_hex, fac_code, card_num, card_num_no_fac])
        os.system("sync")
        print "[*] Added to cards.csv"

    # Decodes the wiegand data based on the bitlength (bits)
    def decodeWiegandData(bits, wiegand):
        if bits == "26":
            head = "0000000100000000001"
            fc = int(wiegand[1:9], 2)
            cn = int(wiegand[9:25], 2)
            cn2 = int(wiegand[1:25], 2)
        elif bits == "35":
            head = "0000000101"
            fc = int(wiegand[2:14], 2)
            cn = int(wiegand[14:34], 2)
            cn2 = int(wiegand[2:34], 2)
        elif bits == "37":
            head = "00000000"
            fc = int(wiegand[1:17], 2)
            cn = int(wiegand[17:36], 2)
            cn2 = int(wiegand[1:36], 2)
        else:
            head = "0"
            fc = -1
            cn = -1
            cn2 = -1
        return str(fc), str(cn), str(cn2), str(head)

    # The actual code that runs every time a card is scanned. Grabs data from, formats it appropriately, and writes to CSV file as well as prints the output to console
    def callback(bits, value):
        bits = str(bits)
        wiegand_binary = format(value, '0' + bits + 'b')
        fac_code, card_num, card_num_no_fac, hidHeader = decodeWiegandData(bits, wiegand_binary)
        wiegand_binary = hidHeader + wiegand_binary
        wiegand_hex = "%016X" % int(wiegand_binary, 2)
        enc_hex = "FFFFFFFFFFFFFFFF".upper()  # To Implement
        addCardsToCSV(bits, wiegand_binary, wiegand_hex, enc_hex, fac_code, card_num, card_num_no_fac)

        # Debug output to console
        print "Bit Length: " + bits
        print "Facility Code: " + fac_code
        
        print "Card Number: " + card_num
        print "Card Number without Facility Code: " + card_num_no_fac
        print "Wiegand Data: " + wiegand_binary
        print "Wiegand Hex Data: " + wiegand_hex
        print "iCLASS Standard Encrypted Hex Data: " + enc_hex
 #      cmdProxmark(wiegand_hex)

    # Initialize pigpio and start the wiegand decoder, listening for Data0 and Data1 on pins 14 and 15, respectively
    pi = pigpio.pi()
    w = lrr_wiegand_listener.decoder(pi, 14, 15, callback)
    
    # Keep the script running until it is manually stopped with Control+C or killed
    while True:
        raw_input()
    w.cancel()
    pi.stop()
    