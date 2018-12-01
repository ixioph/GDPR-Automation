from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import sys

class GetElementWrapper():

    eleNotFound = "Element Not Found: "
    eleFound = "Element Found!"
    unexpectedError = "An Unexpected Error Has Occured. \n"
    noSupport = "Locator type not supported."

    def __init__(self, driver):
        self.driver = driver

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

    # return True if element is not None else False
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
