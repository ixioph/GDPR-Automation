# GDPR-Automation
## Summary
A python script which utilizes the Selenium webdriver to automate the conversion of General Data Protection Regulation customer requests, received within Zendesk, into Jira tickets. Written for the **Chrome Browser**.<br><br>
This script requires a confguration file(format provided below) containing the necessary credentials and links in order to navigate the sites unimpeded.<br><br>
It works by first logging into the Zendesk and Jira services, then navigating to the GDPR queue (where the first field has been made request number)
## Pseudocode

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

## Table of Contents
  * [Dependencies](#dependencies)
  * [Known Issues](#known-issues)
  * [Configuration](#configuration)
  * [Noteworthy Classes](#noteworthy-classes)
    - [GDPRRequester](#gdprrequester)
    - [JiraAgent](#jiraagent)
    - [ZendeskAgent](#zendeskagent)
    - [GetElementWrapper](#getelementwrapper)
  * [Functions](#functions)
    - [ZendeskAgent.login()](#zendeskagent.login)
    - [JiraAgent.login()](#jiraagent.login)
    - [ZendeskAgent.scanQueue()](#zendeskagent.scanqueue)
    - [GDPRRequester.gatherInfo()](#gdprrequester.gatherinfo)
    - [JiraAgent.createTicket()](#jiraagent.createticket)
    - [JiraAgent.storeDataKey()](#jiraagent.storedatakey)
    - [ZendeskAgent.respondInternal()](#zendeskagent.respondinternal)
    - [ZendeskAgent.respondWipeMacro()](#zendeskagent.respondwipemacro)
    - [GetElementWrapper.getByType()](#getelementwrapper.getbytype)
    - [GetElementWrapper.getElement()](#getelementwrapper.getelement)
    - [GetElementWrapper.isElementPresent()](#getelementwrapper.iselementpresent)
## Dependencies
This script was written in Python3 and requires the [Selenium Python webdriver](https://selenium-python.readthedocs.io/installation.html).
## Known issues
  * When submitting a Zendesk ticket, the submission type (Open, Pending, Solved) can't be selected
  * When grabbing the GDPR tickets, currently only the first page is stored
  * When creating the Jira issue, either _Project_ or _Issue type_ will remain unchanged, depending on which is first
## Configuration
The config file is named _gdparse.ini_ and has been the following format:
```
[credentials]
zendesk_uid = <zendesk account email>
zendesk_upw = <zendesk password>
jira_uid = <google sign-in jira email>
jira_upw = < google sign-in password>

[links]
zendesk_gdpr_queue = https://YOUR-SUBDOMAIN.zendesk.com/agent/filters/YOUR-VIEW-NUM
zendesk_ticket_prepend = https://YOUR-SUBDOMAIN.zendesk.com/agent/tickets/
zendesk_login = https://YOUR-SUBDOMAIN.zendesk.com/auth/v2/login/signin?
jira_login = https://id.atlassian.com/login
jira_dashboard = https://YOUR-SUBDOMAIN.atlassian.net/secure/Dashboard.jspa
jira_reported_by_me = https://YOUR-SUBDOMAIN.atlassian.net/issues/?filter=-2

[text-fields]
jira_tx_summary = GDPR Request From:
jira_tx_labels = <your organization's labels>
```
## Noteworthy Classes
### GDPRRequester
Handles the information associated with the source Zendesk request, such as user identification (email, account ID) and ticket information.
### JiraAgent
Handles all of the functions associated with the Jira account, such as data key retrieval and ticket creation.
### ZendeskAgent
Handles all of the functions associated with the Zendesk account, such as queue parsing and ticket responses and tagging.
### GetElementWrapper
Wrapper that modularizes and does exception handling for common Selenium element queries.
## Functions
#### ZendeskAgent.login
Responsible for finding and filling the fields necessary to log into the Zendesk support page.
```python
def login(self, driver, driverElements):
    driver.implicitly_wait(5)
    driver.get(self.loginURL)
    driver.implicitly_wait(10)
    accountEmail = driverElements.getElement("user_email")
    accountEmail.send_keys(self.agentEmail)
    time.sleep(1)
    accountPass = driverElements.getElement("user_password")
    accountPass.send_keys(self.agentPassword)
    time.sleep(1)
    rememberMe = driverElements.getElement("remember_me")
    rememberMe.click()
    time.sleep(1)
    signInBtn = driverElements.getElement("//*[@id='login-form']/input[9]","xpath")
    signInBtn.click()
    print("Logging into Zendesk as: " + self.agentEmail)
    time.sleep(5)
```
#### JiraAgent.login
Responsible for finding and filling the fields necessary to log into the Jira dashboard.
```python
  def login(self, driver, driverElements):
    driver.implicitly_wait(5)
    driver.get(self.loginURL)
    driver.implicitly_wait(10)
    googleSignIn = driverElements.getElement("//*[@id='google-signin-button']","xpath")
    time.sleep(1)
    googleSignIn.click()
    driver.implicitly_wait(10)

    accountEmail = driverElements.getElement("//*[@id='identifierId']","xpath")
    accountEmail.send_keys(self.agentEmail)
    time.sleep(1)
    driverElements.getElement("//*[@id='identifierNext']", "xpath").click()
    driver.implicitly_wait(10)

    accountPass = driverElements.getElement("password", "name")
    accountPass.send_keys(self.agentPassword)
    time.sleep(1)
    driverElements.getElement("//*[@id='passwordNext']","xpath").click()
    print("Logging into Jira as: " + self.agentEmail)
    time.sleep(6)
    driver.implicitly_wait(10)

    print(driver.current_url)

    driver.get(self.dashboardURL)
    driver.implicitly_wait(10)
    time.sleep(1)
```
#### ZendeskAgent.scanQueue
Iterates over the list of Zendesk requests and creates an array of GDPRRequester objects.
```python
def scanQueue(self, driver, prepend):
    requestQueue = []
    for tick in driver.find_elements_by_css_selector("tr.LRbd"):
        #create a new GDPR requester
        requester = GDPRRequester()
        requester.setTicket(tick.find_elements_by_css_selector("td")[4].text[1:])
        print(requester.ticketNum)
        requester.ticketURL = prepend + requester.ticketNum
        requestQueue.append(requester)
    return requestQueue
```
#### GDPRRequester.gatherInfo
Scrapes the ticket for relevant user information for storing within the GDPRRequester object.
```python
def gatherInfo(self, driver, driverElements):
    self.setEmail(driverElements.getElement("span.sender > a.email", "css selector").text)
    driver.implicitly_wait(12)
    self.setMessage(driver)
    driver.implicitly_wait(12)
```
#### JiraAgent.createTicket
Using the information provided from the Zendesk ticket, creates a Jira ticket.
```python
def createTicket(self, requester, driver, driverElements):
    driver.get(self.dashboardURL)
    driver.implicitly_wait(10)
    time.sleep(2)
    #open 'create' menu
    print("Launching the Jira creation popup")
    try:
        ActionChains(driver).send_keys('c').perform()
    except:
        print('Error Opening Jira Ticket Creation: ', sys.exc_info()[0])

    #summary is: "GDPR // Wipe // user: <requester-email>"
    summaryField = driverElements.getElement('//input[@id="summary"]', "xpath")
    descriptionField = driverElements.getElement('//textarea[@id="description"]', "xpath")
    tickLabels = driverElements.getElement('//textarea[@id="labels-textarea"]', "xpath")
    projectField = driverElements.getElement('//input[@id="project-field"]', "xpath")
    issueField = driverElements.getElement('//input[@id="issuetype-field"]', "xpath")

    summaryFieldType = self.ticketPrepend + " " + requester.email

    print("Filling in Jira ticket details")

    try:
        ActionChains(driver).move_to_element(summaryField).click().perform()
        summaryField.send_keys(summaryFieldType)

        #description is user message
        ActionChains(driver).move_to_element(descriptionField).click().perform()
        descriptionField.send_keys(requester.message)

        #labels "gdpr" and "wipe"
        ActionChains(driver).move_to_element(tickLabels).click().perform()
        tickLabels.send_keys(self.ticketLabel)
    except:
        print("Failed to fill in user information: ", sys.exc_info()[0])

    #project type is customer support
    try:
        ActionChains(driver).move_to_element(projectField).click().send_keys(self.projectFieldText).perform()
        time.sleep(1)
    except InvalidElementStateException:
        print("Project Type " + self.actionFieldFail)
        try:
            projectField.click()
            projectField.send_keys(self.projectFieldText)
            time.sleep(1)
        except InvalidElementStateException:
            print("Invalid Element State Exception. Exiting...")
            print(sys.exc_info()[0])
            exit()
        except:
            print(self.unexpectedError, sys.exc_info()[0])
    except:
        print(self.unexpectedError, sys.exc_info()[0])

    #issue type is request
    try:
        ActionChains(driver).move_to_element(issueField).click().send_keys(self.issueFieldText).perform()
        time.sleep(1)
    except InvalidElementStateException:
        print("Issue Type " + self.actionFieldFail)
        try:
            issueField.click()
            issueField.send_keys(self.issueFieldText)
            time.sleep(1)
        except InvalidElementStateException:
            print("Invalid Element State Exception. Exiting...")
            print(sys.exc_info()[0])
            exit()
        except:
            print(self.unexpectedError, sys.exc_info()[0])
    except:
        print(self.unexpectedError, sys.exc_info()[0])

    print("Fields have been completed. Creating Ticket.")
    #create that shit, yo
    createBtn = driverElements.getElement('//input[@id="create-issue-submit"]',"xpath")
    createBtn.click()
    print("Ticket Created.")
```
#### JiraAgent.storeDataKey
Uses the requester's email address (which was placed into the Jira ticket summary) to locate the "data-key" attribute
```python
def storeDataKey(self, requester, driver, driverElements):
    #gdpr = 1
    driver.get(self.reportedIssuesURL)
    time.sleep(3)
    driver.implicitly_wait(10)

    titleText = self.ticketPrepend + requester.email
    print("Grabbing the Jira Data Key...")

    try:
        print("searching for xpath: " + '//*[@title="' + titleText + '"]')
        #driverElements.getElement('//li[contains(@title, "' + requester.email + '")]', 'xpath')
        #titleXpath = '//*[@title="' + titleText + '"]'
        titleXpath = '//li[contains(@title, "' + requester.email + '")]'
        title = driverElements.getElement(titleXpath, "xpath")
        print(str(title))
        requester.jira = title.get_attribute("data-key")
    except:
        print("Error grabbing the data key: ", sys.exc_info()[0])
        return False
    print("Grabbed Jira: " + requester.jira)
```
#### ZendeskAgent.respondInternal
Places an internal note containing the corresponding Jira data-key in a Zendesk ticket
```python
def respondInternal(self, driver, driverElements, url, msg):
    driver.get(url)
    driver.implicitly_wait(12)
    print("Tagging Zendesk ticket with Jira data key")
    intNoteBtn = driverElements.getElement('//span[text()[contains(., "Internal note")]]', "xpath")
    #driverElements.getElement('//li[contains(@title, "' + requester.email + '")]', 'xpath')
    print(intNoteBtn.text)
    intNoteBtn.click()
    time.sleep(1)
    commentField = driverElements.getElement("div.ember-view > textarea", "css selector")
    commentField.send_keys(msg)
    time.sleep(2)
    driver.implicitly_wait(10)
    submitBtn = driverElements.getElement("button[data-test-id*='submit_button-button']", "css selector")
    try:
        ActionChains(driver).move_to_element(submitBtn).click().perform()
        time.sleep(1)
    except InvalidElementStateException:
        print("Invalid Element State: ",sys.exc_info()[0])
        try:
            submitBtn.click()
            time.sleep(1)
        except InvalidElementStateException:
            print(sys.exc_info()[0])
            exit()
        except:
            print(self.unexpectedError, sys.exc_info()[0])
    except:
        print(self.unexpectedError, sys.exc_info()[0])
```
#### ZendeskAgent.respondWipeMacro
Submits a response to the requester which notifies them that their request has been added to the queue
```python
def respondWipeMacro(self, driver, driverElements, url):
    #driver.get(url)
    driver.implicitly_wait(12)
    #replyBtn = driverElements.getElement('//span[text()[contains(., "Public reply")]]', "xpath")
    #print(replyBtn.text)
    #replyBtn.click()
    time.sleep(1)
    commentField = driverElements.getElement("div.ember-view > textarea", "css selector")
    commentField.send_keys(self.wipeMacro)
    time.sleep(2)
    driver.implicitly_wait(10)
    submitBtn = driverElements.getElement("button[data-test-id*='submit_button-button']", "css selector")
    try:
        ActionChains(driver).move_to_element(submitBtn).click().perform()
        time.sleep(1)
    except InvalidElementStateException:
        print("Invalid Element State: ",sys.exc_info()[0])
        try:
            submitBtn.click()
            time.sleep(1)
        except InvalidElementStateException:
            print(sys.exc_info()[0])
            exit()
        except:
            print(self.unexpectedError, sys.exc_info()[0])
    except:
        print(self.unexpectedError, sys.exc_info()[0])
```
#### GetElementWrapper.getByType
Returns the appropriate Selenium *By attribute* based on the provided string.
```python
def getByType(self, type):
    type = type.lower()
    if type == 'id':
        return By.ID
    elif type == 'xpath':
        return By.XPATH
    elif type == 'class name':
        return By.CLASS_NAME
    elif type == 'css selector':
        return By.CSS_SELECTOR
    elif type == 'link text':
        return By.LINK_TEXT
    elif type == 'partial link text':
        return By.PARTIAL_LINK_TEXT6
    elif type == 'tag name':
        return By.TAG_NAME
    elif type == 'name':
        return By.NAME
    else:
        print(self.noSupport)
        return False
```
#### GetElementWrapper.getElement
Returns an element when provided with a locator/identifier and a query type.
```python
def getElement(self, locator, queryType="id"):
    element = None
    try:
        queryType = queryType.lower()
        byType = self.getByType(queryType)
        element = self.driver.find_element(byType, locator)
        print(self.eleFound)
    except NoSuchElementException:
        print(self.eleNotFound, sys.exc_info()[0])
    except:
        print(self.unexpectedError, sys.exc_info()[0])
    return element
```
#### GetElementWrapper.isElementPresent
Exception handling. Checks whether the provided criteria returns a match within the DOM.
```python
def isElementPresent(self, locator, byType):
    element = None
    try:
        element = self.driver.find_element(byType, locator)
        if element is not None:
            print(self.eleFound)
            return True
        else:
            return False

    except NoSuchElementException:
        print(self.eleNotFound, sys.exc_info()[0])
        return False
    except:
        print(self.unexpectedError, sys.exc_info()[0])
        return False
```
