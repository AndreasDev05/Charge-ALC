import sys

class byteArrayToShort(Exception):
    pass

def transEscByArToClearByAr(RawArray : bytearray):
    ''' Entfernt Rahmenzeichen und ESCs

    Entfernt aus dem übergebenen Bytearray das erste und letzte Zeichen
    und tauscht folgende Escape Kombinationen aus:

    0x05 0x12   ->  0x02
    0x05 0x13   ->  0x03
    0x05 0x15   ->  0x05

    Im andern Fall wird 0x00 zurückgegeben
    '''
    laenge = int(RawArray.__len__())
    if laenge < 3:
        raise byteArrayToShort("Bytearry to short, min. 3")
    newArray = []
    tempByte : bytes
    jumpEscFlag = False
    for i in range(1,laenge-1):
        if jumpEscFlag:  # jump over, it is the second char of escape sequence
            jumpEscFlag = False
            continue
        else:
            if RawArray[i] == 0x05:
                if RawArray[i+1] == 0x12:
                    tempByte = 0x02
                elif RawArray[i+1] == 0x13:
                    tempByte = 0x03
                elif RawArray[i+1] == 0x15:
                    tempByte = 0x05
                else:
                    tempByte = 0x00
                newArray.append(tempByte)
                jumpEscFlag = True
                continue
            else:
                newArray.append(RawArray[i])
    return(bytearray(newArray))

def transByArToEscByAr(RawArray : bytearray):
    ''' Fügt Rahmenzeichen und ESCs ein

    Fügt in das übergebenen Bytearray die Rahmenzeichen ein
    und tauscht folgende Escape Kombinationen aus:

    0x02    ->  0x05 0x12
    0x03    ->  0x05 0x13
    0x05    ->  0x05 0x15

    '''
    laenge = int(RawArray.__len__())
    if laenge < 1:
        raise byteArrayToShort("Bytearry to short, min. 1")
    newArray = [0x02]
    for i in range(0,laenge):
        if RawArray[i] == 0x02:
            newArray.append(0x05)
            newArray.append(0x12)
        elif RawArray[i] == 0x03:
            newArray.append(0x05)
            newArray.append(0x13)
        elif RawArray[i] == 0x05:
            newArray.append(0x05)
            newArray.append(0x15)
        else:
            newArray.append(RawArray[i])
    newArray.append(0x03)
    return(bytearray(newArray))

# 
if __name__ == "__main__":
  
    print(transEscByArToClearByAr(([0x02,0x01,0x04,0xFF,0x05,0x12,0x03,0x05,0x15,0x03])))

    try:
        print(transEscByArToClearByAr([0x02,0x03]))
    except byteArrayToShort:
        print("Der übergebene String ist zu kurz!")

    print(transByArToEscByAr([0x01,0x03,0x04,0xFF]))
