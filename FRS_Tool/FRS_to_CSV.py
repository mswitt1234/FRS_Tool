import pandas as pd
import os
from CSVDataManager import CSVDataManager
from datetime import datetime
# from utility_functions import create_roles, create_skill_string
import argparse


def main(excel_file, sheet_name_to_process): 
    # Load the Excel file
    workbook = pd.ExcelFile(excel_file)

    # Get the current date and time
    now = datetime.now()
    date_time_suffix = now.strftime('%Y%m%d_%H%M')

    # Target CSV file
    file_path = f".\\Output\\Output_{date_time_suffix}.csv"
    data_manager = CSVDataManager(file_path)

    print(f"\nProcessing, Please wait...")

    # Loop through each sheet and save it as a CSV file in the specified directory
    for sheet_name in workbook.sheet_names:
        if sheet_name_to_process == sheet_name:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            # Step 1: reset count
            total_processed_rows = 0
            # Step 2: iterate through all rows
            print(f"> Processing Sheet: {sheet_name}")
            bullseye = False
            cgr = False
            for index, row in df.iterrows():
                print(f">> Processing Row: {row["Queue Name"]}")
                # Process Bullseye\Group Routing
                if sheet_name == "BullseyeQueues":
                    bullseye = True
                    howManyIndex = 1
                    maxRings = 6
                    totalRings = 0
                    while howManyIndex <= maxRings:
                        isNotSet = df[f"{howManyIndex} BR EX"].isna()
                        if isNotSet[index] == False:
                            totalRings = totalRings + 1
                        howManyIndex = howManyIndex + 1
                    howManyIndex = 1
                    while howManyIndex <= totalRings:
                        isNotSet = df[f"{howManyIndex} BR TO"].isna()
                        if isNotSet[index] == True:
                            print(f"\nERROR: The Bullseye Expression is populated, but no value for column \"{howManyIndex} BR TO\"\n")
                            exit()
                        try:
                            if howManyIndex == 1:
                                ring = f"{row[f"{howManyIndex} BR EX"]}:{row[f"{howManyIndex} BR TO"]}:{row[f"{howManyIndex} BR Skills"]}"
                                memberGroups = f"{row[f"{howManyIndex} BR SG"]},{row[f"{howManyIndex} BR MG"]}"
                            else:
                                ring = f"{ring},{row[f"{howManyIndex} BR EX"]}:{row[f"{howManyIndex} BR TO"]}:{row[f"{howManyIndex} BR Skills"]}"
                                memberGroups = f"{memberGroups}|{row[f"{howManyIndex} BR SG"]},{row[f"{howManyIndex} BR MG"]}"
                            # print(f"row {index}, rule {howManyIndex} captured")
                        except:
                            print(f"\nERROR: Column Header mismatch for Group Routing related columns. Double check that there are no trailing or leading spaces/whitespace. Exiting...\n")
                            exit()
                        howManyIndex = howManyIndex + 1
                elif sheet_name == "CGRQueues":
                    cgr = True
                    howManyIndex = 1
                    maxRules = 6
                    totalRules = 0
                    while howManyIndex <= maxRules:
                        isNotSet = df[f"{howManyIndex} CGR Metric"].isna()
                        if isNotSet[index] == False:
                            totalRules = totalRules + 1
                        howManyIndex = howManyIndex + 1
                    howManyIndex = 1
                    while howManyIndex <= totalRules:
                        isNotSet = df[f"{howManyIndex} CGR Operator"].isna()
                        if isNotSet[index] == True:
                            print(f"\nERROR: The GroupRouting Metric is populated, but no value for column \"{howManyIndex} CGR Operator\"\n")
                            exit()
                        isNotSet = df[f"{howManyIndex} CGR Value"].isna()
                        if isNotSet[index] == True:
                            print(f"\nERROR: The GroupRouting Metric is populated, but no value for column \"{howManyIndex} CGR Value\"\n")
                            exit()   
                        try:
                            if howManyIndex == 1:
                                rule = f"{row[f"{howManyIndex} CGR Metric"]}:{row[f"{howManyIndex} CGR Operator"]}:{row[f"{howManyIndex} CGR Value"]}:{row[f"{howManyIndex} CGR Wait Sec."]}"
                                memberGroups = f"{row[f"{howManyIndex} CGR SG"]},{row[f"{howManyIndex} CGR MG"]}"
                            else:
                                rule = f"{rule},{row[f"{howManyIndex} CGR Metric"]}:{row[f"{howManyIndex} CGR Operator"]}:{row[f"{howManyIndex} CGR Value"]}:{row[f"{howManyIndex} CGR Wait Sec."]}"
                                memberGroups = f"{memberGroups}|{row[f"{howManyIndex} CGR SG"]},{row[f"{howManyIndex} CGR MG"]}"
                            # print(f"row {index}, rule {howManyIndex} captured")
                        except:
                            print(f"\nERROR: Column Header mismatch for Group Routing related columns. Double check that there are no trailing or leading spaces/whitespace. Exiting...\n")
                            exit()
                        howManyIndex = howManyIndex + 1
                if cgr:
                    new_data = {
                        'groupRouting': rule,
                        'MemberGroups': memberGroups
                    }
                if bullseye:
                    new_data = {
                        'bullseye': ring,
                        'MemberGroups': memberGroups
                    }
                data_manager.add_data([new_data])
                total_processed_rows += 1           
            print(f"> Completed Processing sheet: {sheet_name} | Total Processed Rows: {total_processed_rows}")
            print(f"> Generated CSV File Name: {file_path}")
        # else:
            # print(f"Skipped sheet: {sheet_name}")

    # Save the updated data to the CSV file
    data_manager.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process user data from an Excel file and generate a CSV file.")
    parser.add_argument("--excel_file", type=str, default="FRS_Workbook_for_scripting.xlsx",
                        help="Name of the Excel file with extension. Eg: master-user-list-2024-08-14.xlsx")
    parser.add_argument("--sheet_name_to_process", type=str, default="CGRQueues",
                        help="Specific sheet name to process.Eg: users")

    args = parser.parse_args()
    main(args.excel_file, args.sheet_name_to_process)
