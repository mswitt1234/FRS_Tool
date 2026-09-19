import time
from PureCloudPlatformClientV2.rest import ApiException
import globals, datetime
import pandas as pd
import os
from datetime import datetime
now = datetime.now()
architectApi = globals.gc.ArchitectApi(globals.api_client)
dataActionDfRows = []

def FindFlows(object):
    architectApiSuccess = False
    flowIdList = []
    flowDict = {}
    try:
        dependencyResponse: globals.gc.DependencyObject = architectApi.get_architect_dependencytracking_object(id=object.id, object_type = "dataAction", consuming_resources = True)
        # globals.pprint(dependencyResponse.self_uri)
        architectApiSuccess = True
    except ApiException as e:
        print("Exception when calling ArchitectApi->get_architect_dependencytracking_object: %s\n" % e)
    
    if architectApiSuccess:
        for dep in dependencyResponse.consuming_resources:
            if dep.id not in flowIdList and dep.id not in flowDict:
                flowIdList.append(dep.id)
                flowDict[f"{dep.id}"] = []
        for dictDep in flowDict:
            for dep in dependencyResponse.consuming_resources:
                if dictDep == dep.id:
                    flowDict[dictDep].append(dep.version)  
        try:
            dataActionName = object.name
            dataActionID = object.id
            dataActionCat = object.category
            if len(flowIdList) > 0:
                # print(f"\n{object.name}:")
                try:
                    flowResponse: globals.gc.FlowEntityListing = architectApi.get_flows(include_schemas=True,id=flowIdList)
                except ApiException as e:
                    print("Exception when calling ArchitectApi->get_flows: %s\n" % e)
                for flowEntity in flowResponse.entities:
                    if flowEntity.deleted == True:
                        status = "FLOW DELETED"
                    else:
                        if flowEntity.published_version is None:
                            status = "Flow Not Published"
                        elif flowEntity.published_version.commit_version in flowDict[flowEntity.id]:
                            status = f"IN LASTEST"
                        else:
                            status = "NOT IN LASTEST"
                    # print(f" > {flowEntity.type}: {flowEntity.name} {status}")
                    daFlowType = flowEntity.type
                    daFlowName = flowEntity.name
                    daFlowStatus = status
                    dataActionDfRows.append([dataActionName,dataActionID,dataActionCat,daFlowType,daFlowName,daFlowStatus])
            else:
                daFlowType = ""
                daFlowName = ""
                daFlowStatus = "UNUSED"
                dataActionDfRows.append([dataActionName,dataActionID,dataActionCat,daFlowType,daFlowName,daFlowStatus])
        except:
            print("Whoops, I broke inside \"FindFlows\"")
    else:
        pass

def Dependencies():
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    basePath = f"{__location__}\\GCDependecies"
    dataActionOutputfile = f"{basePath}\\GCDependecies_{globals.org}_{now.strftime("%m.%d.%Y_%H.%M.%S")}.csv"
    integrationsApiSuccess = False
    integrationsApi = globals.gc.IntegrationsApi(globals.api_client)
    dataActionDf = pd.DataFrame(columns=["Data Action Name","Data Action ID","Integration","Flow Type","Flow Name","Status"])
    try:
        # Retrieves all actions associated with filters passed in via query param.
        integrationsResponse: globals.gc.ActionEntityListing = integrationsApi.get_integrations_actions(page_size = 9999)
        # globals.pprint(integrationsResponse)
        print(f"\nData Actions Total: {integrationsResponse.total}")
        integrationsApiSuccess = True
    except ApiException as e:
        print("Exception when calling IntegrationsApi->get_integrations_actions: %s\n" % e)

    if integrationsApiSuccess:
        for entity in integrationsResponse.entities:
            # print(f"{entity.name}:")
            FindFlows(entity)
    else:
        pass
    dataActionRowIndex = 0
    for row in dataActionDfRows:
        dataActionDf.loc[dataActionRowIndex] = row
        dataActionRowIndex = dataActionRowIndex + 1
    with open(dataActionOutputfile, mode='w', newline='') as file:
        dataActionDf.to_csv(dataActionOutputfile, sep=",",index=False,header=True)
    print("Done")

