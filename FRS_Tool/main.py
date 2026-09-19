import globals
import sys

print("\n***Python Bulk Import Utility***")
confirmorg = input(f"\nYou are currently connected to \"{globals.org}\". If this is not expected, please exit. Otherwise hit any key to continue.\n")
menuChoice=input("For Queues press 1\nFor Groups press 2\nFor Data Action > Flow Dependencies Mapping press 3\nFor Script Details press 4\nSELECTION: ")


def promptForInput(objectType):
    while True:
        file_path=input(f"Please specify the {objectType} file path: ")    
        globals.userInputCreate = input(f"Would you like to create {objectType} or update {objectType} settings? 1 for CREATE or 2 for UPDATE: ")
        if globals.userInputCreate == "1":
            #This prevents the script from errroring in def:update_group when the csv has blank values while in create mode. 
            globals.userInputClear = ""
            return file_path
        elif globals.userInputCreate == "2":
            globals.userInputClear = input(f"Would you like to reset {objectType} settings for blank values in the CSV? 1 for YES or 2 for NO: ")
            if globals.userInputClear == "1" or globals.userInputClear == "2":
                return file_path
            else:
                print("\nInvalid Selection. Please Try Again.\n")
        else:
            print("\nInvalid Selection. Please Try Again.\n")

if menuChoice == "1":
    resultsFile=input("Would you like to generate a results file?\nPress 1 for YES\nPress 2 for NO\nSELECTION: ")
    if resultsFile == "1":
        bResultsFile = True
    elif resultsFile == "2":
        bResultsFile = False
    else:
        bResultsFile = False
        print("No selection or invalid selection. Defaulting to NO")
    file_path = promptForInput("Queues")
    apiCounter = 0
    #sys.argv[1]
    from queues import update_queue_from_csv
    update_queue_from_csv(file_path,apiCounter,bResultsFile)
elif menuChoice == "2":
    resultsFile=input("Would you like to generate a results file?\nPress 1 for YES\nPress 2 for NO\nSELECTION: ")
    if resultsFile == "1":
        bResultsFile = True
    elif resultsFile == "2":
        bResultsFile = False
    else:
        bResultsFile = False
        print("No selection or invalid selection. Defaulting to NO")
    file_path = promptForInput("Groups")
    apiCounter = 0
    #sys.argv[1]
    from groups import update_group_from_csv
    update_group_from_csv(file_path,apiCounter,bResultsFile)
elif menuChoice == "3":
    from architectDependency.dataActions import Dependencies
    Dependencies()
elif menuChoice == "4":
    from scriptExport import Scripts
    Scripts()
else:
    print("\nInvalid Selection. Exiting.\n")