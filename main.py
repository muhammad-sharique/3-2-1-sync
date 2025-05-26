import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# import time
import time
import datetime
import os


syncTime = int(time.time());
defaultOffsiteFolderId = '1cd0IYi9qtpRlV-eWBR3-yEak6oGpyvul' # Folder Name - Backup
defaultPrimaryFolderId = 'D:\Backup'
defaultBackupFolderId = 'E:\Backup'

print('Welcome to 3-2-1 Sync! Please Choose Sync Mode')
print('1. Complete 3-2-1 Sync (online - Recommended)')
print('2. Offsite to Primary Sync (Online)')
print('3. Primary to Backup Sync (offline)')
userInput = input('Enter your choice: ');
if userInput == '1':
    syncMode = 1;
elif userInput == '2':
    syncMode = 2;
elif userInput == '3':
    syncMode = 3;
else:
    print('Invalid Input, Exiting...')
    exit();

# syncMode = 3; #for testing

if syncMode == 1 or syncMode == 2:
    if os.path.exists("credentials.json"):
        logout = input(f"You are aLready logged in, Do you want to logout? (y/n) [Default - N]: ") or "n"
        # logout = "n" #for testing
        if logout == "y":
            os.remove("credentials.json")
            print("Logged out successfully")

    print("Logging in...")
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    #create a drive object
    drive = GoogleDrive(gauth)

    offsiteFolderId = input(f"Enter Offsite Folder ID [Default : {defaultOffsiteFolderId}] -> ") or defaultOffsiteFolderId;
    # offsiteFolderId = defaultOffsiteFolderId; #for testing

primaryFolderId = input(f"Enter primary folder Id [Default : {defaultPrimaryFolderId}] -> ") or defaultPrimaryFolderId;
# primaryFolderId = defaultPrimaryFolderId #for testing

if(syncMode == 1 or syncMode == 3):
    backupFolderId = input(f"Enter backup folder Id [Default : {defaultBackupFolderId}] ->") or defaultBackupFolderId;
    # backupFolderId = defaultBackupFolderId #for testing


def main():
    if syncMode == 1 :
        # Here we will need all three folders
        offsiteFoldername = getDriveFolderName(offsiteFolderId)
        primaryFoldername = os.path.basename(primaryFolderId)
        backupFoldername = os.path.basename(backupFolderId)
        # give an error if any of the folder is not found
        if offsiteFoldername == None:
            addLog(f"Error: Offsite folder not found")
            exit()
        if primaryFoldername == None:
            addLog(f"Error: Primary folder not found")
            exit()
        if backupFoldername == None:
            addLog(f"Error: Backup folder not found")
            exit()
        # give error if all three names are not same
        if offsiteFoldername != primaryFoldername or offsiteFoldername != backupFoldername:
            addLog(f"Offsite folder name : {offsiteFoldername}")
            addLog(f"Primary folder name : {primaryFoldername}")
            addLog(f"Backup folder name : {backupFoldername}")
            addLog(f"Error: Folder names are not same")
            exit()
        
        # start the sync
        addLog("Syncing Primary to Backup...")
        insertedInPrimary, insertedInBackup = syncLocalFoldersRecursive(backupFolderId, primaryFolderId)
        addLog("Syncing Offsite to Primary...")
        tempInsertedInPrimary, insertedInOffsite = syncOnlineFoldersRecursive(offsiteFolderId, primaryFolderId)
        insertedInPrimary += tempInsertedInPrimary
        if tempInsertedInPrimary > 0:
            addLog(f"Inserted {insertedInPrimary} files in Primary, needs to be synced to backup")
            addLog("Syncing Primary to Backup...")
            tempInsertedInPrimary, tempInsertedInBackup = syncLocalFoldersRecursive(backupFolderId, primaryFolderId)
            insertedInPrimary += tempInsertedInPrimary
            insertedInBackup += tempInsertedInBackup
        addLog(f"Inserted {insertedInPrimary} files in Primary")
        addLog(f"Inserted {insertedInBackup} files in Backup")
        addLog(f"Inserted {insertedInOffsite} files in Offsite")
        addLog("Sync Completed")
    elif syncMode == 2:
        # Here we will need two folders, one local and one offsite
        offsiteFoldername = getDriveFolderName(offsiteFolderId)
        primaryFoldername = os.path.basename(primaryFolderId)
        # give an error if any of the folder is not found
        if offsiteFoldername == None:
            addLog(f"Error: Offsite folder not found")
            exit()
        if primaryFoldername == None:
            addLog(f"Error: Local folder not found")
            exit()
        # give error if both names are not same
        if offsiteFoldername != primaryFoldername:
            addLog(f"Offsite folder name : {offsiteFoldername}")
            addLog(f"Local folder name : {primaryFoldername}")
            addLog(f"Error: Folder names are not same")
            exit()
        addLog("Starting Offsite and Local Sync")
        insertedInPrimary, insertedInOffsite = syncOnlineFoldersRecursive(offsiteFolderId, primaryFolderId)
        addLog(f"downloaded {insertedInPrimary} files in Primary")
        addLog(f"uploaded {insertedInOffsite} files to Offsite")
        addLog("Offsite and Local Sync Completed")
    elif syncMode == 3:
        # Here we will need two folders, one local Primary and one local Backup
        primaryFoldername = os.path.basename(primaryFolderId)
        backupFoldername = os.path.basename(backupFolderId)
        # give an error if any of the folder is not found
        if primaryFoldername == None:
            addLog(f"Error: Primary folder not found")
            exit()
        if backupFoldername == None:
            addLog(f"Error: Backup folder not found")
            exit()
        # give error if both names are not same
        if primaryFoldername != backupFoldername:
            addLog(f"Primary folder name : {primaryFoldername}")
            addLog(f"Backup folder name : {backupFoldername}")
            addLog(f"Error: Folder names are not same")
            exit()
        addLog("Starting Local and Backup Sync")
        insertedInPrimary, insertedInBackup = syncLocalFoldersRecursive(backupFolderId, primaryFolderId)
        addLog(f"copied {insertedInPrimary} files in Primary")
        addLog(f"copied {insertedInBackup} files in Backup")
        addLog("Local and Backup Sync Completed")

def getDriveFolderName(folderId):
    folder = drive.CreateFile({'id': folderId})
    return folder['title']
  
def getDriveFolderItemsCountAndSizeRecursive(folderId):
    itemsCount = 0
    itemsSize = 0
    file_list = drive.ListFile({'q': f"'{folderId}' in parents and trashed=false"}).GetList()
    for file in file_list:
        if file['mimeType'] == "application/vnd.google-apps.folder":
            tempItemsCount, tempItemsSize = getDriveFolderItemsCountAndSizeRecursive(file['id'])
            itemsCount += tempItemsCount
            itemsSize += tempItemsSize
        else:
            itemsCount += 1
            itemsSize += int(file['fileSize'])
    return itemsCount, itemsSize
def syncOnlineFoldersRecursive(offsite, primary):
    insertedInPrimary = 0
    insertedInOffsite = 0
    # Auto-iterate through all files in the folders
    offsiteList = drive.ListFile({'q': f"'{offsite}' in parents and trashed=false"}).GetList();
    primaryList = os.listdir(primary);

    # get all list of files in offsite
    offsiteFileList = [];
    offsiteFileIds = {};
    for file in offsiteList:
        if file['mimeType'] != 'application/vnd.google-apps.folder':
            offsiteFileList.append(file['title']);
            offsiteFileIds[file['title']] = file['id'];
    # get all list of files in primary
    primaryFileList = [];
    for file in primaryList:
        if os.path.isfile(os.path.join(primary, file)):
            primaryFileList.append(file);

    print(f"In Folder {primary}")
    # compare offsite and primary
    for offsiteFile in offsiteFileList:
        if offsiteFile not in primaryFileList: # file is not in primary, download file from offsite
            logMessage = f"File {offsiteFile} is not in primary, downloading file from offsite"
            addLog(logMessage);
            driveFile = drive.CreateFile({'id': offsiteFileIds[offsiteFile]});
            driveFile.GetContentFile(os.path.join(primary, offsiteFile));
            logMessage = f"Downloaded {offsiteFile} from offsite to primary"
            insertedInPrimary += 1
            addLog(logMessage);
    for primaryFile in primaryFileList:
        if primaryFile not in offsiteFileList: # file is not in offsite, upload file to offsite
            logMessage = f"File {primaryFile} is not in offsite, uploading file to offsite"
            addLog(logMessage);
            driveFile = drive.CreateFile({'parents': [{'id': offsite}], 'title': primaryFile});
            driveFile.SetContentFile(os.path.join(primary, primaryFile));
            driveFile.Upload();
            logMessage = f"Uploaded {primaryFile} from primary to offsite"
            insertedInOffsite += 1
            addLog(logMessage);
    # at this point, all files in offsite and primary are the same
    
    # get all list of folders in offsite
    offsiteFolderList = [];
    offsiteFolderIds = {};
    for file in offsiteList:
        if file['mimeType'] == 'application/vnd.google-apps.folder':
            offsiteFolderList.append(file['title']);
            offsiteFolderIds[file['title']] = file['id'];
    # get all list of folders in primary
    primaryFolderList = [];
    for file in primaryList:
        if os.path.isdir(os.path.join(primary, file)):
            primaryFolderList.append(file);
    
    # compare offsite and primary
    for offsiteFolder in offsiteFolderList:
        if offsiteFolder not in primaryFolderList:  # folder is not in primary, create folder in primary
            os.mkdir(os.path.join(primary, offsiteFolder));
            primaryFolderList.append(offsiteFolder);
            logMessage = f"Created folder {offsiteFolder} in primary"
            insertedInPrimary += 1
            addLog(logMessage);
    for primaryFolder in primaryFolderList:
        if primaryFolder not in offsiteFolderList: # folder is not in offsite, create folder in offsite
            driveFolder = drive.CreateFile({'parents': [{'id': offsite}], 'title': primaryFolder, 'mimeType': 'application/vnd.google-apps.folder'});
            driveFolder.Upload();
            # get the id of the newly created folder
            offsiteFolderList.append(driveFolder['title']);
            offsiteFolderIds[driveFolder['title']] = driveFolder['id'];
            logMessage = f"Created folder {primaryFolder} in offsite"
            insertedInOffsite += 1
            addLog(logMessage);
    # at this point, all folders in offsite and primary are the same
    # now, recursively call syncOnlineFoldersRecursive for all folders in offsite and primary
    for offsiteFolder in offsiteFolderList:
        if offsiteFolder in primaryFolderList:
            insertedInPrimaryTemp, insertedInOffsiteTemp = syncOnlineFoldersRecursive(offsiteFolderIds[offsiteFolder], os.path.join(primary, offsiteFolder));
            insertedInPrimary += insertedInPrimaryTemp;
            insertedInOffsite += insertedInOffsiteTemp;
    return insertedInPrimary, insertedInOffsite
def syncLocalFoldersRecursive(backup, primary):
    insertedInPrimary = 0
    insertedInBackup = 0

    # get all list of files in backup and primary
    primaryList = os.listdir(primary);
    backupList = os.listdir(backup);

    # get all list of files in backup
    backupFileList = [];
    for file in backupList:
        if os.path.isfile(os.path.join(backup, file)):
            backupFileList.append(file);

    # get all list of files in primary
    primaryFileList = [];
    for file in primaryList:
        if os.path.isfile(os.path.join(primary, file)):
            primaryFileList.append(file);

    print(f"In Folder {primary}")
    # compare backup and primary
    for backupFile in backupFileList:
        if backupFile not in primaryFileList:
            logMessage = f"File {backupFile} is not in primary, copying file from backup to primary"
            addLog(logMessage);
            shutil.copy(os.path.join(backup, backupFile), os.path.join(primary, backupFile));
            logMessage = f"Copied {backupFile} from backup to primary"
            insertedInPrimary += 1
            addLog(logMessage);
    
    for primaryFile in primaryFileList:
        if primaryFile not in backupFileList:
            logMessage = f"File {primaryFile} is not in backup, copying file from primary to backup"
            addLog(logMessage);
            shutil.copy(os.path.join(primary, primaryFile), os.path.join(backup, primaryFile));
            logMessage = f"Copied {primaryFile} from primary to backup"
            insertedInBackup += 1
            addLog(logMessage);
    # at this point, all files in backup and primary are the same

    # get all list of folders in backup and primary
    primaryFolderList = [];
    for file in primaryList:
        if os.path.isdir(os.path.join(primary, file)):
            primaryFolderList.append(file);
    backupFolderList = [];
    for file in backupList:
        if os.path.isdir(os.path.join(backup, file)):
            backupFolderList.append(file);
    
    # compare backup and primary
    for backupFolder in backupFolderList:
        if backupFolder not in primaryFolderList:
            os.mkdir(os.path.join(primary, backupFolder));
            primaryFolderList.append(backupFolder);
            logMessage = f"Created folder {backupFolder} in primary"
            insertedInPrimary += 1
            addLog(logMessage);
    for primaryFolder in primaryFolderList:
        if primaryFolder not in backupFolderList:
            os.mkdir(os.path.join(backup, primaryFolder));
            backupFolderList.append(primaryFolder);
            logMessage = f"Created folder {primaryFolder} in backup"
            insertedInBackup += 1
            addLog(logMessage);
    
    # at this point, all folders in backup and primary are the same
    # now, recursively call syncLocalFoldersRecursive for all folders in backup and primary
    for backupFolder in backupFolderList:
        if backupFolder in primaryFolderList:
            insertedInPrimaryTemp, insertedInBackupTemp = syncLocalFoldersRecursive(os.path.join(backup, backupFolder), os.path.join(primary, backupFolder));
            insertedInPrimary += insertedInPrimaryTemp;
            insertedInBackup += insertedInBackupTemp;
    
    return insertedInPrimary, insertedInBackup

def addLog(logMessage):
    print(logMessage)
    if not os.path.exists("logs"):
        os.mkdir("logs");
    if not os.path.exists(f"logs/{syncTime}.log"):
        open(f"logs/{syncTime}.log", "w", encoding='utf-8').close();
    with open(f"logs/{syncTime}.log", "a", encoding='utf-8') as outfile:
        # append to the file
        outfile.writelines(f"{datetime.datetime.now()} -> {logMessage}\n")


if __name__ == '__main__':
    main()