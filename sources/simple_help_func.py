# import sys


class byte_array_to_short(Exception):
    pass


def trans_accu_num_to_str(accu_number: int):
    """Gibt den ausgeschriebenen Akkutyp zurück.

    Der übergebene Bytewert wird in ein String umgesetzt
    """
    accu_typs_str = ["NiCd", "NiMH", "Li-Ion", "LiPo", "Pb", "LiFePO", "N/A"]
    if accu_number < 6:
        return accu_typs_str[int(accu_number)]
    else:
        return accu_typs_str[6]


def trans_esc_by_ar_to_clear_by_ar(raw_array: bytearray):
    """Entfernt Rahmenzeichen und ESCs.

    Entfernt aus dem übergebenen Bytearray das erste und letzte Zeichen
    und tauscht folgende Escape Kombinationen aus:

    0x05 0x12   ->  0x02
    0x05 0x13   ->  0x03
    0x05 0x15   ->  0x05

    Im andern Fall wird 0x00 zurückgegeben
    """
    laenge = int(raw_array.__len__())
    if laenge < 3:
        raise byte_array_to_short("Bytearry to short, min. 3")
    new_array = bytearray(raw_array.__len__()-2)
    temp_byte: bytes
    j = 0
    jump_esc_flag = False
    for i in range(1, laenge-1):
        if jump_esc_flag:
            # jump over, it is the second char of escape sequence
            jump_esc_flag = False
            continue
        else:
            if raw_array[i] == 0x05:
                if raw_array[i+1] == 0x12:
                    temp_byte = 0x02
                elif raw_array[i+1] == 0x13:
                    temp_byte = 0x03
                elif raw_array[i+1] == 0x15:
                    temp_byte = 0x05
                else:
                    temp_byte = 0x00
                new_array[j] = temp_byte
                j += 1
                jump_esc_flag = True
                continue
            else:
                new_array[j] = raw_array[i]
                j += 1
    return(bytearray(new_array))


def trans_by_ar_to_esc_by_ar(raw_array: bytearray):
    """Fügt Rahmenzeichen und ESCs ein.

    Fügt in das übergebenen Bytearray die Rahmenzeichen ein
    und tauscht folgende Escape Kombinationen aus:

    0x02    ->  0x05 0x12
    0x03    ->  0x05 0x13
    0x05    ->  0x05 0x15

    """
    laenge = int(raw_array.__len__())
    if laenge < 1:
        raise byte_array_to_short("Bytearry to short, min. 1")
    new_array = [0x02]
    for i in range(0, laenge):
        if raw_array[i] == 0x02:
            new_array.append(0x05)
            new_array.append(0x12)
        elif raw_array[i] == 0x03:
            new_array.append(0x05)
            new_array.append(0x13)
        elif raw_array[i] == 0x05:
            new_array.append(0x05)
            new_array.append(0x15)
        else:
            new_array.append(raw_array[i])
    new_array.append(0x03)
    return(bytearray(new_array))


#
if __name__ == "__main__":

    print(trans_esc_by_ar_to_clear_by_ar(
        ([0x02, 0x01, 0x04, 0xFF, 0x05, 0x12, 0x03, 0x05, 0x15, 0x03])))

    try:
        print(trans_esc_by_ar_to_clear_by_ar([0x02, 0x03]))
    except byte_array_to_short:
        print("Der übergebene String ist zu kurz!")

    print(trans_by_ar_to_esc_by_ar([0x01, 0x03, 0x04, 0xFF]))
