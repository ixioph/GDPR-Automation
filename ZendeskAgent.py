from selenium.common.exceptions import InvalidElementStateException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
import configparser
import time
import sys

from GetElementWrapper import GetElementWrapper
from GDPRRequester import GDPRRequester

class ZendeskAgent():
    parser = configparser.ConfigParser()
    parser.read('config.ini')
    loginURL = ''
    agentEmail = ""
    agentPassword = ""
    unexpectedError = "An Unexpected Error has Occurred: "
    wipeMacro = "Hi there,\n\nThanks so much for emailing in. The security of your data is important to us! We have reached out to our internal operations to have your data removed in its entirety. \n\nYour request has been placed into the queue--We will notify you just as soon as it has been processed. Thank you for your continued patience!"

    def __init__(self, parser):
        self.agentEmail = parser.get('credentials','zendesk_uid')
        self.agentPassword = parser.get('credentials','zendesk_upw')
        self.loginURL = parser.get('links', 'zendesk_login')

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

    def scanQueue(self, driver, prepend):
        requestQueue = []
        for tick in driver.find_elements_by_css_selector("tr.LRbd"):
            requester = GDPRRequester()
            requester.setTicket(tick.find_elements_by_css_selector("td")[4].text[1:])
            print(requester.ticketNum)
            requester.ticketURL = prepend + requester.ticketNum
            requestQueue.append(requester)
        return requestQueue


    def respondInternal(self, driver, driverElements, url, msg):
        driver.get(url)
        driver.implicitly_wait(12)
        print("Tagging Zendesk ticket with Jira data key")
        intNoteBtn = driverElements.getElement('//span[text()[contains(., "Internal note")]]', "xpath")
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

    def respondWipeMacro(self, driver, driverElements, url):
        driver.implicitly_wait(12)
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







#EOF
