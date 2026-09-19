import time
from PureCloudPlatformClientV2.rest import ApiException
import globals, datetime
import pandas as pd

def update_queue(queue: globals.gc.Queue, acw: str, queueflow: str, routingRules:str, callScript: str, bullseye: str, memberGroups: str, evaluation: str, caller_id_num: str, caller_id_name: str,
                 alertingTimeoutSeconds: str, slPercentage: str, slDuration_ms: str, division: str, group_Routing: str, apiCounter: int, description: str, enableTranscription: str,
                 enableManualAssignment: str, suppressInQueueCallRecording: str, callBackMode: str, callbackLiveVoice: str, callbackLiveVoiceFlow: str, callbackAnswerMachine: str, callbackAnswerMachineFlow: str,
                 enableAutoAnswerVoice: str, enableAutoAnswerAll: str, cannedResponses: str, cb_alertingTimeoutSeconds: str, cb_slPercentage: str, cb_slDuration_ms: str,
                 email_slPercentage: str, email_slDuration_ms: str, email_alertingTimeoutSeconds: str, email_in_queue_flow: str, emailScript: str, emailAddress: str, emailDomain: str,
                 wrapUpCodes: str, scoreMethod: str):
    global prebuilt
    global resultsFile
    global bResultsFile
    routing_api = globals.gc.RoutingApi(globals.api_client)
    queueDivision = globals.gc.NamedEntity()
    if division == "pass":
        if globals.userInputClear == "1":
            auth_api = globals.gc.AuthorizationApi(globals.api_client)
            responseL: globals.gc.AuthzDivisionEntityListing = auth_api.get_authorization_divisions(name = "Home")
            apiCounter = apiCounter + 1
            queueDivision.name = "Home"
            queueDivision.id = responseL.entities[0].id
            queue.division = queueDivision
        else:
            pass
    else:
        queueDivisionName = division
        auth_api = globals.gc.AuthorizationApi(globals.api_client)
        responseL: globals.gc.AuthzDivisionEntityListing = auth_api.get_authorization_divisions(name = queueDivisionName)
        apiCounter = apiCounter + 1
        queueDivision.name = queueDivisionName
        divisionIndex = 0
        try:
            queueDivision.id = responseL.entities[0].id
        except:
            print(f"> ERROR: The Division: \"{queueDivisionName}\" may not exist. Skipping")
            if bResultsFile:
                with open(resultsFile, 'a') as rFile:
                    rFile.write(f"> ERROR: The Division: \"{queueDivisionName}\" may not exist. Skipping\n")
            return apiCounter
        while divisionIndex < len(responseL.entities):
            if queueDivisionName == responseL.entities[divisionIndex].name:
                queueDivision.id = responseL.entities[divisionIndex].id
                queue.division = queueDivision    
            divisionIndex = divisionIndex + 1
    if description == "pass":
        if globals.userInputClear == "1":
            queue.description = ""
        else:
            pass
    else:
        queue.description = description
    bulls_eye = globals.gc.Bullseye()
    if bullseye == "pass":
        if globals.userInputClear == "1":
            queue.bullseye = {}
        elif memberGroups == "pass":
            if globals.userInputClear == "1":
                queue.member_groups = None
            else:
                pass
        else:
            queue.bullseye = {}
            divisionT = globals.gc.NamedEntity()
            members = memberGroups.split(",")
            memberIndex = 0
            memberlist = []
            if group_Routing != "pass":
                pass
            else:
                while memberIndex < len(members):
                    memberGroup = globals.gc.MemberGroup()    
                    skillgroupname,divisionname = members[memberIndex].split(":")
                    if divisionname == "none":
                        group_api = globals.gc.GroupsApi(globals.api_client)
                        groupSearch = globals.gc.GroupSearchRequest()
                        groupSearchCriteria = globals.gc.GroupSearchCriteria()
                        groupSearchCriteria.fields = ["name"]
                        groupSearchCriteria.type = "EXACT"
                        groupSearchCriteria.value = skillgroupname                    
                        groupSearch.query = [groupSearchCriteria]                  
                        responseF: globals.gc.GroupsSearchResponse = group_api.post_groups_search(groupSearch)
                        apiCounter = apiCounter + 1
                        memberGroup.type = "GROUP"
                        memberGroup.name = skillgroupname
                        memberGroup.id = responseF.results[0].id
                    else:
                        auth_api = globals.gc.AuthorizationApi(globals.api_client)
                        responseD: globals.gc.AuthzDivisionEntityListing = auth_api.get_authorization_divisions(name = divisionname)
                        apiCounter = apiCounter + 1
                        divisionT.name = divisionname
                        divisionT.id = responseD.entities[0].id
                        memberGroup.type = "SKILLGROUP"
                        memberGroup.division = divisionT
                        routing_api = globals.gc.RoutingApi(globals.api_client)
                        responseS: globals.gc.SkillGroupEntityListing = routing_api.get_routing_skillgroups(name = skillgroupname)
                        skillGroupIndex = 0
                        try:
                            len(responseS.entities) == 0
                        except:    
                            print(f"> ERROR: No Skill Expression Groups Found. Skipping {queue.name}")
                            if bResultsFile:
                                with open(resultsFile, 'a') as rFile:
                                    rFile.write(f"> ERROR: No Skill Expression Groups Found. Skipping {queue.name}\n")
                            return apiCounter
                        while skillGroupIndex < len(responseS.entities):
                            if skillgroupname == responseS.entities[skillGroupIndex].name:
                                memberGroup.id = responseS.entities[skillGroupIndex].id
                                break
                            skillGroupIndex = skillGroupIndex + 1
                        apiCounter = apiCounter + 1
                        memberGroup.name = skillgroupname
                        try:
                            memberGroup.id = responseS.entities[skillGroupIndex].id
                        except:
                            print(f"> ERROR: The Skill Expression Group \"{skillgroupname}\" may not exist. Skipping {queue.name}")
                            if bResultsFile:
                                with open(resultsFile, 'a') as rFile:
                                    rFile.write(f"> ERROR: The Skill Expression Group \"{skillgroupname}\" may not exist. Skipping {queue.name}\n")
                            return apiCounter
                    memberlist.append(memberGroup)
                    memberIndex = memberIndex + 1
                queue.member_groups = memberlist
    else:
        queue.conditional_group_routing = {}
        queue.member_groups = None
        rings = bullseye.split(",")
        if len(memberGroups.split("|")) >=2:
            members = memberGroups.split("|")
            many = True    
        else:
            members = memberGroups.split(",")
            many = False
        ringlist = []
        index = 0
        while index < len(rings):
            ring = globals.gc.Ring()
            expansion = globals.gc.ExpansionCriterium()
            try:
                exptype, expthreshold = rings[index].split(":")
                actionB = False
            except:
                exptype, expthreshold, skillToRemove = rings[index].split(":")
                actionB = True
            expansion.type = exptype
            expansion.threshold = expthreshold
            ring.expansion_criteria = [expansion]
            if actionB == True:
                action = globals.gc.Actions()
                removelist = []
                skillremoveindex = 0
                while skillremoveindex < len(skillToRemove.split("|")):
                    skillToRemoveList = skillToRemove.split("|")
                    skillRemove = globals.gc.SkillsToRemove()
                    routing_api = globals.gc.RoutingApi(globals.api_client)
                    responseY: globals.gc.SkillGroupEntityListing = routing_api.get_routing_skills(name = skillToRemoveList[skillremoveindex])
                    apiCounter = apiCounter + 1
                    skillRemove.name = skillToRemoveList[skillremoveindex]
                    try:
                        skillRemove.id = responseY.entities[0].id
                    except:
                        print(f"> ERROR: The Skill \"{skillToRemoveList[skillremoveindex]}\" may not exist.")
                        if bResultsFile:
                            with open(resultsFile, 'a') as rFile:
                                rFile.write(f"> ERROR: The Skill \"{skillToRemoveList[skillremoveindex]}\" may not exist.\n")
                        return apiCounter
                    removelist.append(skillRemove)
                    action.skills_to_remove = removelist
                    skillremoveindex = skillremoveindex + 1
                ring.actions = action
            if memberGroups == "pass":
                if globals.userInputClear == "1":
                    queue.member_groups = None
                else:
                    pass
            else:               
                divisionT = globals.gc.NamedEntity()
                if many == True:
                    members[index] = members[index].split(",")
                    stopLoop = len(members[index])
                else:
                    stopLoop = 1
                memberIndex = 0
                memberlist = []
                while memberIndex < stopLoop:
                    memberGroup = globals.gc.MemberGroup()    
                    if many == True:
                        try:
                            skillgroupname,divisionname = members[index][memberIndex].split(":")
                            skipgroup = False
                        except:
                            skipgroup = True
                    else:
                        skillgroupname,divisionname = members[index].split(":")
                        skipgroup = False
                    if skipgroup != True:
                        if divisionname == "none":
                            group_api = globals.gc.GroupsApi(globals.api_client)
                            groupSearch = globals.gc.GroupSearchRequest()
                            groupSearchCriteria = globals.gc.GroupSearchCriteria()
                            groupSearchCriteria.fields = ["name"]
                            groupSearchCriteria.type = "EXACT"
                            groupSearchCriteria.value = skillgroupname
                            groupSearch.query = [groupSearchCriteria]
                            responseF: globals.gc.GroupsSearchResponse = group_api.post_groups_search(groupSearch)
                            apiCounter = apiCounter + 1
                            memberGroup.type = "GROUP"
                            memberGroup.name = skillgroupname
                            try:
                                memberGroup.id = responseF.results[0].id
                            except:
                                print(f"> ERROR: The Group \"{skillgroupname}\" may not exist. Skipping.")
                                if bResultsFile:
                                    with open(resultsFile, 'a') as rFile:
                                        rFile.write(f"> ERROR: The Group \"{skillgroupname}\" may not exist. Skipping.\n")
                                return apiCounter
                        else:
                            auth_api = globals.gc.AuthorizationApi(globals.api_client)
                            responseD: globals.gc.AuthzDivisionEntityListing = auth_api.get_authorization_divisions(name = divisionname)
                            apiCounter = apiCounter + 1
                            divisionT.name = divisionname
                            divisionT.id = responseD.entities[0].id
                            memberGroup.type = "SKILLGROUP"
                            memberGroup.division = divisionT
                            routing_api = globals.gc.RoutingApi(globals.api_client)
                            responseS: globals.gc.SkillGroupEntityListing = routing_api.get_routing_skillgroups(name = skillgroupname)
                            skillGroupIndex = 0
                            try:
                                len(responseS.entities) == 0
                            except:    
                                print(f"> ERROR: No Skill Expression Groups Found. Skipping {queue.name}")
                                if bResultsFile:
                                    with open(resultsFile, 'a') as rFile:
                                        rFile.write(f"> ERROR: No Skill Expression Groups Found. Skipping {queue.name}\n")
                                return apiCounter
                            while skillGroupIndex < len(responseS.entities):
                                if skillgroupname == responseS.entities[skillGroupIndex].name:
                                    memberGroup.id = responseS.entities[skillGroupIndex].id
                                    break
                                skillGroupIndex = skillGroupIndex + 1
                            apiCounter = apiCounter + 1
                            memberGroup.name = skillgroupname
                            try:
                                memberGroup.id = responseS.entities[skillGroupIndex].id
                            except:
                                print(f"> ERROR: The Skill Expression Group \"{skillgroupname}\" may not exist. Skipping.")
                                if bResultsFile:
                                    with open(resultsFile, 'a') as rFile:
                                        rFile.write(f"> ERROR: The Skill Expression Group \"{skillgroupname}\" may not exist. Skipping.\n")
                                return apiCounter
                        memberlist.append(memberGroup)
                    memberIndex = memberIndex + 1
                ring.member_groups = memberlist
            ringlist.append(ring)
            index = index + 1  
        bulls_eye.rings = ringlist
        queue.bullseye = bulls_eye
    if alertingTimeoutSeconds == "pass":
        if globals.userInputClear == "1":
            queue.media_settings.call.alerting_timeout_seconds = "8"
            # mediaSettings.alerting_timeout_seconds = "8"
        else:
            if globals.userInputCreate == "2":
                pass
                # mediaSettings.alerting_timeout_seconds = queue.media_settings.call.alerting_timeout_seconds
    else:
        queue.media_settings.call.alerting_timeout_seconds = alertingTimeoutSeconds
        # mediaSettings.alerting_timeout_seconds = alertingTimeoutSeconds
        # queueMediaSettings.call = mediaSettings
    if slPercentage == "pass":
        if globals.userInputClear == "1":
            queue.media_settings.call.service_level.percentage = ".8"
        else:
            if globals.userInputCreate == "2":
                pass
                # serviceLevel.percentage = queue.media_settings.call.service_level.percentage
    else:
        queue.media_settings.call.service_level.percentage = slPercentage
        # mediaSettings.service_level = serviceLevel
    if slDuration_ms == "pass":
        if globals.userInputClear == "1":
            queue.media_settings.call.service_level.duration_ms = "20000"
        else:
            if globals.userInputCreate == "2":
                pass
                # serviceLevel.duration_ms = queue.media_settings.call.service_level.duration_ms
    else:
        queue.media_settings.call.service_level.duration_ms = slDuration_ms
        # mediaSettings.service_level = serviceLevel
    if cb_alertingTimeoutSeconds == "pass":
        if globals.userInputClear == "1":
            queue.media_settings.callback.alerting_timeout_seconds = "30"
        else:
            if globals.userInputCreate == "2":
                pass
    else:
        queue.media_settings.callback.alerting_timeout_seconds = cb_alertingTimeoutSeconds
    if cb_slPercentage == "pass":
        if globals.userInputClear == "1":
            queue.media_settings.callback.service_level.percentage = ".8"
        else:
            if globals.userInputCreate == "2":
                pass
    else:
        queue.media_settings.callback.service_level.percentage = cb_slPercentage
    if cb_slDuration_ms == "pass":
        if globals.userInputClear == "1":
            queue.media_settings.callback.service_level.duration_ms = "20000"
        else:
            if globals.userInputCreate == "2":
                pass
    else:
        queue.media_settings.callback.service_level.duration_ms = cb_slDuration_ms
    if email_alertingTimeoutSeconds == "pass":
        if globals.userInputClear == "1":
            queue.media_settings.email.alerting_timeout_seconds = "30"
        else:
            if globals.userInputCreate == "2":
                pass
    else:
        queue.media_settings.email.alerting_timeout_seconds = email_alertingTimeoutSeconds
    if email_slPercentage == "pass":
        if globals.userInputClear == "1":
            queue.media_settings.email.service_level.percentage = ".8"
        else:
            if globals.userInputCreate == "2":
                pass
    else:
        queue.media_settings.email.service_level.percentage = email_slPercentage
    if email_slDuration_ms == "pass":
        if globals.userInputClear == "1":
            queue.media_settings.email.service_level.duration_ms = "20000"
        else:
            if globals.userInputCreate == "2":
                pass
    else:
        queue.media_settings.email.service_level.duration_ms = email_slDuration_ms
    email_queue_flow = globals.gc.NamedEntity()
    if email_in_queue_flow == "pass":
        if globals.userInputClear == "1":
            queue.email_in_queue_flow = {}
        else:
            pass
    else:
        emailQueue_flowName = email_in_queue_flow
        ArchitectApi_api = globals.gc.ArchitectApi(globals.api_client)
        emailInQueueResponseFlow: globals.gc.FlowEntityListing = ArchitectApi_api.get_flows(name = emailQueue_flowName)

        if len(emailInQueueResponseFlow.entities) == 0:
            print(f"> ERROR: The In Queue Flow \"{emailQueue_flowName}\" may not exist. Skipping.")
            if bResultsFile:
                with open(resultsFile, 'a') as rFile:
                    rFile.write(f"> ERROR: The In Queue Flow \"{emailQueue_flowName}\" may not exist. Skipping.\n")
            return apiCounter
        else:
            apiCounter = apiCounter + 1
            email_queue_flow.id = emailInQueueResponseFlow.entities[0].id
            email_queue_flow.name = emailQueue_flowName
            queue.email_in_queue_flow = email_queue_flow
    
    email_address = globals.gc.QueueEmailAddress()
    email_address.domain = globals.gc.DomainEntityRef()
    email_address.route = globals.gc.InboundRoute()
    if emailAddress == "pass":
        if globals.userInputClear == "1":
            queue.outbound_email_address = email_address
        else:
            pass
    else:
        RoutingApi_api = globals.gc.RoutingApi(globals.api_client)
        routingEmailResponse: globals.gc.InboundRouteEntityListing = RoutingApi_api.get_routing_email_domain_routes(domain_name = emailDomain)
        apiCounter = apiCounter + 1
        if len(routingEmailResponse.entities) != 0:
            for emailroute in routingEmailResponse.entities:
                if emailroute.pattern == emailAddress:
                    email_address.route.id = emailroute.id
                    email_address.route.pattern = emailAddress
            if emailAddress == "pass":
                print(f"> ERROR: Must have Domain populated if setting an email address. Skipping setting.")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"> ERROR: Must have Domain populated if setting an email address. Skipping setting.")
            else:
                email_address.domain.id = emailDomain
                queue.outbound_email_address = email_address
        else:
            print(f"> ERROR: Specified outbound email address not found. Skipping setting.")
            if bResultsFile:
                with open(resultsFile, 'a') as rFile:
                    rFile.write(f"> ERROR: Specified outbound email address not found. Skipping setting.")

    if enableAutoAnswerAll == "pass":
        if enableAutoAnswerVoice == "pass":
            if globals.userInputClear == "1":
                queue.media_settings.call.enable_auto_answer = False
            else:
                if globals.userInputCreate == "2":
                    pass
                    # serviceLevel.duration_ms = queue.media_settings.call.service_level.duration_ms
        else:
            queue.media_settings.call.enable_auto_answer = enableAutoAnswerVoice
    else:
        queue.media_settings.call.enable_auto_answer = enableAutoAnswerAll
        queue.media_settings.message.enable_auto_answer = enableAutoAnswerAll
        queue.media_settings.message.sub_type_settings = {
            "webmessaging":
            {
                "enableAutoAnswer": enableAutoAnswerAll
            },
            "facebook":
            {
                "enableAutoAnswer": enableAutoAnswerAll
            },
            "instagram":
            {
                "enableAutoAnswer": enableAutoAnswerAll
            },
            "open":
            {
                "enableAutoAnswer": enableAutoAnswerAll
            },
            "sms":
            {
                "enableAutoAnswer": enableAutoAnswerAll
            },
            "twitter":
            {
                "enableAutoAnswer": enableAutoAnswerAll
            },
            "whatsapp":
            {
                "enableAutoAnswer": enableAutoAnswerAll
            }
        }
        queue.media_settings.email.enable_auto_answer = enableAutoAnswerAll
        # mediaSettings.service_level = serviceLevel
    # queueMediaSettings.call = mediaSettings
    # queue.media_settings = queueMediaSettings   
    call_Script = globals.gc.Script()
    scriptDict = queue.default_scripts
    if callScript == "pass":
        if globals.userInputClear == "1":
            if "CALL" in scriptDict:
                scriptDict.pop("CALL")
        else:
            pass
    else:
        call_Script.id = callScript
        scriptDict["CALL"] = call_Script
        # queue.default_scripts = {"CALL":call_Script}
    email_Script = globals.gc.Script()
    if emailScript == "pass":
        if globals.userInputClear == "1":
            if "EMAIL" in scriptDict:
                scriptDict.pop("EMAIL")
        else:
            pass
    else:
        email_Script.id = emailScript
        scriptDict["EMAIL"] = email_Script
        # queue.default_scripts = {"EMAIL":email_Script}
    queue.default_scripts = scriptDict
    if evaluation == "pass":
        if globals.userInputClear == "1":
            queue.skill_evaluation_method = "ALL"
        else:
            pass
    else:
        queue.skill_evaluation_method = evaluation
    if scoreMethod == "pass":
        if globals.userInputClear == "1":
            queue.scoring_method = "TimestampAndPriority"
        else:
            pass
    else:
        queue.scoring_method = scoreMethod
    if caller_id_num == "pass":
        if globals.userInputClear == "1":
            queue.calling_party_number = ""
        else:
            pass
    else:
        queue.calling_party_number = caller_id_num
    if caller_id_name == "pass":
        if globals.userInputClear == "1":
            queue.calling_party_name = ""
        else:
            pass
    else:
        queue.calling_party_name = caller_id_name
    queue_flow = globals.gc.NamedEntity()
    if queueflow == "pass":
        if globals.userInputClear == "1":
            queue.queue_flow = {}
        else:
            pass
    else:
        queue_flowName = queueflow
        ArchitectApi_api = globals.gc.ArchitectApi(globals.api_client)
        responseFlow: globals.gc.FlowEntityListing = ArchitectApi_api.get_flows(name = queue_flowName)

        if len(responseFlow.entities) == 0:
            print(f"> ERROR: The In Queue Flow \"{queue_flowName}\" may not exist. Skipping.")
            if bResultsFile:
                with open(resultsFile, 'a') as rFile:
                    rFile.write(f"> ERROR: The In Queue Flow \"{queue_flowName}\" may not exist. Skipping.\n")
            return apiCounter
        else:
            apiCounter = apiCounter + 1
            queue_flow.id = responseFlow.entities[0].id
            queue_flow.name = queue_flowName
            queue.queue_flow = queue_flow
    if routingRules == "pass":
        if globals.userInputClear == "1":
            queue.routing_rules = None
        else:
            pass
    else:
        rules = routingRules.split(",")
        index = 0
        ruleslist = []
        while index < len(rules):
            RoutingRule = globals.gc.RoutingRule()
            if len(rules[index].split(":")) == 2:
                RoutingRule_wait_seconds, RoutingRule_operator = rules[index].split(":")
                RoutingRule.wait_seconds = RoutingRule_wait_seconds
                RoutingRule.operator = RoutingRule_operator
            else:
                RoutingRule_wait_seconds, RoutingRule_threshold, RoutingRule_operator = rules[index].split(":")
                RoutingRule.wait_seconds = RoutingRule_wait_seconds
                RoutingRule.threshold = RoutingRule_threshold
                RoutingRule.operator = RoutingRule_operator
            ruleslist.append(RoutingRule)
            index = index + 1
        queue.routing_rules = ruleslist
    acw_settings = globals.gc.AcwSettings()
    if acw == "pass":
        if globals.userInputClear == "1":
            queue.acw_settings = {}
        else:
            pass
    else:
        if ":" in acw:
            wrapup_prompt, timeout_in_seconds = acw.split(":")
            acw_settings.wrapup_prompt = wrapup_prompt
            acw_settings.timeout_ms = int(timeout_in_seconds) * 1000
        else:
            acw_settings.wrapup_prompt = acw
        queue.acw_settings = acw_settings
    if group_Routing == "pass":
        if globals.userInputClear == "1":
            queue.conditional_group_routing = {}
        else:
            try:
                """Prevents erroring when an update involves a blank CSV value when the queue has CGR already set"""
                queue.conditional_group_routing.rules[0].queue.id = None
                queue.conditional_group_routing.rules[0].queue.self_uri = None
            except:
                pass
    else:
        queue.bullseye = {}
        group_RoutingList = group_Routing.split(",")
        cgrIndex = 0
        while cgrIndex < len(group_Routing.split(",")):
            divisionZ = globals.gc.NamedEntity()
            memberSplitList = memberGroups.split("|")
            memberSplitListIndex = 0
            groupRoutingRules = []
            fullmemberlist = []
            while memberSplitListIndex < len(memberSplitList):
                groupRouting = globals.gc.ConditionalGroupRouting()
                groupRoutingRule = globals.gc.ConditionalGroupRoutingRule()
                cgrQueue = globals.gc.DomainEntityRef()
                #queue.member_groups = None
                metric, operator, conditionValue, waitSeconds,queueCGR = group_RoutingList[cgrIndex].split(":")
                cgrQueue.name = queue.name
                if memberSplitListIndex == 0:
                    cgrQueue.id = None
                if memberSplitListIndex >= 1:
                    cgrQueue.id = queue.id
                groupRoutingRule.queue = cgrQueue
                groupRoutingRule.metric = metric
                groupRoutingRule.operator = operator
                groupRoutingRule.condition_value = conditionValue
                groupRoutingRule.wait_seconds = waitSeconds
                memberIndex = 0
                members = memberSplitList[memberSplitListIndex].split(",")
                memberlist = []
                while memberIndex < len(members):
                    memberGroup = globals.gc.MemberGroup()    
                    skillgroupname,divisionname = members[memberIndex].split(":")
                    if divisionname == "none":
                        group_api = globals.gc.GroupsApi(globals.api_client)
                        groupSearch = globals.gc.GroupSearchRequest()
                        groupSearchCriteria = globals.gc.GroupSearchCriteria()
                        groupSearchCriteria.fields = ["name"]
                        groupSearchCriteria.type = "EXACT"
                        groupSearchCriteria.value = skillgroupname                    
                        groupSearch.query = [groupSearchCriteria]                   
                        responseZ: globals.gc.GroupsSearchResponse = group_api.post_groups_search(groupSearch)
                        apiCounter = apiCounter + 1
                        memberGroup.type = "GROUP"
                        memberGroup.name = skillgroupname
                        try:
                            memberGroup.id = responseZ.results[0].id
                        except:
                            print(f"> ERROR: The Member Group \"{skillgroupname}\" may not exist. Skipping.")
                            if bResultsFile:
                                with open(resultsFile, 'a') as rFile:
                                    rFile.write(f"> ERROR: The Member Group \"{skillgroupname}\" may not exist. Skipping.\n")
                            return apiCounter
                    else:
                        auth_api = globals.gc.AuthorizationApi(globals.api_client)
                        responseG: globals.gc.AuthzDivisionEntityListing = auth_api.get_authorization_divisions(name = divisionname)
                        apiCounter = apiCounter + 1
                        divisionZ.name = divisionname
                        divisionZ.id = responseG.entities[0].id
                        memberGroup.type = "SKILLGROUP"
                        memberGroup.division = divisionZ
                        routing_api = globals.gc.RoutingApi(globals.api_client)
                        responseQ: globals.gc.SkillGroupEntityListing = routing_api.get_routing_skillgroups(name = skillgroupname)
                        apiCounter = apiCounter + 1
                        memberGroup.name = skillgroupname
                        skillGroupIndex = 0
                        while skillGroupIndex < len(responseQ.entities):
                            if skillgroupname == responseQ.entities[skillGroupIndex].name:
                                memberGroup.id = responseQ.entities[skillGroupIndex].id
                                break
                            skillGroupIndex = skillGroupIndex + 1
                    memberlist.append(memberGroup)
                    fullmemberlist.append(memberGroup)
                    memberIndex = memberIndex + 1
                groupRoutingRule.groups = memberlist
                groupRoutingRules.append(groupRoutingRule)
                memberSplitListIndex = memberSplitListIndex + 1
            cgrIndex = cgrIndex + 1
        groupRouting.rules = groupRoutingRules
        queue.conditional_group_routing = groupRouting
        queue.member_groups = fullmemberlist
    if enableTranscription == "pass":
        if globals.userInputClear == "1":
            queue.enable_transcription = False
        else:
            pass
    else:
        queue.enable_transcription = bool(enableTranscription)
    if enableManualAssignment == "pass":
        if globals.userInputClear == "1":
            queue.enable_manual_assignment = False
        else:
            pass
    else:
        queue.enable_manual_assignment = bool(enableManualAssignment)
    if suppressInQueueCallRecording == "pass":
        if globals.userInputClear == "1":
            queue.suppress_in_queue_call_recording = True
        else:
            pass
    else:
        queue.suppress_in_queue_call_recording = bool(suppressInQueueCallRecording)
    CBL_flow = globals.gc.NamedEntity()
    CBA_flow = globals.gc.NamedEntity()
    if callBackMode == "pass":
        if globals.userInputClear == "1":
            # this is the only way I could could "delete" the CustomerFirst applicable properties.  Class does not have a deleter, and setting the property to None throws an error in the class file.
            callbackMediaSettings = globals.gc.CallbackMediaSettings()
            if queue.media_settings.callback.enable_auto_answer == None:
                callbackMediaSettings.enable_auto_answer = False
            else:
                callbackMediaSettings.enable_auto_answer = queue.media_settings.callback.enable_auto_answer    
            callbackMediaSettings.alerting_timeout_seconds = queue.media_settings.callback.alerting_timeout_seconds
            callbackMediaSettings.service_level = queue.media_settings.callback.service_level
            callbackMediaSettings.mode = "AgentFirst"
            callbackMediaSettings.enable_auto_dial_and_end = queue.media_settings.callback.enable_auto_dial_and_end
            callbackMediaSettings.auto_dial_delay_seconds = queue.media_settings.callback.auto_dial_delay_seconds
            callbackMediaSettings.auto_end_delay_seconds = queue.media_settings.callback.auto_end_delay_seconds
            queue.media_settings.callback = callbackMediaSettings
        else:
            pass
    else:
        queue.media_settings.callback.mode = callBackMode
        if callBackMode == "CustomerFirst":
            if queue.media_settings.callback.live_voice_reaction_type == None and callbackLiveVoice == "pass":
                print(f"> CustomerFirst being enabled with default Transfer to Queue Live Voice Action.")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"> CustomerFirst being enabled with default Transfer to Queue Live Voice Action.\n")
                queue.media_settings.callback.live_voice_reaction_type =  "TransferToQueue"
            if callbackLiveVoice == "TransferToFlow" and callbackLiveVoiceFlow == "pass":
                print(f"> Must have a flow present in \"CallbackLiveVoiceFlow\" column. Skipping {queue.name}")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"> Must have a flow present in \"CallbackLiveVoiceFlow\" column. Skipping {queue.name}\n")
                return apiCounter
            if callbackLiveVoice == "pass":
                if globals.userInputClear == "1":
                    queue.media_settings.callback.live_voice_reaction_type =  "TransferToQueue"
                else:
                    pass
            else: 
                queue.media_settings.callback.live_voice_reaction_type = callbackLiveVoice
            if callbackLiveVoiceFlow == "pass":
                if globals.userInputClear == "1":
                    print(f"> Cannot Clear \"CallbackLiveVoiceFlow\" setting. Leaving as-is")
                    if bResultsFile:
                        with open(resultsFile, 'a') as rFile:
                            rFile.write(f"> Cannot Clear \"CallbackLiveVoiceFlow\" setting. Leaving as-is\n")
                else:
                    pass
            else:
                ArchitectApi_api = globals.gc.ArchitectApi(globals.api_client)
                responseCBFlow: globals.gc.FlowEntityListing = ArchitectApi_api.get_flows(name = callbackLiveVoiceFlow)
                apiCounter = apiCounter + 1
                if len(responseCBFlow.entities) == 0:
                    print(f"> ERROR: The In Queue Flow \"{callbackLiveVoiceFlow}\" may not exist. Skipping.")
                    if bResultsFile:
                        with open(resultsFile, 'a') as rFile:
                            rFile.write(f"> ERROR: The In Queue Flow \"{callbackLiveVoiceFlow}\" may not exist. Skipping.\n")
                    return apiCounter
                else:
                    CBL_flow.id = responseCBFlow.entities[0].id
                    CBL_flow.name = callbackLiveVoiceFlow
                    queue.media_settings.callback.live_voice_flow = CBL_flow
            if queue.media_settings.callback.answering_machine_reaction_type == None and callbackAnswerMachine == "pass":
                print(f"> CustomerFirst being enabled with default Hangup Voicemail Action.")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"> CustomerFirst being enabled with default Hangup Voicemail Action.\n")
                queue.media_settings.callback.answering_machine_reaction_type =  "Hangup"
            if callbackAnswerMachine == "TransferToFlow" and callbackAnswerMachineFlow == "pass":
                print(f"> Must have a flow present in \"callbackAnswerMachineFlow\" column. Skipping {queue.name}")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"> Must have a flow present in \"callbackAnswerMachineFlow\" column. Skipping {queue.name}\n")
                return apiCounter
            if callbackAnswerMachine == "pass":
                if globals.userInputClear == "1":
                    queue.media_settings.callback.answering_machine_reaction_type =  "Hangup"
                else:
                    pass
            else: 
                queue.media_settings.callback.answering_machine_reaction_type = callbackAnswerMachine
            if callbackAnswerMachineFlow == "pass":
                if globals.userInputClear == "1":
                    print(f"> Cannot Clear \"callbackAnswerMachineFlow\" setting. Leaving as-is")
                    if bResultsFile:
                        with open(resultsFile, 'a') as rFile:
                            rFile.write(f"> Cannot Clear \"callbackAnswerMachineFlow\" setting. Leaving as-is\n")
                else:
                    pass
            else:
                ArchitectApi_api = globals.gc.ArchitectApi(globals.api_client)
                responseCBAMFlow: globals.gc.FlowEntityListing = ArchitectApi_api.get_flows(name = callbackAnswerMachineFlow)
                apiCounter = apiCounter + 1
                if len(responseCBAMFlow.entities) == 0:
                    print(f"> ERROR: The In Queue Flow \"{callbackAnswerMachineFlow}\" may not exist. Skipping.")
                    if bResultsFile:
                        with open(resultsFile, 'a') as rFile:
                            rFile.write(f"> ERROR: The In Queue Flow \"{callbackAnswerMachineFlow}\" may not exist. Skipping.\n")
                    return apiCounter
                else:
                    CBA_flow.id = responseCBAMFlow.entities[0].id
                    CBA_flow.name = callbackAnswerMachineFlow
                    queue.media_settings.callback.answering_machine_flow = CBA_flow
        elif callBackMode == "AgentFirst":
            # this is the only way I could could "delete" the CustomerFirst applicable properties.  Class does not have a deleter, and setting the property to None throws an error in the class file.
            callbackMediaSettings = globals.gc.CallbackMediaSettings()
            if queue.media_settings.callback.enable_auto_answer == None:
                callbackMediaSettings.enable_auto_answer = False
            else:
                callbackMediaSettings.enable_auto_answer = queue.media_settings.callback.enable_auto_answer
            callbackMediaSettings.alerting_timeout_seconds = queue.media_settings.callback.alerting_timeout_seconds
            callbackMediaSettings.service_level = queue.media_settings.callback.service_level
            callbackMediaSettings.mode = callBackMode
            callbackMediaSettings.enable_auto_dial_and_end = queue.media_settings.callback.enable_auto_dial_and_end
            callbackMediaSettings.auto_dial_delay_seconds = queue.media_settings.callback.auto_dial_delay_seconds
            callbackMediaSettings.auto_end_delay_seconds = queue.media_settings.callback.auto_end_delay_seconds
            queue.media_settings.callback = callbackMediaSettings
    cannedResponsesObj = globals.gc.CannedResponseLibraries()
    if cannedResponses == "pass":
        if globals.userInputClear == "1":
            cannedResponsesObj.mode = "All"
            queue.canned_response_libraries = cannedResponsesObj
        else:
            pass
    else:
        if cannedResponses != "All" and cannedResponses != "Blank":
            cannedResponsesIdList = []
            cannedResponsesNameList = cannedResponses.split(",")
            responseAPI = globals.gc.ResponseManagementApi(globals.api_client)
            for cr in cannedResponsesNameList:
                crResponse: globals.gc.LibraryEntityListing = responseAPI.get_responsemanagement_libraries(library_prefix = cr)
                for crR in crResponse.entities:
                    if crR.name == cr:
                        cannedResponsesIdList.append(crR.id)
            
            cannedResponsesObj.mode = "SelectedOnly"
            cannedResponsesObj.library_ids = cannedResponsesIdList
        else:
            if cannedResponses == "Blank":
                cannedResponses = "None"
            cannedResponsesObj.mode = cannedResponses
        queue.canned_response_libraries = cannedResponsesObj
    if wrapUpCodes == "pass":
        updateWrapUpCodes = False
        if globals.userInputClear == "1":
            pass
        else:
            pass
    else:
        updateWrapUpCodes = True
        wrapUpCodesNameList = wrapUpCodes.split(",")
        wrapUpCodesDict = []
        for wrapUpCode in wrapUpCodesNameList:
            wrapUpCodesResponse: globals.gc.WrapupCodeEntityListing = routing_api.get_routing_wrapupcodes(name = wrapUpCode)
            apiCounter = apiCounter + 1
            if len(wrapUpCodesResponse.entities) == 0:
                print(f"> Could not locate Wrapup Code: {wrapUpCode}")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"> Could not locate Wrapup Code: {wrapUpCode}\n")
            for wrEntity in wrapUpCodesResponse.entities:
                if wrEntity.name == wrapUpCode:
                    wrapUpCodesDict.append({
                        "id":wrEntity.id
                    })
        # queue.canned_response_libraries = cannedResponsesObj
    
    queue.date_created = None
    queue.date_modified = None
    if globals.userInputCreate == "1":
        if prebuilt == True:
            try:
                routing_api.put_routing_queue(queue.id, queue)
                apiCounter = apiCounter + 1
                if updateWrapUpCodes:
                    routing_api.post_routing_queue_wrapupcodes(queue.id,wrapUpCodesDict)
                    apiCounter = apiCounter + 1
                print(f"> UPDATED")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"> UPDATED\n")
            except ApiException as e:
                print("Exception when updating queue %s\n" % e)
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write("Exception when updating queue %s\n" % e)
        else:    
            try:
                routing_api.post_routing_queues(queue)
                if updateWrapUpCodes:
                    routing_api.post_routing_queue_wrapupcodes(queue.id,wrapUpCodesDict)
                    apiCounter = apiCounter + 1
                apiCounter = apiCounter + 1
                print(f"> CREATED")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"> CREATED\n")
            except ApiException as e:
                print("Exception when creating queue %s\n" % e)
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write("Exception when creating queue %s\n" % e)
    elif globals.userInputCreate == "2":
        try:
            routing_api.put_routing_queue(queue.id, queue)
            apiCounter = apiCounter + 1
            if updateWrapUpCodes:
                routing_api.post_routing_queue_wrapupcodes(queue.id,wrapUpCodesDict)
                apiCounter = apiCounter + 1
            print(f"> UPDATED")
            if bResultsFile:
                with open(resultsFile, 'a') as rFile:
                    rFile.write(f"> UPDATED\n")
        except ApiException as e:
            print("Exception when updating queue %s\n" % e)
            if bResultsFile:
                with open(resultsFile, 'a') as rFile:
                    rFile.write("Exception when updating queue %s\n" % e)
    return apiCounter

def fetch_all_queues() -> {}: # type: ignore
    routing_api = globals.gc.RoutingApi(globals.api_client)
    page_number = 1
    queues_info = {}
    print(f"\nFETCHING ALL QUEUES INFO...")
    while True:
        response: globals.gc.QueueEntityListing = routing_api.get_routing_queues(page_number=page_number, page_size=100)
        for queue in response.entities:
            queues_info.update({queue.name: queue})
        page_number += 1
        print(f"...")
        if page_number > response.page_count:
            print("...DONE\n")
            break
    return queues_info

def update_queue_from_csv(file_path, apiCounter,resultsFile_in):
    global prebuilt
    global resultsFile
    global bResultsFile
    bResultsFile = resultsFile_in
    prebuilt = False
    data_frame = pd.read_csv(file_path, sep=",")
    startTime = datetime.datetime.now()
    startTime1 = startTime.strftime("%m/%d/%Y %H:%M:%S")
    if bResultsFile:
        resultsFile = f".\\results\\result_{startTime.strftime("%m.%d.%Y_%H.%M.%S")}.txt"
        with open(resultsFile, "w") as rFile:
            rFile.write("BEGIN \n")
    bMissingColumn = False
    for index, row in data_frame.iterrows():
        current_queue = row["queue"]
        try:
            isNotSet = data_frame["description"].isna()
            if isNotSet[index]:
                current_description = "pass"
            else:
                current_description = row["description"]
        except:
            missingColumn = "description"
            bMissingColumn = True
        try:
            isNotSet = data_frame["evaluation"].isna()
            if isNotSet[index]:
                current_evaluation = "pass"
            else:
                current_evaluation = row["evaluation"]
        except:
            missingColumn = "evaluation"
        try:
            isNotSet = data_frame["alerting_timeout_seconds"].isna()
            if isNotSet[index]:
                current_alerting_timeout_seconds = "pass"
            else:
                current_alerting_timeout_seconds = row["alerting_timeout_seconds"]
        except:
            missingColumn = "alerting_timeout_seconds"
            bMissingColumn = True
        try:
            isNotSet = data_frame["slPercentage"].isna()
            if isNotSet[index]:
                current_slPercentage = "pass"
            else:
                current_slPercentage = row["slPercentage"]
        except:
            missingColumn = "slPercentage"
            bMissingColumn = True
        try:
            isNotSet = data_frame["slDuration_ms"].isna()
            if isNotSet[index]:
                current_slDuration_ms = "pass"
            else:
                current_slDuration_ms = row["slDuration_ms"]
        except:
            missingColumn = "slDuration_ms"
            bMissingColumn = True
        try:
            isNotSet = data_frame["cb_alerting_timeout_seconds"].isna()
            if isNotSet[index]:
                current_cb_alerting_timeout_seconds = "pass"
            else:
                current_cb_alerting_timeout_seconds = row["cb_alerting_timeout_seconds"]
        except:
            missingColumn = "cb_alerting_timeout_seconds"
            bMissingColumn = True
        try:
            isNotSet = data_frame["cb_slPercentage"].isna()
            if isNotSet[index]:
                current_cb_slPercentage = "pass"
            else:
                current_cb_slPercentage = row["cb_slPercentage"]
        except:
            missingColumn = "cb_slPercentage"
            bMissingColumn = True
        try:
            isNotSet = data_frame["cb_slDuration_ms"].isna()
            if isNotSet[index]:
                current_cb_slDuration_ms = "pass"
            else:
                current_cb_slDuration_ms = row["cb_slDuration_ms"]
        except:
            missingColumn = "cb_slDuration_ms"
            bMissingColumn = True
        try:
            isNotSet = data_frame["callerIDNum"].isna()
            if isNotSet[index]:
                current_callerIDNum = "pass"
            else:
                current_callerIDNum = "+" + str(round(row["callerIDNum"]))
        except:
            missingColumn = "callerIDNum"
            bMissingColumn = True
        try:
            isNotSet = data_frame["callerIDName"].isna()
            if isNotSet[index]:
                current_callerIDName = "pass"
            else:
                current_callerIDName = row["callerIDName"]
        except:
            missingColumn = "callerIDName"
            bMissingColumn = True
        try:
            isNotSet = data_frame["bullseye"].isna()
            if isNotSet[index]:
                current_bullseye = "pass"
            else:
                current_bullseye = row["bullseye"]
        except:
            missingColumn = "bullseye"
            bMissingColumn = True
        try:
            isNotSet = data_frame["acw"].isna()
            if isNotSet[index]:
                current_acw = "pass"
            else:
                current_acw = row["acw"]
        except:
            missingColumn = "acw"
            bMissingColumn = True
        try:
            isNotSet = data_frame["inQueueFlow"].isna()
            if isNotSet[index]:
                current_inQueue = "pass"
            else:
                current_inQueue = row["inQueueFlow"]
        except:
            missingColumn = "inQueueFlow"
            bMissingColumn = True
        try:
            isNotSet = data_frame["routingRules"].isna()
            if isNotSet[index]:
                current_routingRules = "pass"
            else:
                current_routingRules = row["routingRules"]
        except:
            missingColumn = "routingRules"
            bMissingColumn = True
        try:
            isNotSet = data_frame["callScript"].isna()
            if isNotSet[index]:
                current_callScript = "pass"
            else:
                current_callScript = row["callScript"]
        except:
            missingColumn = "callScript"
            bMissingColumn = True
        try:
            isNotSet = data_frame["MemberGroups"].isna()
            if isNotSet[index]:
                current_MemberGroups = "pass"
            else:
                current_MemberGroups = row["MemberGroups"]
        except:
            missingColumn = "MemberGroups"
            bMissingColumn = True
        try:
            isNotSet = data_frame["division"].isna()
            if isNotSet[index]:
                current_division = "pass"
            else:
                current_division = row["division"]
        except:
            missingColumn = "division"
            bMissingColumn = True
        try:
            isNotSet = data_frame["groupRouting"].isna()
            if isNotSet[index]:
                current_groupRouting = "pass"
            else:
                current_groupRouting = row["groupRouting"]
        except:
            missingColumn = "groupRouting"
            bMissingColumn = True
        try:
            isNotSet = data_frame["enableTranscription"].isna()
            if isNotSet[index]:
                current_enableTranscription = "pass"
            else:
                current_enableTranscription = row["enableTranscription"]
        except:
            missingColumn = "enableTranscription"
            bMissingColumn = True
        try:
            isNotSet = data_frame["enableManualAssignment"].isna()
            if isNotSet[index]:
                current_enableManualAssignment = "pass"
            else:
                current_enableManualAssignment = row["enableManualAssignment"]
        except:
            missingColumn = "enableManualAssignment"
            bMissingColumn = True
        try:
            isNotSet = data_frame["suppressInQueueCallRecording"].isna()
            if isNotSet[index]:
                current_suppressInQueueCallRecording = "pass"
            else:
                current_suppressInQueueCallRecording = row["suppressInQueueCallRecording"]
        except:
            missingColumn = "suppressInQueueCallRecording"
            bMissingColumn = True
        try:
            isNotSet = data_frame["callBackMode"].isna()
            if isNotSet[index]:
                current_callBackMode = "pass"
            else:
                current_callBackMode = row["callBackMode"]
        except:
            missingColumn = "callBackMode"
            bMissingColumn = True
        try:
            isNotSet = data_frame["CallbackLiveVoice"].isna()
            if isNotSet[index]:
                current_callbackLiveVoice = "pass"
            else:
                current_callbackLiveVoice = row["CallbackLiveVoice"]
        except:
            missingColumn = "CallbackLiveVoice"
            bMissingColumn = True
        try:
            isNotSet = data_frame["CallbackLiveVoiceFlow"].isna()
            if isNotSet[index]:
                current_callbackLiveVoiceFlow = "pass"
            else:
                current_callbackLiveVoiceFlow = row["CallbackLiveVoiceFlow"]
        except:
            missingColumn = "CallbackLiveVoiceFlow"
            bMissingColumn = True
        try:
            isNotSet = data_frame["CallbackAnswerMachine"].isna()
            if isNotSet[index]:
                current_callbackAnswerMachine = "pass"
            else:
                current_callbackAnswerMachine = row["CallbackAnswerMachine"]
        except:
            missingColumn = "CallbackAnswerMachine"
            bMissingColumn = True
        try:
            isNotSet = data_frame["CallbackAnswerMachineFlow"].isna()
            if isNotSet[index]:
                current_callbackAnswerMachineFlow = "pass"
            else:
                current_callbackAnswerMachineFlow = row["CallbackAnswerMachineFlow"]
        except:
            missingColumn = "CallbackAnswerMachineFlow"
            bMissingColumn = True  
        try:
            isNotSet = data_frame["enableAutoAnswerVoice"].isna()
            if isNotSet[index]:
                current_enableAutoAnswerVoice = "pass"
            else:
                current_enableAutoAnswerVoice = row["enableAutoAnswerVoice"]
        except:
            missingColumn = "enableAutoAnswerVoice"
            bMissingColumn = True
        try:
            isNotSet = data_frame["enableAutoAnswerAll"].isna()
            if isNotSet[index]:
                current_enableAutoAnswerAll = "pass"
            else:
                current_enableAutoAnswerAll = row["enableAutoAnswerAll"]
        except:
            missingColumn = "enableAutoAnswerAll"
            bMissingColumn = True
        try:
            isNotSet = data_frame["email_slPercentage"].isna()
            if isNotSet[index]:
                current_email_slPercentage = "pass"
            else:
                current_email_slPercentage = row["email_slPercentage"]
        except:
            missingColumn = "email_slPercentage"
            bMissingColumn = True
        try:
            isNotSet = data_frame["email_slDuration_ms"].isna()
            if isNotSet[index]:
                current_email_slDuration_ms = "pass"
            else:
                current_email_slDuration_ms = row["email_slDuration_ms"]
        except:
            missingColumn = "email_slDuration_ms"
            bMissingColumn = True
        try:
            isNotSet = data_frame["email_alerting_timeout_seconds"].isna()
            if isNotSet[index]:
                current_email_alerting_timeout_seconds = "pass"
            else:
                current_email_alerting_timeout_seconds = row["email_alerting_timeout_seconds"]
        except:
            missingColumn = "email_alerting_timeout_seconds"
            bMissingColumn = True
        try:
            isNotSet = data_frame["emailInQueueFlow"].isna()
            if isNotSet[index]:
                current_emailInQueueFlow = "pass"
            else:
                current_emailInQueueFlow = row["emailInQueueFlow"]
        except:
            missingColumn = "emailInQueueFlow"
            bMissingColumn = True
        try:
            isNotSet = data_frame["emailScript"].isna()
            if isNotSet[index]:
                current_emailScript = "pass"
            else:
                current_emailScript = row["emailScript"]
        except:
            missingColumn = "emailScript"
            bMissingColumn = True
        try:
            isNotSet = data_frame["emailAddress"].isna()
            if isNotSet[index]:
                current_emailAddress = "pass"
            else:
                current_emailAddress = row["emailAddress"]
        except:
            missingColumn = "emailAddress"
            bMissingColumn = True
        try:
            isNotSet = data_frame["emailDomain"].isna()
            if isNotSet[index]:
                current_emailDomain = "pass"
            else:
                current_emailDomain = row["emailDomain"]
        except:
            missingColumn = "emailDomain"
            bMissingColumn = True
        try:
            isNotSet = data_frame["cannedResponses"].isna()
            if isNotSet[index]:
                current_cannedResponses = "pass"
            else:
                current_cannedResponses = row["cannedResponses"]
        except:
            missingColumn = "cannedResponses"
            bMissingColumn = True
        try:
            isNotSet = data_frame["wrapUpCodes"].isna()
            if isNotSet[index]:
                current_wrapUpCodes = "pass"
            else:
                current_wrapUpCodes = row["wrapUpCodes"]
        except:
            missingColumn = "wrapUpCodes"
            bMissingColumn = True
        try:
            isNotSet = data_frame["scoreMethod"].isna()
            if isNotSet[index]:
                current_scoreMethod = "pass"
            else:
                current_scoreMethod = row["scoreMethod"]
        except:
            missingColumn = "scoreMethod"
            bMissingColumn = True

        if bMissingColumn:
            exit(f"\n> ERROR: You are missing require column in CSV: {missingColumn}. This is case senstive. Double check case or please add if missing and try again :)\n")
        if index == 0:
            queues_info: {} = fetch_all_queues() # type: ignore
        
        if globals.userInputCreate == "1":
            if current_queue not in queues_info:
                #queues_info = {}
                queueCreate = globals.gc.Queue()
                queueCreate.name = row["queue"]
                queueDivision = globals.gc.NamedEntity()
                queueDivisionName = row["division"]
                auth_api = globals.gc.AuthorizationApi(globals.api_client)
                responseL: globals.gc.AuthzDivisionEntityListing = auth_api.get_authorization_divisions(name = queueDivisionName)
                apiCounter = apiCounter + 1
                queueDivision.name = queueDivisionName
                divisionIndex = 0
                print(f"QUEUE: {queueCreate.name}")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"QUEUE: {queueCreate.name}\n")
                try:
                    queueDivision.id = responseL.entities[0].id
                except:
                    print(f"> ERROR: Must include a Division when creating a queue for the first time. Even if meant for the \"Home\" Division.")
                    if bResultsFile:
                        with open(resultsFile, 'a') as rFile:
                            rFile.write(f"> ERROR: The Division: \"{queueDivisionName}\" may not exist. Skipping\n")
                    continue
                while divisionIndex < len(responseL.entities):
                    if queueDivisionName == responseL.entities[divisionIndex].name:
                        queueDivision.id = responseL.entities[divisionIndex].id
                        queueCreate.division = queueDivision    
                    divisionIndex = divisionIndex + 1
                routing_api = globals.gc.RoutingApi(globals.api_client)
                queueCreate: globals.gc.Queue = routing_api.post_routing_queues(queueCreate)
                print(f"> CREATED")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"> CREATED\n")
                queues_info.update({queueCreate.name: queueCreate})
                apiCounter = apiCounter + 1
                prebuilt = True
                apiCounter = update_queue(
                    queues_info[current_queue],current_acw, current_inQueue, current_routingRules, current_callScript, current_bullseye, current_MemberGroups, current_evaluation, current_callerIDNum,
                    current_callerIDName, current_alerting_timeout_seconds, current_slPercentage, current_slDuration_ms, current_division, current_groupRouting, apiCounter, current_description,
                    current_enableTranscription, current_enableManualAssignment, current_suppressInQueueCallRecording, current_callBackMode, current_callbackLiveVoice, current_callbackLiveVoiceFlow, current_callbackAnswerMachine, current_callbackAnswerMachineFlow,
                    current_enableAutoAnswerVoice, current_enableAutoAnswerAll, current_cannedResponses, current_cb_alerting_timeout_seconds, current_cb_slPercentage, current_cb_slDuration_ms,
                    current_email_slPercentage,current_email_slDuration_ms,current_email_alerting_timeout_seconds,current_emailInQueueFlow,current_emailScript,current_emailAddress,current_emailDomain,
                    current_wrapUpCodes,current_scoreMethod)
            else:
                print(f"QUEUE: {current_queue}\n> ALREADY EXISTS. USE UPDATE OPTION INSTEAD")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"QUEUE: {current_queue}\n> ALREADY EXISTS. USE UPDATE OPTION INSTEAD\n")
        elif globals.userInputCreate == "2":
            if current_queue in queues_info:
                print(f"QUEUE: {current_queue}")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"QUEUE: {current_queue} \n")
                apiCounter = update_queue(
                    queues_info[current_queue], current_acw, current_inQueue, current_routingRules, current_callScript, current_bullseye, current_MemberGroups, current_evaluation, current_callerIDNum,
                    current_callerIDName, current_alerting_timeout_seconds, current_slPercentage, current_slDuration_ms, current_division, current_groupRouting, apiCounter, current_description,
                    current_enableTranscription, current_enableManualAssignment, current_suppressInQueueCallRecording, current_callBackMode, current_callbackLiveVoice, current_callbackLiveVoiceFlow, current_callbackAnswerMachine,current_callbackAnswerMachineFlow,
                    current_enableAutoAnswerVoice,current_enableAutoAnswerAll,current_cannedResponses, current_cb_alerting_timeout_seconds, current_cb_slPercentage, current_cb_slDuration_ms,
                    current_email_slPercentage,current_email_slDuration_ms,current_email_alerting_timeout_seconds,current_emailInQueueFlow,current_emailScript,current_emailAddress,current_emailDomain,
                    current_wrapUpCodes,current_scoreMethod)
            else:
                print(f"QUEUE: {current_queue}\n> NOT FOUND, USE CREATE OPTION INSTEAD")
                if bResultsFile:
                    with open(resultsFile, 'a') as rFile:
                        rFile.write(f"QUEUE: {current_queue}\n> NOT FOUND, USE CREATE OPTION INSTEAD\n")

    endTime = datetime.datetime.now()
    endTime1 = endTime.strftime("%m/%d/%Y %H:%M:%S")
    totalDuration = endTime - startTime
    delta_as_time_obj = time.gmtime(totalDuration.total_seconds())
    print(f"\n<<< PROCESSED ALL >>>")
    print(f"<<< START:     {startTime1} >>>")
    print(f"<<< END:       {endTime1} >>>")
    print(f"<<< Duration:  {str(delta_as_time_obj.tm_min)} MIN {str(delta_as_time_obj.tm_sec + 1)} SEC >>>") 
    print(f"<<< APPROX. API CALLS: {apiCounter} >>>\n")

    if bResultsFile:
        with open(resultsFile, 'a') as rFile:
            rFile.write(f"\n<<< PROCESSED ALL >>>\n")
            rFile.write(f"<<< START:     {startTime1} >>>\n")
            rFile.write(f"<<< END:       {endTime1} >>>\n")
            rFile.write(f"<<< Duration:  {str(delta_as_time_obj.tm_min)} MIN {str(delta_as_time_obj.tm_sec + 1)} SEC >>>\n") 
            rFile.write(f"<<< APPROX. API CALLS: {apiCounter} >>>\n")