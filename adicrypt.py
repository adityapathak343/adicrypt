import random
import json
import hashlib


def sumord(string):
    sum = 0
    for i in string:
        sum += ord(i)
    return sum


class TextTableGenerator:
    def __init__(self):
        self.valid_chars = list(
            set(r',./[]:;<>?/\|=+-_)(*&^%$#@!`~)1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ '))

    def generate(self):
        valid_chars = self.valid_chars
        valid_chars.sort()

        final_encr_dict = {}
        final_decr_dict = {}
        map_chars = valid_chars.copy()

        for i in range(1000):
            seed = i
            random.seed(seed)
            random.shuffle(map_chars)
            mapped_encr_dict = {valid_chars[j]: map_chars[j] for j in range(len(valid_chars))}
            mapped_decr_dict = {map_chars[j]: valid_chars[j] for j in range(len(valid_chars))}
            final_encr_dict[i] = mapped_encr_dict
            final_decr_dict[i] = mapped_decr_dict

        with open('encr_tables.json', 'w') as f:
            json.dump(final_encr_dict, f)

        with open('decr_tables.json', 'w') as f:
            json.dump(final_decr_dict, f)

class ByteTableGenerator:
    def __init__(self):
        self.valid_chars = [i for i in range(256)]

    def generate(self):
        valid_chars = self.valid_chars
        valid_chars.sort()

        final_encr_dict = {}
        final_decr_dict = {}
        map_chars = valid_chars.copy()

        for i in range(1000):
            seed = i
            random.seed(seed)
            random.shuffle(map_chars)
            mapped_encr_dict = {valid_chars[j]: map_chars[j] for j in range(len(valid_chars))}
            mapped_decr_dict = {map_chars[j]: valid_chars[j] for j in range(len(valid_chars))}
            final_encr_dict[i] = mapped_encr_dict
            final_decr_dict[i] = mapped_decr_dict

        with open('encr_tables_expanded.json', 'w') as f:
            json.dump(final_encr_dict, f)

        with open('decr_tables_expanded.json', 'w') as f:
            json.dump(final_decr_dict, f)


class TextEncrypt:
    def __init__(self, pwd):
        self.pwd = pwd
        try:
            self.encr_tables = json.loads(open('encr_tables.json', 'r').read())
            self.decr_tables = json.loads(open('decr_tables.json', 'r').read())
        except FileNotFoundError:
            TextTableGenerator().generate()
            self.encr_tables = json.loads(open('encr_tables.json', 'r').read())
            self.decr_tables = json.loads(open('decr_tables.json', 'r').read())

    def encrypt(self, string):
        pwd = self.pwd
        random.seed(sumord(pwd))
        ctr = random.randint(0, 999)
        pwd_ctr = 0
        encr_str = ''
        for i in string:
            char = pwd[pwd_ctr]
            ctr = (ctr + ord(char)) % 1000
            table = self.encr_tables[str(ctr)]
            encr_str += table[i]
            pwd_ctr = (pwd_ctr + 1) % len(pwd)
        return encr_str

    def decrypt(self, string):
        pwd = self.pwd
        random.seed(sumord(pwd))
        ctr = random.randint(0, 999)
        # ctr = 0
        pwd_ctr = 0
        decr_str = ''
        for i in string:
            char = pwd[pwd_ctr]
            ctr = (ctr + ord(char)) % 1000
            table = self.decr_tables[str(ctr)]
            decr_str += table[i]
            pwd_ctr = (pwd_ctr + 1) % len(pwd)
        return decr_str


class FileEncrypt:
    def __init__(self, pwd):
        self.pwd = hashlib.sha256(pwd.encode()).hexdigest()
        try:
            self.encr_tables = json.loads(open('encr_tables_expanded.json', 'r').read())
            self.decr_tables = json.loads(open('decr_tables_expanded.json', 'r').read())
        except FileNotFoundError:
            ByteTableGenerator().generate()
            self.encr_tables = json.loads(open('encr_tables_expanded.json', 'r').read())
            self.decr_tables = json.loads(open('decr_tables_expanded.json', 'r').read())

    def encrypt(self, filename):
        with open(filename, "rb") as file:
            data = file.read()
        ext = filename.split('.')[1]
        filename = filename.split('.')[0]
        ext_toadd = "adienc"
        pwd = self.pwd

        random.seed(sumord(pwd))
        ctr = random.randint(0, 999)
        pwd_ctr = 0
        encr_arr = []

        for i in data:
            char = pwd[pwd_ctr]
            ctr = (ctr + ord(char)) % 1000
            table = self.encr_tables[str(ctr)]
            encr_arr.append(table[str(i)])
            pwd_ctr = (pwd_ctr + 1) % len(pwd)

        encrypted = bytearray([len(ext)]) + bytearray(ext, 'utf-8') + bytearray(encr_arr)

        with open(filename + "_encrypted." + ext_toadd, 'wb') as file:
            file.write(encrypted)

        return 0

    def decrypt(self, filename):

        with open(filename, "rb") as file:
            data = file.read()
        ext = filename.split('.')[1]
        filename = filename.split('.')[0]
        if ext != 'adienc':
            print("File is not an ADIENC file. Cannot decrypt!")
            return -1
        ext_toadd = data[1:1 + int(data[0])]
        bytearr = data[1 + int(data[0]):]

        pwd = self.pwd
        random.seed(sumord(pwd))
        ctr = random.randint(0, 999)
        pwd_ctr = 0
        decr_arr = []
        for i in bytearr:
            char = pwd[pwd_ctr]
            ctr = (ctr + ord(char)) % 1000
            table = self.decr_tables[str(ctr)]
            decr_arr.append(table[str(i)])
            pwd_ctr = (pwd_ctr + 1) % len(pwd)

        with open(filename + "_decrypted." + str(ext_toadd, 'utf-8'), 'wb') as file:
            file.write(bytearray(decr_arr))

        return 0

