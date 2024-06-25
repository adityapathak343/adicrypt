import click
import json
import hashlib
import adicrypt

try:
    print("Loading Passwords...")
    encrypted_list = json.loads(open("pwd.json").read())
    print("Done")
except FileNotFoundError:
    print("pwd.json not found! Creating Passwords File...")
    json.dump({}, open("pwd.json", "w"))
    encrypted_list = json.loads(open("pwd.json").read())
    print("Done")

def sha_encrypt(thing):
    return hashlib.sha256(thing.encode()).hexdigest()

def readPasswordKey():
    with open("passkey_encrypted.txt", 'r') as f:
        pwd_key = f.read()
    return pwd_key

def changePassword(new_pass):
    new_key = sha_encrypt(new_pass)
    with open("passkey_encrypted.txt", 'w') as f:
        f.write(new_key)

try:
    pwd_enc = readPasswordKey()
except FileNotFoundError:
    changePassword("password")
    pwd_enc = readPasswordKey()
@click.group("cli")
@click.password_option()
def cli(password):
    global TextEncryptor
    if sha_encrypt(password) != pwd_enc:
        click.echo("Authentication failed")
        raise SystemExit(-1)

    TextEncryptor = adicrypt.TextEncrypt(password)


@cli.command("show")
def show():
    names = list(encrypted_list.keys())
    click.echo({i: names[i] for i in range(len(names))})

@cli.command("get")
@click.argument("name", required=True)
def get(name):
    names = list(encrypted_list.keys())
    if name in names:
        click.echo(TextEncryptor.decrypt(encrypted_list[name]))
    else:
        click.echo("No such name in the encrypted list")

@cli.command("add")
@click.argument("name", required=True)
@click.password_option(prompt="Enter Password to add >")
def add(name, password):
    encrypted_list[name] = TextEncryptor.encrypt(password)
    with open("pwd.json", "w") as file:
        json.dump(encrypted_list, file)
    click.echo("Password Added")

@cli.command("remove")
@click.argument("name", required=True)
def remove(name):
    names = list(encrypted_list.keys())
    if name in names:
        del encrypted_list[name]
        with open("pwd.json", "w") as file:
            json.dump(encrypted_list, file)
        click.echo("Password Removed")
    else:
        click.echo("No such name in encrypted list")

@cli.command("encrypt")
@click.argument("file", required=True)
@click.password_option(prompt="Enter encryption password for file >")
def encrypt(file, password):
    FileEncryptor = adicrypt.FileEncrypt(password)
    try:
        FileEncryptor.encrypt(file)
        click.echo("File encrypted!")
    except FileNotFoundError:
        click.echo("No such file")

@cli.command("decrypt")
@click.argument("file", required=True)
@click.password_option(prompt="Enter encryption password for file >")
def decrypt(file, password):
    FileEncryptor = adicrypt.FileEncrypt(password)
    try:
        FileEncryptor.decrypt(file)
        click.echo("File decrypted!")
    except FileNotFoundError:
        click.echo("No such file")

@cli.command("change_key")
@click.password_option(prompt="Enter new password >")
def change_key(password):
    NewTextEncryptor = adicrypt.TextEncrypt(password)
    for i, (k, v) in enumerate(encrypted_list.items()):
        encrypted_list[k] = NewTextEncryptor.encrypt(TextEncryptor.decrypt(v))
    changePassword(password)
    with open("pwd.json", "w") as file:
        json.dump(encrypted_list, file)


if __name__ == "__main__":
    cli()
