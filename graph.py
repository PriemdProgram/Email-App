from configparser import SectionProxy
from azure.identity import DeviceCodeCredential, InteractiveBrowserCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import (
    MessagesRequestBuilder)
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import (
    SendMailPostRequestBody)
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from test2 import CodeRetreiver
from test import Broker
from msal import PublicClientApplication
import aiohttp


class Graph:
    settings: SectionProxy
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        clientSecret = self.settings['clientSecret']
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        self.graph_scopes = self.settings['graphUserScopes'].split(' ')
        self.sign_in = Broker(client_id, self.graph_scopes)
        self.token = self.sign_in.get_token()
        self.user_client = GraphServiceClient(credentials=self.sign_in, scopes=self.graph_scopes)


    async def get_user_token(self):
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
        return access_token.token
    
    async def get_user(self):
        # Only request specific properties using $select
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName']
        )

        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        user = await self.user_client.me.get(request_configuration=request_config)
        return user
    
    
    async def get_inbox(self, inbox):
        print("DEBUG: get_inbox() called")  # Ensure function is being called
        print(f"DEBUG: self.user_client -> {self.user_client}")
        try:
            query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                # Only request specific properties
                select=['from', 'body', 'receivedDateTime', 'subject','bccRecipients','ccRecipients','toRecipients','uniqueBody'],
                # Get at most 25 results
                top=25,
                # Sort by received time, newest first
                orderby=['receivedDateTime DESC']
            )

            
            request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters= query_params
            )

            print("DEBUG: About to make request to Graph API")
            messages = await self.user_client.me.mail_folders.by_mail_folder_id(inbox).messages.get(
                    request_configuration=request_config)
            
            print("DEBUG: Request to Graph API successful")
            return messages
        except Exception as e:
            print(f"Error in get_inbox(): {e}")
            return None
