# okta-portal
This is a basic Flask app that allows support engineers to manage Okta users without using the Okta console where they may have too many permissions for other areas. It uses an Okta OpenID connect for authentication.

Refer to: https://www.okta.com/free-trial/workforce-identity to create a free trial account. Steps to create a new application in Okta are here: https://help.okta.com/en-us/Content/Topics/Apps/Apps_App_Integration_Wizard_OIDC.htm

When creating a new Okta app, select the "Client authentication" option and save off the client id and the client secret.
Use the 2 PNG screenshot files for help.

You need 2 variables:
TOKEN (Okta API Token) and URLBASE (ex: 'https://YOURNAME.okta.com')

(Make sure the Okta token is a user with Super admin privileges)

Steps to run the container:

1) Edit the file "client_secrets.json" and add the Okta secret and URL information
2) Edit the "go" script and add your TOKEN and URLBASE variables
3) Run the "go" script
4) You can now add users to this application.  Refer to: https://help.okta.com/en-us/Content/Topics/users-groups-profiles/usgp-assign-apps.htm

By default it will run on port 5000.
