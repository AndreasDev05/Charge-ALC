from ctypes.wintypes import CHAR
import serial
from serial.serialutil import PARITY_EVEN, Timeout
import serial.tools.list_ports, serial.tools.list_ports_common, serial.tools.list_ports_windows
import time

from simpleHelpFunc import transByArToEscByAr, transEscByArToClearByAr

#import locale
#locale.setlocale(locale.LC_ALL, 'de_DE')

def transAccuNumToStr(accuNumber):
    accuTypsStr = ["NiCd","NiMH","Li-Ion","LiPo","Pb","LiFePO","N/A"]
    if accuNumber < 6:
        return(accuTypsStr[accuNumber])
    else:
        return(accuTypsStr[6])

class ChargeDevicesAlcGeneric():

    ChargeChannels = 0
    AccuDbItems = 0x27

    def __init__(self, ser_port):
        self.__chargePort = serial.Serial(ser_port, 38400, 8, PARITY_EVEN, 1, 3)
        #TODO: Expliziete Übergabe der Schnittstellenparameter, für eine unverselle Funktion
    #    print(type(self.__chargePort))

    def pullVerSerNum(self):
        temp_ByteArray : bytearray
        chargeInstr = bytearray([0x75])
        
        self.__chargePort.write(transByArToEscByAr(chargeInstr))

        temp_ByteArray = self.__chargePort.read_until(b'\x03',50)
        temp_ByteArray = transEscByArToClearByAr(temp_ByteArray)
        return(temp_ByteArray)

    def pullTemperatures(self):
        temp_ByteArray : bytearray
        chargeInstr = bytearray([0x74])
        
        self.__chargePort.write(transByArToEscByAr(chargeInstr))

        temp_ByteArray = self.__chargePort.read_until(b'\x03',50)
        temp_ByteArray = transEscByArToClearByAr(temp_ByteArray)
        return(temp_ByteArray)
   
    def setVerSerNum(self, serNumRaw: bytearray):
        longAlcTyp = {98: "ALC 8500 Firmware < 2.00", 99: "ALC 8000 Firmware < 2.00",
                      100: "ALC 8500-2 Firmware < 2.00", 101: "ALC 8000 PLUS Firmware < 2.00", 102: "ALC 5000 mobile Firmware < 2.00",
                      103: "ALC 3000 PC Firmware > 2.00", 104: "ALC 8500-2 Firmware > 2.00", 105: "ALC 8000 Firmware > 2.00",
                      106: "ALC 5000 mobil Firmware > 2.00"}
        
        shortAlcTyp = {98: "ALC8500", 99: "ALC8000", 100: "ALC8500-2", 101: "ALC8000PLUS",
                       102: "ALC5000mobile", 103: "ALC3000PC", 104: "ALC8500-2", 105: "ALC8000", 106: "ALC5000mobil"}
        
        temp_string = serNumRaw[6:10]
        self.__SwVersion = temp_string.decode()
        self.__TypeLong = longAlcTyp[serNumRaw[1]]
        self.__TypeShort = shortAlcTyp[serNumRaw[1]]

        temp_string = serNumRaw[12:22]
        self.__SerialNumber = temp_string.decode()

    def setTemperatures(self, temperaturesRaw: bytearray):

        temp_temp_int = temperaturesRaw[1] * 256 + temperaturesRaw[2]
        if temp_temp_int == 0xABE0:
            self.__tempAccuFloat = None
        else:
            self.__tempAccuFloat = float(temp_temp_int / 100)
        #TODO: Negative Temperaturen berechnen

        temp_temp_int = temperaturesRaw[3] * 256 + temperaturesRaw[4]
        if temp_temp_int == 0xABE0:
            self.__tempPowerSupFloat = None
        else:
            self.__tempPowerSupFloat = float(temp_temp_int / 100)
        #TODO: Negative Temperaturen berechnen

        temp_temp_int = temperaturesRaw[5] * 256 + temperaturesRaw[6]
        self.__tempMainFloat = float(temp_temp_int / 100)

    def getSerNum(self):
        return(self.__SerialNumber)

    def getDeviceTypeLong(self):
        return(self.__TypeLong)

    def getDeviceTypeShort(self):
        return(self.__TypeShort)

    def getDeviceSwVersion(self):
        return(self.__SwVersion)

    def getChargePort(self):
        return(self.__chargePort)

    def getMainTemperature(self):
        return(self.__tempMainFloat)

    def getAccuTemperature(self):
        '''  Temperatur des Akkus

        Gibt die Temperatur des Akkus in °C als float zurück.
        Wenn kein Sensor angeschlossen ist gibt die Funktion "None" zurück.
        '''
        return(self.__tempAccuFloat)

class ChargeDeviceALC3000(ChargeDevicesAlcGeneric):

    chargeCannel = 1

    def __init__(self, ser_port):
        ChargeDevicesAlcGeneric.__init__(self, ser_port)
        
        for i in range(1,self.chargeCannel):
            self.chargeCannelIns[i] = ChargeDeviceALCChannel(self.__chargePort,i-1)
            self.chargeCannelIns[i].pullCurrentCannelData()
            self.chargeCannelIns[i].pullCurrentMeasuredValues()

        for i in range(self.AccuDbItems):
            self.chargeDbEntry[i] = ChargeDeviceAccuDbEntry(self.__chargePort,i)
            self.chargeDbEntry[i].pulldbEntry

class ChargeDeviceALCChannel():

    def __init__(self, chargePort:serial.Serial, channelNumber):

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
        self.__accuNumber   = temp_ByteArray[2]
        self.__accuType     = temp_ByteArray[3]
        self.__accuTypeDescription = transAccuNumToStr(self.__accuType)
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
        
        print("Akkunummer: ",self.__accuNumber)
        print("Ladestrom: ",self.__chargeCurrent)
        print("Entladestrom: ",self.__rechargeCurrent)
        print("Akkutype: ",self.__accuTypeDescription)
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
        temp_ByteArray : bytearray
        ChargeFunctionStr_DE = {0:"DE",1:"Leerlauf",2:"Pause / Warten",3:"Entladen",4:"Erhaltungsladung",5:"Entladen beendet",6:"Notabschaltung"}
        ChargeFunctionStr_EN = {0:"EN",1:"idel state",2:"pause / wait",3:"discharge",4:"maintenance charging",5:"discharge end",6:"emergency cutout"}
        ChargeFunctionStr = [ChargeFunctionStr_EN,ChargeFunctionStr_DE]
        channelInstr = bytearray([0x61,self.__channelNumber])

        self.__chargePort.write(transByArToEscByAr(channelInstr))

        temp_ByteArray = self.__chargePort.read_until(b'\x03',20)
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
        return(self.__topicalVoltage)

    def getTopicalCurrent(self):
        return(self.__topicalCurrent)

    def getTopicalAccuCapacity(self):
        return(self.__topicalAccuCapacity)

    def getAccuNumber(self):
        return(self.__accuNumber)

    def getChargeCurrent(self):
        return(self.__chargeCurrent)

    def getRechargeCurrent(self):
        return(self.__rechargeCurrent)

    def getAccuTypeDescription(self):
        return(self.__accuTypeDescription)

    def getCellCount(self):
        return(self.__cellCount)

    def getProgramNumber(self):
        return(self.__programNumber)

    def getFormatingCurrent(self):
        return(self.__formattingCurrent)

    def getRestPeriod(self):
        return(self.__restPeriod)

    def getChargeFlags(self):
        # TODO: Flags seperat auswerten
        return(self.__chargeFlags)

    def getPointerDataRecord(self):
        return(self.__pointerDataRecord)

    def getAccuCapacityFactor(self):
        return(self.__accuCapacityFactor)

    def getChargeFunktion(self):
        return(self.__chargeFunktion)

    def getChargeFunctionStr(self):
        return(self.__chargeFunktionStr)

class ChargeDeviceAccuDbEntry():
    
    def __init__(self,chargePort:serial.Serial,dbEntryNumber):
        
        self.__chargePort = chargePort
        self.__dbEntryNumber = dbEntryNumber

    def pulldbEntry(self):
        temp_ByteArray : bytearray
        channelInstr = bytearray([0x64,self.__dbEntryNumber])
        temp_ByteArray = transByArToEscByAr(channelInstr)
        '''
        for i in range(0,temp_ByteArray.__len__()):
            self.__chargePort.write(temp_ByteArray[i])
            time.sleep(0.01)
            print(i," ",temp_ByteArray[i])
        '''
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
        return(self.__accuName)

    def getAccuTyp(self):
        return(self.__accuType)

    def getAccuCellCount(self):
        return(self.__accuCellCount)

    def getAccuCapacity(self):
        return(self.__accuCapacity)

    def getRechargeCurrent(self):
        return(self.__rechargeCurrent)

    def getChargeCurrent(self):
        return(self.__chargeCurrent)

    def getRestPeriod(self):
        return(self.__restPeriod)

    def getChargeFlags(self):
        return(self.__chargeFlags)

    def getFunctionsFlags(self):
        return(self.__functionsFlags)

if __name__ == "__main__":

    chargeDevice = ChargeDevicesAlcGeneric("COM4")
    chargeDevice.setVerSerNum(chargeDevice.pullVerSerNum())
    chargeDevice.setTemperatures(chargeDevice.pullTemperatures())

    chargeCannel = ChargeDeviceALCChannel(chargeDevice.getChargePort(),0)
    chargeCannel.pullCurrentCannelData()
    chargeCannel.pullCurrentMeasuredValues()
    chargeCannel.pullChargeFunction()
    chargeDBentry = ChargeDeviceAccuDbEntry(chargeDevice.getChargePort(),0x05)
    chargeDBentry.pulldbEntry()

    print(chargeDevice.getSerNum())
    print(chargeDevice.getDeviceTypeLong())
    print(chargeDevice.getDeviceTypeShort())
    print(chargeDevice.getDeviceSwVersion())
    print(chargeCannel.getChargeFunctionStr())
    print(chargeDevice.getMainTemperature(),"°C")

    print(chargeDBentry.getAccuName())
    print(chargeDBentry.getAccuTyp())
    print(chargeDBentry.getAccuCellCount())
    print(chargeDBentry.getChargeCurrent())