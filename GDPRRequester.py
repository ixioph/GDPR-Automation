from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
import sys

class GDPRRequester():
    name = ""
    email = ""
    message = ""
    accountID = ""
    ticketNum = ""
    ticketURL = ""
    jira = ""
    reportFile = "outFile.out"

    def setName(self, name):
        self.name = name

    def setID(self, id):
        self.accountID = id

    def setTicket(self, tick):
        self.ticketNum = tick

    def setEmail(self, email):
        self.email = email

    def setMessage(self, driver):
        for paragraph in driver.find_elements_by_css_selector("div.comment > div.zd-comment > p"):
            self.message += paragraph.text

    def gatherInfo(self, driver, driverElements):
        self.setEmail(driverElements.getElement("span.sender > a.email", "css selector").text)
        driver.implicitly_wait(12)
        self.setMessage(driver)
        driver.implicitly_wait(12)

    def markAsReported(self):
        #Takes the returned key after Jira creation and saves all of the user information for replying later
        outFile = open(self.reportFile, "a+")
        outFile.write(self.email + ";" + self.jira + ";" + self.ticketNum + "\n") #user print command here?
        outFile.close()
        #return key
