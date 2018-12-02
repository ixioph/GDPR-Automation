from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
import configparser
import time
import sys

from GetElementWrapper import GetElementWrapper

class JiraAgent():
    loginURL = ''
    dashboardURL = ''
    reportedIssuesURL = ''
    ticketPrepend = ''
    ticketLabel = ''
    actionFieldFail = "Field Selection Failed! Trying again without ActionChains..."
    unexpectedError = "An Unexpected Error Has Occured. \n"
    agentEmail = ""
    agentPassword = ""
    projectFieldText = "Customer Support (CS)"
    issueFieldText = "Request"

    def __init__(self, parser):
        self.agentEmail = parser.get('credentials', 'jira_uid')
        self.agentPassword = parser.get('credentials', 'jira_upw')

        self.loginURL = parser.get('links', 'jira_login')
        self.dashboardURL = parser.get('links', 'jira_dashboard')
        self.reportedIssuesURL = parser.get('links', 'jira_reported_by_me')
        self.ticketPrepend = parser.get('text-fields', 'jira_tx_summary')
        self.ticketLabel = parser.get('text-fields', 'jira_tx_labels')

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

            ActionChains(driver).move_to_element(descriptionField).click().perform()
            descriptionField.send_keys(requester.message)

            ActionChains(driver).move_to_element(tickLabels).click().perform()
            tickLabels.send_keys(self.ticketLabel)
        except:
            print("Failed to fill in user information: ", sys.exc_info()[0])


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
        createBtn = driverElements.getElement('//input[@id="create-issue-submit"]',"xpath")
        createBtn.click()
        print("Ticket Created.")

    def storeDataKey(self, requester, driver, driverElements):
        #gdpr = 1
        driver.get(self.reportedIssuesURL)
        time.sleep(3)
        driver.implicitly_wait(10)

        titleText = self.ticketPrepend + requester.email
        print("Grabbing the Jira Data Key...")

        try:
            print("searching for xpath: " + '//*[@title="' + titleText + '"]')
            titleXpath = '//li[contains(@title, "' + requester.email + '")]'
            title = driverElements.getElement(titleXpath, "xpath")
            print(str(title))
            requester.jira = title.get_attribute("data-key")
        except:
            print("Error grabbing the data key: ", sys.exc_info()[0])
            return False
        print("Grabbed Jira: " + requester.jira)
