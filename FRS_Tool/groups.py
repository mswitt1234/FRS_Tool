import globals, datetime
import pandas as pd
## Import requests because the python SDK is not aware of the "calls_enabled" API request parameter. We have to use the "requests" package.
import requests

## These next two lines are here specifically because the python SDK is not aware of the "calls_enabled" API request parameter. We have to use the "requests" package. 
api_client2 = globals.gc.ApiClient().get_client_credentials_token(globals.client_id, globals.client_secret)
requestHeaders = {
    "Authorization": f"Bearer {api_client2.access_token}"
}



def update_group(group: globals.gc.Group, type: str, visibility: str, include_owners:str, enable_calls: str, extension: str, call_route_type: str, route_calls: str, stop_ringing: str, overflow: str, overflow_targer: str, voicemail: str, greeting: str, email_notification: str, members: str, oweners: str, apiCounter: int):
    
    group_api = globals.gc.GroupsApi(globals.api_client)
    voicemail_api = globals.gc.VoicemailApi(globals.api_client)
    if globals.userInputCreate == "1":
        print(f"GROUP: {group.name}")
    elif globals.userInputCreate == "2":
        print(f"GROUP: {group.name}")
    
    if type == "pass":
        if globals.userInputClear == "1":
            print("can't clear type, skipping")
        else:
            pass
    else:
        group.type = type.lower()

    if visibility == "pass":
        if globals.userInputClear == "1":
            print("Can't clear visibility, skipping")
        else:
            pass
    else:
        group.visibility = visibility.lower() 
    
    if oweners == "pass":
        if globals.userInputClear == "1":
            print("Can't fully clear owner membership, skipping")
        else:
            pass
    else:
        users_api = globals.gc.UsersApi(globals.api_client)
        search = globals.gc.UserSearchCriteria()
        tosearch = oweners.split(",")
        #print(tosearch)
        search.values = tosearch
        search.fields = ["name"]
        search.type = "EXACT"
        users: globals.gc.UsersSearchResponse = users_api.post_users_search(search)
        apiCounter = apiCounter +1
        userlist = []
        userIndex = 0
        while userIndex < len(users.results):
            #owner = globals.gc.Entity()
            #owner.id = users.results[userIndex].id
            userlist.append(users.results[userIndex].id)
            userIndex = userIndex + 1
        #print(userlist)
        group.owners = userlist  

    groupContact = globals.gc.GroupContact()
    if extension == "pass":
        if globals.userInputClear == "1":
            groupContact.extension = None  
        else:
            pass 
    else:
        groupContact.extension = extension
        groupContact.display = f"({extension})"
        groupContact.type = "GROUPRING"
        groupContact.media_type = "PHONE"
    group.addresses = [groupContact]

    if enable_calls == "pass":
        if globals.userInputClear == "1":
            enable_calls = False
        else:
            enable_calls = bool(enable_calls)
    request_body = [
            {
                "callsEnabled": enable_calls
            }
        ]

    groupPut = globals.gc.VoicemailGroupPolicy()
    groupPut.name = group.name

    if call_route_type == "pass":
        if globals.userInputClear == "1":
            groupPut.group_alert_type = "RANDOM"
        else:
            pass
    else:
        groupPut.group_alert_type = call_route_type

    if voicemail == "pass":
        if globals.userInputClear == "1":
            groupPut.enabled = False
        else:
            pass
    else:
        groupPut.enabled = bool(voicemail)
    
    if email_notification == "pass":
        if globals.userInputClear == "1":
            groupPut.send_email_notifications = False
        else:
            pass
    else:
        groupPut.send_email_notifications = bool(email_notification)
    
    groupPut.disable_email_pii = False
    groupPut.include_email_transcriptions = False

    #print(group)
    if globals.userInputCreate == "1":
        responsePost = group_api.post_groups(group)
        apiCounter = apiCounter +1
        responseenablecall = requests.put(f"https://api.{globals.env}/api/v2/groups/{responsePost.id}", json=request_body[0], headers=requestHeaders)
        apiCounter = apiCounter + 1
        
        if responseenablecall.status_code == 200:
            if enable_calls == True:
                print("> Calls Enabled")
            else:
                print("> Calls Disabled")
        else:
            print(f"> Error enabling/disbling calls >> API ERROR {responseenablecall.content}")
        reponseVoicemail = voicemail_api.patch_voicemail_group_policy(responsePost.id, groupPut)
        apiCounter = apiCounter +1
        if reponseVoicemail.group.id == responsePost.id:
            print("> Voicemail Applied")

        print(f"> CREATED")
    elif globals.userInputCreate == "2":
        responsePut = group_api.put_group(group.id, body=group)
        responseenablecall = requests.put(f"https://api.{globals.env}/api/v2/groups/{responsePut.id}", json=request_body[0], headers=requestHeaders)
        apiCounter = apiCounter +1
        if responseenablecall.status_code == 200:
            if enable_calls == True:
                print("> Calls Enabled")
            else:
                print("> Calls Disabled")
        else:
            print(f"> Error enabling/disbling calls >> API ERROR {responseenablecall}")
        reponseVoicemail = voicemail_api.patch_voicemail_group_policy(responsePut.id, groupPut)
        apiCounter = apiCounter +1
        if reponseVoicemail.group.id == responsePut.id:
            print("> Voicemail Applied")
        print(f"> UPDATED")
    return apiCounter

def fetch_all_groups() -> {}: # type: ignore
    group_api = globals.gc.GroupsApi(globals.api_client)
    routing_api = globals.gc.RoutingApi(globals.api_client)
    page_number = 1
    groups_info = {}
    print(f"\nFETCHING ALL GROUPS INFO")
    while True:
        response: globals.gc.GroupEntityListing = group_api.get_groups(page_number=page_number, page_size=100)
        for group in response.entities:
            groups_info.update({group.name: group})
        #print(f"GOT GROUPS FROM PAGE: {page_number} ")
        page_number += 1
        #print(f"GETTING NEXT PAGE: {page_number}...")
        print("...")
        if page_number > response.page_count:
            print("...DONE\n")
            break
    return groups_info


def update_group_from_csv(file_path, apiCounter):
    data_frame = pd.read_csv(file_path, sep=",")
    groups_info: {} = fetch_all_groups() # type: ignore
    startTime = datetime.datetime.now()
    startTime1 = startTime.strftime("%d/%m/%Y %H:%M:%S")
    for index, row in data_frame.iterrows():
        current_group = row["Group_Name"]

        isNotSet = data_frame["Type"].isna()
        if isNotSet[index]:
            current_type = "pass"
        else:
            current_type = row["Type"]

        isNotSet = data_frame["Visibility"].isna()
        if isNotSet[index]:
            current_Visibility = "pass"
        else:
            current_Visibility = row["Visibility"]

        isNotSet = data_frame["Include_owners"].isna()
        if isNotSet[index]:
            current_Include_owners = "pass"
        else:
            current_Include_owners = row["Include_owners"]

        isNotSet = data_frame["Enable_Calls"].isna()
        if isNotSet[index]:
            current_Enable_Calls = "pass"
        else:
            current_Enable_Calls = row["Enable_Calls"]

        isNotSet = data_frame["Extension"].isna()
        if isNotSet[index]:
            current_Extension = "pass"
        else:
            current_Extension = row["Extension"]

        isNotSet = data_frame["Call_Route_Type"].isna()
        if isNotSet[index]:
            current_Call_Route_Type = "pass"
        else:
            current_Call_Route_Type = row["Call_Route_Type"]

        isNotSet = data_frame["Rotate_Calls"].isna()
        if isNotSet[index]:
            current_Rotate_Calls = "pass"
        else:
            current_Rotate_Calls = row["Rotate_Calls"]

        isNotSet = data_frame["Stop_Ringing"].isna()
        if isNotSet[index]:
            current_Stop_Ringing = "pass"
        else:
            current_Stop_Ringing = row["Stop_Ringing"]
        
        isNotSet = data_frame["Overflow"].isna()
        if isNotSet[index]:
            current_Overflow = "pass"
        else:
            current_Overflow = row["Overflow"]

        isNotSet = data_frame["Overflow_Target"].isna()
        if isNotSet[index]:
            current_Overflow_Target = "pass"
        else:
            current_Overflow_Target = row["Overflow_Target"]
        
        isNotSet = data_frame["Voicemail"].isna()
        if isNotSet[index]:
            current_Voicemail = "pass"
        else:
            current_Voicemail = row["Voicemail"]
        
        isNotSet = data_frame["Greeting"].isna()
        if isNotSet[index]:
            current_Greeting = "pass"
        else:
            current_Greeting = row["Greeting"]

        isNotSet = data_frame["Email_Notification"].isna()
        if isNotSet[index]:
            current_Email_Notification = "pass"
        else:
            current_Email_Notification = row["Email_Notification"]

        isNotSet = data_frame["Members"].isna()
        if isNotSet[index]:
            current_Members = "pass"
        else:
            current_Members = row["Members"]

        isNotSet = data_frame["Owners"].isna()
        if isNotSet[index]:
            current_Owners = "pass"
        else:
            current_Owners = row["Owners"]

        if globals.userInputCreate == "1":
            if current_group not in groups_info:
                groups_info = {}
                groupCreate = globals.gc.Group()
                groupCreate.name = row["Group_Name"]
                groups_info.update({groupCreate.name: groupCreate})
                apiCounter = update_group(groups_info[current_group], current_type, current_Visibility, current_Include_owners, current_Enable_Calls, current_Extension, current_Call_Route_Type, current_Rotate_Calls, current_Stop_Ringing, current_Overflow, current_Overflow_Target, current_Voicemail, current_Greeting, current_Email_Notification, current_Members, current_Owners, apiCounter)
            else:
                print(f"GROUP: {current_group} ALREADY EXISTS. USE UPDATE OPTION INSTEAD")
        elif globals.userInputCreate == "2":
            if current_group in groups_info:
                apiCounter = update_group(groups_info[current_group], current_type, current_Visibility, current_Include_owners, current_Enable_Calls, current_Extension, current_Call_Route_Type, current_Rotate_Calls, current_Stop_Ringing, current_Overflow, current_Overflow_Target, current_Voicemail, current_Greeting, current_Email_Notification, current_Members, current_Owners, apiCounter)
            else:
                print(f"GROUP: {current_group} NOT FOUND, USE CREATE OPTION INSTEAD")

    endTime = datetime.datetime.now()
    endTime1 = endTime.strftime("%d/%m/%Y %H:%M:%S")
    totalDuration = endTime - startTime
    print(f"\n<<< PROCESSED ALL >>>")
    print(f"<<< START:    {startTime1} >>>")
    print(f"<<< END:      {endTime1} >>>")
    print(f"<<< APPROX. Duration:  {str(round(totalDuration.seconds) / 60)[:2].replace('.','')} MIN {str(round(totalDuration.seconds / 60,2))[-2:].replace('.','')} SEC >>>") 
    print(f"<<< APPROX. API CALLS: {apiCounter} >>>\n")
