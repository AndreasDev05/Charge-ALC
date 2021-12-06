def transEscByArToClearByAr(RawArray : bytearray):
    laenge = int(RawArray.__len__())
    newArray = []
    tempByte : bytes
    jumpEscFlag = False
    print(RawArray)
    for i in range(1,laenge-1):
        print("Count: ",i)
        if jumpEscFlag:
            jumpEscFlag = False
            continue
        else:
            print("TargetByte",RawArray[i])
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
                print(tempByte)
                jumpEscFlag = True
                continue
            else:
                newArray.append(RawArray[i])
                print(newArray)
    print()
    print(newArray)
    return(bytearray(newArray))

print(transEscByArToClearByAr(([0x02,0x01,0x04,0xFF,0x05,0x12,0x03,0x05,0x15,0x03])))