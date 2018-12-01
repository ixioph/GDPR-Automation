# GDPR-Automation
## Brief
A python script which utilizes the Selenium webdriver to automate the conversion of General Data Protection Regulation customer requests, received within Zendesk, into Jira tickets. Written for the **Chrome Browser**.
## Summary 
This script requires an initialization file(format provided below) containing the necessary credentials and links in order to navigate the sites unimpeded. 
It works by first logging into the Zendesk and Jira services, then navigating to the GDPR queue (where the first field has been made request number)
>     Navigate to Zendesk website
>         enter username and password and login from gdparse.ini file
>     Navigate to the Jira website
>         enter username and password and login from gdparse.ini
>     Navigate to GDPR queue
>         for each item on page:
>             open the item, create a new gdpr ticket object with the email and message
>             navigate to the jira website
>                 create a new ticket and populate it with the object properties
>                 return the resulting Jira ticket number
>             place the Jira ticket number in an internal comment on Zendesk and submit
>             use the GDPR macro from gdparse.ini and submit
## Dependencies
This script was written in Python3 and requires the [Selenium Python webdriver](https://selenium-python.readthedocs.io/installation.html).
## Noteworthy Classes
### GDPRRequester()
Handles the information associated with the source Zendesk request, such as user identification (email, account ID) and ticket information.
### JiraAgent()
Handles all of the functions associated with the Jira account, such as data key retrieval and ticket creation.
### ZendeskAgent()
Handles all of the functions associated with the Zendesk account, such as queue parsing and ticket responses and tagging.
### GetElementWrapper()
Wrapper that modularizes and does exception handling for common Selenium element queries.
## Functions
#### ZendeskAgent.login()
Responsible for finding and filling the fields necessary to log into the Zendesk support page.
#### JiraAgent.login()
Responsible for finding and filling the fields necessary to log into the Jira dashboard.
#### ZendeskAgent.scanQueue()
Iterates over the list of Zendesk requests and creates an array of GDPRRequester objects.
#### GDPRRequester.gatherInfo()
Scrapes the ticket for relevant user information for storing within the GDPRRequester object.
#### JiraAgent.createTicket
Using the information provided from the Zendesk ticket, creates a Jira ticket.
#### JiraAgent.storeDataKey()
Uses the requester's email address (which was placed into the Jira ticket summary) to locate the "data-key" attribute
#### ZendeskAgent.respondInternal()
Places an internal note containing the corresponding Jira data-key in a Zendesk ticket
#### ZendeskAgent.respondWipeMacro()
Submits a response to the requester which notifies them that their request has been added to the queue
#### GetElementWrapper.getByType()
Returns the appropriate Selenium *By attribute* based on the provided string.
#### GetElementWrapper.getElement()
Returns an element when provided with a locator/identifier and a query type.
#### GetElementWrapper.isElementPresent()
Exception handling. Checks whether the provided criteria returns a match within the DOM.
