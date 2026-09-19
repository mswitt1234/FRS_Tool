import os
from dotenv import load_dotenv
from PureCloudPlatformClientV2.rest import ApiException
import PureCloudPlatformClientV2 as gct
from pprint import pprint
global gc
global org
global env
global userInputClear
global userInputCreate

load_dotenv()

gc = gct

# Secrets — read from main.env.
client_id = os.environ["GC_CLIENT_ID"]
client_secret = os.environ["GC_CLIENT_SECRET"]

# Not secrets, but they must match the credentials above.
region_name = os.environ["GC_REGION"]   # e.g. ca_central_1
env = os.environ["GC_ENV"]              # e.g. cac1.pure.cloud

region = getattr(gc.PureCloudRegionHosts, region_name)
gc.configuration.host = region.get_api_host()

# Get API Token and display connected Org for confirmation.
api_client = gc.ApiClient().get_client_credentials_token(client_id, client_secret)
tokenApi = gc.TokensApi(api_client)
preserve_idle_ttl = True
try:
    # Fetch information about the current token
    api_response = tokenApi.get_tokens_me(preserve_idle_ttl=preserve_idle_ttl)
    org = api_response.organization.name
except ApiException as e:
    print("Exception when calling TokensApi->get_tokens_me: %s\n" % e)