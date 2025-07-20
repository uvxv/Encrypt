from moduleAES import *
import os


def folder_encryption():
    while True:
        folder_path = input("Enter the absolute folder path: ")
        key = input("Enter the password: ")

        if len(key) != 16:
            print('The password should be 16 characters in length')
            continue

        if os.path.isdir(folder_path):
            break
        elif os.path.isfile(folder_path):
            print("This is a path to a file, Required a path directory")
            continue
        else:
            print("Invalid path")
            continue


    for root, dir, files in os.walk(folder_path):
        for file in files:
            join_path = os.path.join(root, file)
            extension = os.path.splitext(join_path)
            extension_list = list(extension)

            if '.aes' not in extension_list:
                with open(join_path, 'rb') as file_data:
                    read = file_data.read()
                    crypt = AESfile.encryption(key, read)
                with open(join_path, 'wb') as wfile:
                    wfile.write(crypt)

                extension_list.append('.aes')
                os.rename(join_path, ''.join(extension_list))

                print('Encrypted the file', file)

            else:
                print(file, 'Aready encrypted')
    input('Press any key to exit...')
    return


def folder_decryption():
    while True:
        folder_path = input("Enter the absolute folder path: ")

        if os.path.isdir(folder_path):
            break
        elif os.path.isfile(folder_path):
            print("This is a path to a file, Required a path")
            continue
        else:
            print("Invalid path")
            continue

    key = input("Enter the password: ")

    for root, dir, files in os.walk(folder_path):
        for file in files:
            join_path = os.path.join(root, file)  # Output a tuple --> ('filename', '.txt')
            extension = os.path.splitext(join_path)
            extension_list = list(extension)

            if '.aes' in extension_list:
                with open(join_path, 'rb') as file_data:
                    read = file_data.read()
                    try:
                        crypt = AESfile.decryption(key, read)
                    except ValueError:
                        print("Make sure the PASSWORD CORRECT, re-run the program and try again!")
                        input('Press any key to exit...')
                        return
                with open(join_path, 'wb') as wfile:
                    wfile.write(crypt)

                extension_list.pop(-1)
                os.rename(join_path, ''.join(extension_list))

                print('Decrypted the file', file)

            else:
                print(file, 'Aready decrypted')

    input('Press any key to exit...')

    return


print("This program is to encrypt/decrypt the folders\n")
select = input("Select whether to encrypt of decrypt a folder (e/d): ")

if select.lower() == 'e':
    folder_encryption()
elif select.lower() == 'd':
    folder_decryption()
else:
    print("Oops invalid choice...!")
