from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
import configparser
import time
import sys

from GetElementWrapper import GetElementWrapper
from ZendeskAgent import ZendeskAgent
from JiraAgent import JiraAgent

# Automation Steps:
#     Go to Zendesk website
#         enter username and password and login
#     Go to the Jira website
#         enter username and password and login
#     Navigate to GDPR queue
#         for each item on page:
#             open the item, create a new gdpr ticket object with the email and message
#             navigate to the jira website
#                 create a new ticket and populate it with the object properties
#                 return the resulting Jira ticket number
#             place the Jira ticket number in an internal comment on Zendesk and submit
#             use the GDPR macro and place the ticket on hold
#     close the GDPRProgram

class HandleGDPRTickets():

    def automate(self):

        parser = configparser.ConfigParser()
        parser.read('gdparse.ini')
        print("Parser output: ")
        print(parser.sections())

        gdprQueue = parser.get('links','zendesk_gdpr_queue')
        prepend = parser.get('links','zendesk_ticket_prepend')
        zendeskSite = parser.get('links','zendesk_login')
        jiraSite = parser.get('links','jira_login')

        zendeskQueue = []

        driver = webdriver.Chrome()
        driverElements = GetElementWrapper(driver)

        zAgent = ZendeskAgent(parser)
        zAgent.login(driver, driverElements)
        time.sleep(2)

        jAgent = JiraAgent(parser)
        jAgent.login(driver, driverElements)
        time.sleep(2)

        driver.get(gdprQueue)
        driver.implicitly_wait(12)
        zendeskQueue = zAgent.scanQueue(driver, prepend)
        for requester in zendeskQueue:
            driver.get(requester.ticketURL)
            driver.implicitly_wait(12)

            requester.gatherInfo(driver, driverElements)
            print(requester.ticketNum)

            jAgent.createTicket(requester, driver, driverElements)
            jAgent.storeDataKey(requester, driver, driverElements)

            zAgent.respondInternal(driver, driverElements, requester.ticketURL, requester.jira)
            zAgent.respondWipeMacro(driver, driverElements, requester.ticketURL)

        time.sleep(25)


GDPRProgram = HandleGDPRTickets()
GDPRProgram.automate()
