from msal import PublicClientApplication
import configparser
from msgraph import GraphServiceClient
#from azure.identity import TokenCredential
from azure.core.credentials import TokenCredential, AccessToken

config = configparser.ConfigParser()
config.read(['config.cfg', 'config.dev.cfg'])
azure_settings = config['azure']
graph_scopes = azure_settings['graphUserScopes'].split(' ')


class Broker(TokenCredential):
    def __init__(self,client_id, graph_scopes):
        self.client_id = client_id
        self.graph_scopes = graph_scopes

        app = PublicClientApplication(
            self.client_id,
            authority="https://login.microsoftonline.com/common",
            enable_broker_on_windows=True)

        self.result = app.acquire_token_interactive(self.graph_scopes,
                parent_window_handle=app.CONSOLE_WINDOW_HANDLE,
                prompt="select_account")
        
        self.token = self.result["access_token"]
        self.expires_on = int(self.result["expires_in"])
        
    def get_token(self, *args, **kwargs):
        print(f"get_token() called with args={args}, kwargs={kwargs}")
        print(f"Returning token: {self.token[:20]}...")
        return AccessToken(self.token, self.expires_on)

"""
code = Broker(azure_settings['clientId'], graph_scopes)
"""
""" try:
    print(code.result["claims"])
except KeyError:
    print(f"Not found")
 """
