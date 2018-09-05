#Author : INF3995 - Équipe 5
import  os.path, sys, hashlib, binascii
from lxml import etree as ET

dataBaseFileName = '../Account/accounts.xml'

#Fonction permettant de créer le compte d'un nouvel utilisateur
def createAccount(chosenUsername, chosenPassword):
    try:
        if not os.path.exists(dataBaseFileName):
            root = ET.Element('Accounts')
            tree = addUserToTree(root, chosenUsername, chosenPassword)
            writeTreeToXMLFile(tree)
            print("User " + chosenUsername + " was created.")
        else:
            parser = ET.XMLParser(remove_blank_text=True)
            tree = ET.parse(dataBaseFileName, parser)
            root = tree.getroot()
            if root.find(chosenUsername) is None:
                tree = addUserToTree(root, chosenUsername, chosenPassword)
                writeTreeToXMLFile(tree)
                print("User " + chosenUsername + " was created.")
            else:
                print("Error, account already exists")
    except ValueError as valueErr:
        print("Exception", valueErr, "was caught.")

#Fonction permettant de supprimer le compte d'un utilisateur
def deleteAccount(user):
    try:
        if os.path.exists(dataBaseFileName):
            parser = ET.XMLParser(remove_blank_text=True)
            tree = ET.parse(dataBaseFileName, parser)
            root = tree.getroot()
            theUser = root.find(user)
            if theUser is None:
                print("Error, user specified does not exist.")
            else:
                root.remove(theUser)
                tree = ET.ElementTree(root)
                writeTreeToXMLFile(tree)
                print("User " + user + " was deleted.")
        else:
            print("Error, account database file not found.")
    except ValueError as valueErr:
        print("Exception", valueErr, "was caught.")

#Fonction permettant de modifier le mot de passe d'un utilisateur
def alterAccountPassword(username, password):
    try:
        if os.path.exists(dataBaseFileName):
            parser = ET.XMLParser(remove_blank_text=True)
            tree = ET.parse(dataBaseFileName, parser)
            root = tree.getroot()
            theUser = root.find(username)
            if theUser is None:
                print("Error, user specified does not exist.")
            else:
                userPassword = theUser.find('password')
                userPassword.text = encryptPassword(password)
                tree = ET.ElementTree(root)
                writeTreeToXMLFile(tree)
                print("User " + username + "'s password altered.")
        else:
            print("Error, account database file not found.")
    except ValueError as valueErr:
        print("Exception", valueErr, "was caught.")

#Fonction permettant d'écrire l'arbre XML dans le fichier accounts.xml
def writeTreeToXMLFile(tree):
    tree.write(dataBaseFileName, pretty_print=True, xml_declaration=True, encoding="utf-8")

#Fonction permettant d'ajouté un utilisateur à l'arbre XML
def addUserToTree(root, chosenUsername, chosenPassword):
    user = ET.SubElement(root, chosenUsername)
    #username = ET.SubElement(user, 'username')
    #username.text = chosenUsername
    password = ET.SubElement(user, 'password')
    password.text = encryptPassword(chosenPassword)
    tree = ET.ElementTree(root)
    return tree

#Fonction permettant d'imprimer à l'écran les options que prend cet utilitaire
def printUsage():
    print("Options : \n(--new USERNAME PASSWORD) - Creates a new account \n(--delete USERNAME) - Deletes an existing account \n(--alter USERNAME NEWPASSWORD) - Modify an existing user's password")

#Fonction permettant d'encrypter le mot de passe d'un utilisateur en sha512,
#salé 0XCAFE fois
def encryptPassword(chosenPassword):
    value = hashlib.pbkdf2_hmac('sha512', bytes(chosenPassword, encoding='utf-8'), b'I love my grandma', 51966)
    return binascii.hexlify(value)

#Main function
def main():
    try:
        if len(sys.argv) > 1:
            if len(sys.argv) > 3 and sys.argv[1].lower() == '--new':
               createAccount(sys.argv[2].lower(), sys.argv[3])
            elif sys.argv[1].lower() == '--delete':
                deleteAccount(sys.argv[2].lower())
            elif len(sys.argv) > 3 and sys.argv[1].lower() == '--alter':
                alterAccountPassword(sys.argv[2].lower(), sys.argv[3])
            else:
                printUsage()
        else:
            printUsage()
    except KeyError as e:
        print('Username cannot contain special character ', e)

if __name__ == '__main__':
    main()
