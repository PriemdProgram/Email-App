from azure.identity import DeviceCodeCredential
import msal


class CodeRetreiver():
    def __init__(self, client_id):
        self.client_id = client_id

        self.msal_app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority="https://login.microsoftonline.com/common"
        )

        self.device_code_result = self.msal_app.initiate_device_flow(scopes=["https://graph.microsoft.com/.default"])

        self.user_code = self.device_code_result["user_code"]
        self.verification_url = self.device_code_result["verification_uri"]
        self.full_message = self.device_code_result["message"]
    
    def token(self):
        """ Returns an object with get_token() instead of just the access token. """
        token_result = self.msal_app.acquire_token_by_device_flow(self.device_code_result)
        
        if "access_token" not in token_result:
            raise Exception(f"Failed to retrieve access token: {token_result.get('error_description', 'Unknown error')}")
        
        class TokenCredential:
            def __init__(self, token):
                self.token = token
            
            def get_token(self, *args, **kwargs):
                return self.token

        return TokenCredential(token_result["access_token"])

'''    
code = CodeRetreiver("bc7fa2de-d8ed-47a3-8e46-f878c4e768d7")
print(code.device_code_result)
print(code.user_code)
print(code.full_message)
print(code.token().get_token())
'''

'''
code = DeviceCodeCredential(client_id="bc7fa2de-d8ed-47a3-8e46-f878c4e768d7",tenant_id="common")
print(code)
'''
