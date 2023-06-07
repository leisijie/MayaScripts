from P4 import P4,P4Exception
#p4python is needed for this script
#This script will clean the have list to remove files that show existing but actually not in workspace.This problem will lead Get Lastest not work but only can use Get Revision with Force Operation to update.
address = "Your server address"
user_name = "Your user name"
folder = "the folder you want to clean"

if __name__ == '__main__':
    p4 = P4()
    p4.port = address
    p4.user = user_name
    p4.connect()
    files = p4.run("diff","-sd",folder)
    index = 0
    length = len(files)
    if(length==0):
        print("No such files in the workspace")
    for i in range(length):
        p4.run("sync",files[i]["depotFile"]+"#0")
        print(str(length-i))
        
    