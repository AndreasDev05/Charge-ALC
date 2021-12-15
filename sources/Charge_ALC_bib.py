# import time

import serial
import serial.tools.list_ports
import serial.tools.list_ports_common
import serial.tools.list_ports_windows
from serial.serialutil import PARITY_EVEN, Timeout

from simpleHelpFunc import transByArToEscByAr, transEscByArToClearByAr

# import locale
# locale.setlocale(locale.LC_ALL, 'de_DE')


def trans_accu_num_to_str(accu_number: bytes):
    """ Gibt den ausgeschriebenen Akkutyp zurück

    Der übergebene Bytewert wird in ein String umgesetzt
    """
    accu_typs_str = ["NiCd", "NiMH", "Li-Ion", "LiPo", "Pb", "LiFePO", "N/A"]
    if accu_number < 6:
        return accu_typs_str[accu_number]
    else:
        return accu_typs_str[6]


class charge_devices_alc_generic():

    charge_channels = 0
    accu_db_items = 0x27

    def __init__(self, ser_port):
        self.__sw_version: str = str()
        self.__type_long: str = str()
        self.__type_short: str = str()
        self.__serial_number: str = str()

        self.__temp_main_float: float = float()
        self.__temp_accu_float: float = float()
        self.__temp_power_sup_float: float =float()
        self.__charge_port = serial.Serial(ser_port, 38400, 8, PARITY_EVEN, 1, 3)
        # TODO: Expliziete Übergabe der Schnittstellenparameter, für eine unverselle Funktion
    #    print(type(self.__chargePort))

    def pull_ver_ser_num(self):
        temp_byte_array: bytearray
        charge_instr = bytearray([0x75])

        self.__charge_port.write(transByArToEscByAr(charge_instr))

        temp_byte_array = self.__charge_port.read_until(b'\x03', 50)
        temp_byte_array = transEscByArToClearByAr(temp_byte_array)
        return temp_byte_array

    def pull_temperatures(self):
        temp_byte_array: bytearray
        charge_instr = bytearray([0x74])

        self.__charge_port.write(transByArToEscByAr(charge_instr))

        temp_byte_array = self.__charge_port.read_until(b'\x03', 50)
        temp_byte_array = transEscByArToClearByAr(temp_byte_array)
        return temp_byte_array

    def set_ver_ser_num(self, ser_num_raw: bytearray):
        long_alc_typ = {98: "ALC 8500 Firmware < 2.00", 99: "ALC 8000 Firmware < 2.00",
                      100: "ALC 8500-2 Firmware < 2.00", 101: "ALC 8000 PLUS Firmware < 2.00", 102: "ALC 5000 mobile Firmware < 2.00",
                      103: "ALC 3000 PC Firmware > 2.00", 104: "ALC 8500-2 Firmware > 2.00", 105: "ALC 8000 Firmware > 2.00",
                      106: "ALC 5000 mobil Firmware > 2.00"}

        short_alc_typ = {98: "ALC8500", 99: "ALC8000", 100: "ALC8500-2", 101: "ALC8000PLUS",
                       102: "ALC5000mobile", 103: "ALC3000PC", 104: "ALC8500-2", 105: "ALC8000", 106: "ALC5000mobil"}

        temp_string = ser_num_raw[6:10]
        self.__sw_version = temp_string.decode()
        self.__type_long = long_alc_typ[ser_num_raw[1]]
        self.__type_short = short_alc_typ[ser_num_raw[1]]

        temp_string = ser_num_raw[12:22]
        self.__serial_number = temp_string.decode()

    def set_temperatures(self, temperatures_raw: bytearray):

        temp_temp_int = temperatures_raw[1] * 256 + temperatures_raw[2]
        if temp_temp_int == 0xABE0:
            self.__temp_accu_float = None
        else:
            self.__temp_accu_float = float(temp_temp_int / 100)
        # TODO: Negative Temperaturen berechnen

        temp_temp_int = temperatures_raw[3] * 256 + temperatures_raw[4]
        if temp_temp_int == 0xABE0:
            self.__temp_power_sup_float = None
        else:
            self.__temp_power_sup_float = float(temp_temp_int / 100)
        # TODO: Negative Temperaturen berechnen

        temp_temp_int = temperatures_raw[5] * 256 + temperatures_raw[6]
        self.__temp_main_float = float(temp_temp_int / 100)

    def get_ser_num(self):
        return self.__serial_number

    def get_device_type_long(self):
        return self.__type_long

    def get_device_type_short(self):
        return self.__type_short

    def get_device_sw_version(self):
        return self.__sw_version

    def get_charge_port(self):
        return self.__charge_port

    def get_main_temperature(self):
        """Temperatur des Sytems.

        Gibt die Temperatur des Systems /Kühlkörper in °C als float zurück.
        """
        return self.__temp_main_float

    def get_accu_temperature(self):
        """Temperatur des Akkus.

        Gibt die Temperatur des Akkus in °C als float zurück.
        Wenn kein Sensor angeschlossen ist gibt die Funktion "None" zurück.
        """
        return self.__temp_accu_float

    def get_power_sup_temperature(self):
        """Temperatur des Netzteils.

        Gibt die Temperatur des Netzteils in °C als float zurück.
        Wenn kein Sensor angeschlossen ist gibt die Funktion "None" zurück.
        """
        return self.__temp_power_sup_float


class ChargeDeviceALC3000(charge_devices_alc_generic):

    chargeCannel = 1

    def __init__(self, ser_port):
        charge_devices_alc_generic.__init__(self, ser_port)

        self.chargeCannelIns: list = list()
        self.chargeDbEntry: list = list()
        for i in range(1, self.chargeCannel):
            self.chargeCannelIns[i] = Charge_device_alc_channel(self.__charge_port, i-1)
            self.chargeCannelIns[i].pullCurrentCannelData()
            self.chargeCannelIns[i].pullCurrentMeasuredValues()

        for i in range(self.accu_db_items):
            self.chargeDbEntry[i] = ChargeDeviceAccuDbEntry(self.__charge_port, i)
            self.chargeDbEntry[i].pulldbEntry()


class Charge_device_alc_channel():

    def __init__(self, chargePort: serial.Serial, channelNumber):

        self.__accu_number: bytes = bytes()
        self.__accu_type: bytes = bytes()
        self.__accu_type_description: str = str()
        self.ser_port = chargePort
        self.__chargePort = chargePort
        self.__channelNumber = channelNumber

    def pullCurrentCannelData(self):
        temp_ByteArray : bytearray
        #self.__chargePort = serial.Serial(self.ser_port, 38400, 8, PARITY_EVEN, 1, 3)
        channelInstr = bytearray([0x70,self.__channelNumber])
        self.__chargePort.write(transByArToEscByAr(channelInstr))

        temp_ByteArray = self.__chargePort.read_until(b'\x03',50)
        temp_ByteArray = transEscByArToClearByAr(temp_ByteArray)
        self.__accu_number  = temp_ByteArray[2]
        self.__accu_type    = temp_ByteArray[3]
        self.__accu_type_description = trans_accu_num_to_str(self.__accu_type)
        self.__cellCount    = temp_ByteArray[4]
        self.__rechargeCurrent = float((temp_ByteArray[5] * 256 + temp_ByteArray[6]) / 10)
        self.__chargeCurrent = float((temp_ByteArray[7] * 256 + temp_ByteArray[8]) / 10)
        self.__accuCapacity = float((temp_ByteArray[9] * 0x1000000 + temp_ByteArray[10] * 0x10000 + temp_ByteArray[11] * 0x100 + temp_ByteArray[12]) / 10000)
        self.__programNumber = temp_ByteArray[13]
        self.__formattingCurrent = float((temp_ByteArray[14] * 256 + temp_ByteArray[15]) / 10)
        self.__restPeriod   = temp_ByteArray[16] * 256 + temp_ByteArray[17]
        self.__chargeFlags  = temp_ByteArray[18]
        self.__pointerDataRecord = temp_ByteArray[19] * 256 + temp_ByteArray[20]
        self.__accuCapacityFactor = temp_ByteArray[21]
        
        print("Akkunummer: ",self.__accu_number)
        print("Ladestrom: ",self.__chargeCurrent)
        print("Entladestrom: ",self.__rechargeCurrent)
        print("Akkutype: ",self.__accu_type_description)
        print("Akkukapazität: ",self.__accuCapacity)

    def pullCurrentMeasuredValues(self):
        temp_ByteArray : bytearray
        attemptCount = 0
        channelInstr = bytearray([0x6D,self.__channelNumber])

        self.__chargePort.write(transByArToEscByAr(channelInstr))

        temp_ByteArray = self.__chargePort.read_until(b'\x03',50)
        self.__chargePort.reset_input_buffer()
        self.__chargePort.reset_output_buffer()
        temp_ByteArray = transEscByArToClearByAr(temp_ByteArray)
        if (temp_ByteArray[2] * 256 + temp_ByteArray[2]) != 0xFFFF:
            self.__topicalVoltage = float((temp_ByteArray[2] * 256 + temp_ByteArray[3]) / 1000)
        else:
            self.__topicalVoltage = None
        if (temp_ByteArray[4] * 256 + temp_ByteArray[5]) != 0xFFFF:
            self.__topicalCurrent = float((temp_ByteArray[4] * 256 + temp_ByteArray[5]) / 10)
        else:
            self.__topicalCurrent = None
        self.__topicalAccuCapacity = float((temp_ByteArray[6] * 0x1000000 + temp_ByteArray[7] * 0x10000 + temp_ByteArray[8] * 0x100 + temp_ByteArray[9]) / 10000)
        attemptCount = attemptCount + 1

    def pullChargeFunction(self):
        temp_ByteArray: bytearray
        ChargeFunctionStr_DE = {0:"DE", 1:"Leerlauf", 2:"Pause / Warten", 3:"Entladen", 4:"Erhaltungsladung", 5:"Entladen beendet", 6:"Notabschaltung"}
        ChargeFunctionStr_EN = {0:"EN", 1:"idel state", 2:"pause / wait", 3:"discharge", 4:"maintenance charging", 5:"discharge end", 6:"emergency cutout"}
        ChargeFunctionStr = [ChargeFunctionStr_EN, ChargeFunctionStr_DE]
        channelInstr = bytearray([0x61, self.__channelNumber])

        self.__chargePort.write(transByArToEscByAr(channelInstr))

        temp_ByteArray = self.__chargePort.read_until(b'\x03', 20)
        temp_ByteArray = transEscByArToClearByAr(temp_ByteArray)

        self.__chargeFunktion = temp_ByteArray[1]

        if self.__chargeFunktion >= 0x00 and self.__chargeFunktion <= 0x0A:
            self.__chargeFunktionStr = ChargeFunctionStr[1][1]
        elif self.__chargeFunktion >= 0x0B and self.__chargeFunktion <= 0x2D:
            self.__chargeFunktionStr = ChargeFunctionStr[1][2]
        elif self.__chargeFunktion >= 0x2E and self.__chargeFunktion <= 0x37:
            self.__chargeFunktionStr = ChargeFunctionStr[1][3]
        elif self.__chargeFunktion >= 0x38 and self.__chargeFunktion <= 0x6E:
            self.__chargeFunktionStr = ChargeFunctionStr[1][4]
        elif self.__chargeFunktion >= 0x6F and self.__chargeFunktion <= 0xA0:
            self.__chargeFunktionStr = ChargeFunctionStr[1][5]
        elif self.__chargeFunktion >= 0xA1 and self.__chargeFunktion <= 0xFF:
            self.__chargeFunktionStr = ChargeFunctionStr[1][6]

    def getTopicalVoltage(self):
        return self.__topicalVoltage

    def getTopicalCurrent(self):
        return self.__topicalCurrent

    def getTopicalAccuCapacity(self):
        return self.__topicalAccuCapacity 

    def getAccuNumber(self):
        return self.__accu_number

    def getChargeCurrent(self):
        return self.__chargeCurrent 

    def getRechargeCurrent(self):
        return self.__rechargeCurrent

    def getAccuTypeDescription(self):
        return self.__accu_type_description

    def getCellCount(self):
        return self.__cellCount

    def getProgramNumber(self):
        return self.__programNumber

    def getFormatingCurrent(self):
        return self.__formattingCurrent

    def getRestPeriod(self):
        return self.__restPeriod

    def getChargeFlags(self):
        # TODO: Flags seperat auswerten
        return self.__chargeFlags

    def getPointerDataRecord(self):
        return self.__pointerDataRecord

    def getAccuCapacityFactor(self):
        return self.__accuCapacityFactor

    def getChargeFunktion(self):
        return self.__chargeFunktion

    def getChargeFunctionStr(self):
        return self.__chargeFunktionStr


class ChargeDeviceAccuDbEntry():
    
    def __init__(self, chargePort: serial.Serial, dbEntryNumber):
        
        self.__chargePort = chargePort
        self.__dbEntryNumber = dbEntryNumber

    def pulldbEntry(self):
        temp_ByteArray: bytearray
        channelInstr = bytearray([0x64, self.__dbEntryNumber])
        temp_ByteArray = transByArToEscByAr(channelInstr)
        """
        for i in range(0,temp_ByteArray.__len__()):
            self.__chargePort.write(temp_ByteArray[i])
            time.sleep(0.01)
            print(i," ",temp_ByteArray[i])
        """
        self.__chargePort.write(transByArToEscByAr(channelInstr))
        temp_ByteArray          = self.__chargePort.read_until(b'\x03',50)
        temp_ByteArray          = transEscByArToClearByAr(temp_ByteArray)
        self.__accuName         = temp_ByteArray[2:11].decode()
        self.__dbRereadEntryNumber = temp_ByteArray[1]
        self.__accuType         = temp_ByteArray[11]
        self.__accuCellCount    = temp_ByteArray[12]
        self.__accuCapacity     = float((temp_ByteArray[13] * 0x1000000 + temp_ByteArray[14] * 0x10000 + temp_ByteArray[15] * 0x100 + temp_ByteArray[16]) / 10000)
        self.__rechargeCurrent  = float((temp_ByteArray[17] * 256 + temp_ByteArray[18]) / 10)
        self.__chargeCurrent    = float((temp_ByteArray[19] * 256 + temp_ByteArray[20]) / 10)
        self.__restPeriod       = temp_ByteArray[21] * 256 + temp_ByteArray[22]
        self.__chargeFlags      = temp_ByteArray[23]
        self.__functionsFlags   = temp_ByteArray[24]


    def getAccuName(self):
        return self.__accuName

    def getAccuTyp(self):
        return self.__accuType

    def getAccuCellCount(self):
        return self.__accuCellCount

    def getAccuCapacity(self):
        return self.__accuCapacity

    def getRechargeCurrent(self):
        return self.__rechargeCurrent

    def getChargeCurrent(self):
        return self.__chargeCurrent

    def getRestPeriod(self):
        return self.__restPeriod

    def getChargeFlags(self):
        return self.__chargeFlags

    def getFunctionsFlags(self):
        return self.__functionsFlags


if __name__ == "__main__":

    chargeDevice = charge_devices_alc_generic("COM4")
    chargeDevice.set_ver_ser_num(chargeDevice.pull_ver_ser_num())
    chargeDevice.set_temperatures(chargeDevice.pull_temperatures())

    chargeCannel = Charge_device_alc_channel(chargeDevice.get_charge_port(), 0)
    chargeCannel.pullCurrentCannelData()
    chargeCannel.pullCurrentMeasuredValues()
    chargeCannel.pullChargeFunction()
    chargeDBentry = ChargeDeviceAccuDbEntry(chargeDevice.get_charge_port(), 0x05)
    chargeDBentry.pulldbEntry()

    print(chargeDevice.get_ser_num())
    print(chargeDevice.get_device_type_long())
    print(chargeDevice.get_device_type_short())
    print(chargeDevice.get_device_sw_version())
    print(chargeCannel.getChargeFunctionStr())
    print(chargeDevice.get_main_temperature(), "°C")

    print(chargeDBentry.getAccuName())
    print(chargeDBentry.getAccuTyp())
    print(chargeDBentry.getAccuCellCount())
    print(chargeDBentry.getChargeCurrent())
