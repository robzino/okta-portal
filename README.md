# okta-platform
This is a basic Flask app that allows support engineers to manage Okta users without using the Okta console where they may have too many permissions for other areas. It uses an Okta OpenID connect application for authentication.

Refer to: https://www.okta.com/free-trial/workforce-identity to create a free trial account. Steps to create a new application in Okta are here: https://help.okta.com/en-us/Content/Topics/Apps/Apps_App_Integration_Wizard_OIDC.htm When creating a new Okta app, select the "Client authentication" option and save off the client id and the client secret.

To run launch you need 2 ENV vars:

TOKEN (Okta API Token)

URLBASE (ex: 'https://YOURNAME.okta.com')
(Make sure the Okta token is a user with Super admin privileges)

To run the container: docker run -d -e TOKEN='5vZJod...' -e URLBASE='https://YOURNAME.okta.com' -v $(pwd)/config:/app/config -p 5000:5000 robzino/public_images:okta-portal.20b

By default it will run on port 5000.
