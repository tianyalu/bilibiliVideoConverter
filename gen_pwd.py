import hashlib
import datetime

SPECIAL_CHART = [")", "!", "@", "#", "$", "%", "^", "&", "*", "("]
UPPERCASE = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
             "V", "W", "X", "Y", "Z"]
LOWERCASE = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
             "v", "w", "x", "y", "z"]
NUMBER = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# SRC_STR = '18126532381'
SALT = 'flcp2023!!!'


def hex_str_to_int_array(temp_string):
    array = []
    for i in range(0, len(temp_string), 2):
        array.append(int(temp_string[i: i + 2], 16))
    return array


def gen_password(src_str):
    digest1 = hashlib.md5(src_str.encode()).hexdigest()  # efdb701da50f3bac8f80efb5262
    digest = hashlib.md5(f'{digest1}{SALT}'.encode()).hexdigest()  # 78142a0be1532cc916d917ec6e
    temp_string = digest[4: 24]  # 2a0be1532cc916d917ec
    int_array = hex_str_to_int_array(temp_string)  # [42, 11, 225, 83, 44, 201, 22, 217, 23, 236]
    pwd = ''
    for i, value in enumerate(int_array):  # [16, 1, 5, 5, 4, 19, 2, 9, 23, 2]
        index = i + 1
        if index == 1 or index == 6 or index == 9:
            pwd += UPPERCASE[value % len(UPPERCASE)]
        elif index == 4 or index == 8 or index == 10:
            pwd += LOWERCASE[value % len(LOWERCASE)]
        elif index == 2 or index == 7:
            pwd += SPECIAL_CHART[value % len(SPECIAL_CHART)]
        elif index == 3 or index == 5:
            pwd += NUMBER[value % len(NUMBER)]
    return pwd


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    SRC_STR = input('请输入需要加密的字符串：')
    if SRC_STR.lower() == 'date':
        now = datetime.datetime.now().strftime("%Y%m%d")
        SRC_STR = now
    # print(f'SRC_STR: {now}')
    password = gen_password(SRC_STR)
    print(f'加密结果为：')
    print(password)
    input('Press Enter key to quit program.')
