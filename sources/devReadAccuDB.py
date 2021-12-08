from ctypes.wintypes import CHAR
import serial
from serial.serialutil import PARITY_EVEN, Timeout
import serial.tools.list_ports, serial.tools.list_ports_common, serial.tools.list_ports_windows
import Charge_ALC
from simpleHelpFunc import transByArToEscByAr, transEscByArToClearByAr

def pulldbEntry(chargeport:serial.Serial,dbEntryNumber):
    temp_ByteArray : bytearray

    print(dbEntryNumber)
    channelInstr            = transByArToEscByAr([0x64,dbEntryNumber])
    print(channelInstr)
    chargeport.write(channelInstr)
    temp_ByteArray          = chargeport.read_until(b'\x03',50)
    temp_ByteArray          = transEscByArToClearByAr(temp_ByteArray)
    accuName                = temp_ByteArray[2:11].decode()
    dbRereadEntryNumber = temp_ByteArray[1]
    accuType                = temp_ByteArray[11]
    accuCellCount    = temp_ByteArray[12]
    accuCapacity     = float((temp_ByteArray[13] * 0x1000000 + temp_ByteArray[14] * 0x10000 + temp_ByteArray[15] * 0x100 + temp_ByteArray[16]) / 10000)
    '''
    self.__rechargeCurrent  = float((temp_ByteArray[18] * 256 + temp_ByteArray[19]) / 10)
    self.__chargeCurrent    = float((temp_ByteArray[20] * 256 + temp_ByteArray[21]) / 10)
    self.__restPeriod       = temp_ByteArray[22] * 256 + temp_ByteArray[23]
    self.__chargeFlags      = temp_ByteArray[24]
    self.__functionsFlags   = temp_ByteArray[25]
    '''
    print(type(temp_ByteArray))
    print(temp_ByteArray)
    print(accuName)
    print(dbRereadEntryNumber)
    print(accuType)
    print(accuCellCount)
    print(accuCapacity)

    #print(self.__accuName)


chargeDevice = Charge_ALC.ChargeDevicesAlcGeneric("COM4")
# chargeDevice.setVerSerNum(chargeDevice.pullVerSerNum())
# chargeDevice.setTemperatures(chargeDevice.pullTemperatures())

pulldbEntry(chargeDevice.getChargePort(),2)