from core.client_class import Client, elasticsearch_required
from core.basic_utils  import dotkeys
from core.search_utils import doctype_first

import httplib2
from oauth2client import client
from oauth2client.client import Credentials

class youtube(Client):
    """Class to add youtube credentials """

    service_name = "youtube"

    @elasticsearch_required
    def add_application(self, app='default', response=None):
        """add a youtube app to generate credentials"""
        if not response:


            app_prompt = {
                "header" : "Create a Youtube Application",
                "description" : "You will need a YouTube app to start collecting data \n"
                "from the YouTube service. You can create it by following these steps: \n"
                "\n"
                "1.  Go to https://console.developers.google.com/ \n"
                "2.  Click on the 'YouTube Data API' in the lower right corner \n"
                "3.  Agree with the Terms of service \n"
                "4.  Create a project with an arbitrary name (if you do not already have one) \n"
                "5.  Click on 'Enable', which is on a blue button next to 'YouTube Data API vX' \n"
                "6.  Click on 'Create Credentials', the blue button on the rigth side of the screen \n"
                "7.  For 'Which API are you using, keep the 'YouTube API v3 option' \n"
                "    For 'Where will you be calling the API from?' pick 'Other UI (e.g. Windows, CLI tool)' \n"
                "    For 'Which data will you be accessing', you can should pick 'User data' \n"
                "8.  Click 'What credentials do I need?' \n"
                "9.  Click 'Done', the blue button at the bottom \n"
                "10. Click on your application under the 'OAuth 2.0 client IDs'",

                "inputs" : [
                    {
                    "label" : "Application name",
                    "description" : "An internal identifier for your app ",
                    "help" : "The application name does not have to match that of the YouTube app",
                    "inputtype": "text",
                    "minimum": 4,
                    "maximum": 15,
                    "default":app

                    },
                    {
                    "label" : "Application Client Id",
                    "description" : "Please copy the API key shown under 'Get your credentials' ",
                    "help" : "The credentials should look something like '708587097539-gbpoflpng1ola0hbh4fcob3ugL1Dcy60.apps.googleusercontent.com'",
                    "inputtype": "text",
                    "minimum": 8,
                    "maximum": 20

                    },
                    {
                    "label" : "Application Client Secret",
                    "description" : "Please copy the API key shown under 'Get your credentials' ",
                    "help" : "The credentials should look something like 'AIzaWyBcVB4AB9zMF9LQbghB3yF5z13Tp'",
                    "inputtype": "text",
                    "minimum": 8,
                    "maximum": 20

                    },
                    {
                    "label" : "Now activate credential additions for your application",
                    "description" : "In the 'credentials' tab of the Google API overview click on 'OAuth consent screen'. \n"
                    "Here, you should fill in an email address and appname to be shown to users when adding credentials. \n"
                    "Once you have entered this information, click 'Done'",
                    "help" : "only the email and product name are required",
                    "inputtype": "bool",
                    "default" : "True"

                    }


                ]

            }

            response = self.prompt(app_prompt)
            return self.add_application(app=app, response=response)

        elif response:
            credentials = {'client_id': response['Application Client Id'],'client_secret':response["Application Client Secret"]}
            return self.store_application(appname=app, app_credentials=credentials)

    @elasticsearch_required
    def add_credentials(self, app='default'):
        """Add credentials for an app"""
        app = self.load_application(app=app)
        app_url = "https://accounts.google.com/o/oauth2/v2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.readonly&response_type=code&state=security_token%3D138r5719ru3e1%26url%3Dhttps://oauth2.example.com/token&redirect_uri=urn:ietf:wg:oauth:2.0:oob&client_id={app[client_id]}".format(**locals())
        credentials_prompt = {
            "header" : "add credentials to app {app}".format(**locals()),
            "description" : "Go to the below URL, select the account you want to add to this app [{app}] and click 'Allow'\n\nUrl:{app_url}".format(**locals()),
            "inputs" : [
                {
                "label" : "Please enter the authentication code:",
                "description" : "",
                "help" : "",
                "inputtype" : "text",
                "minimum" : 10
                }


            ]


        }
        pass
