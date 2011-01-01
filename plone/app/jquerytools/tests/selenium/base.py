import selenium
import os
import transaction
import unittest2 as unittest

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.app.testing import PLONE_SITE_ID
from plone.app.testing import FunctionalTesting
from plone.app.testing.layers import PLONE_FIXTURE
from plone.testing.z2 import ZServer
# from zope.configuration import xmlconfig

class HostAdjustableZServer(ZServer):
    host = os.environ.get('ZSERVER_HOST', 'localhost')
    port = int(os.environ.get('ZSERVER_PORT', 55001))
    
HOST_ADJUSTABLE_ZSERVER_FIXTURE = HostAdjustableZServer()

class SeleniumLayer(PloneSandboxLayer):
    defaultBases = (HOST_ADJUSTABLE_ZSERVER_FIXTURE, PLONE_FIXTURE)

    # Connection parameters
    seleniumHost = os.environ.get('SELENIUM_HOST', 'localhost')
    seleniumPort = os.environ.get('SELENIUM_PORT', '4444')
    seleniumBrowser = os.environ.get('SELENIUM_BROWSER', '*firefox')

    # def setUpZope(self, app, configurationContext):
    #     # load ZCML
    #     import assessmentmanagement.core
    #     xmlconfig.file('meta.zcml', assessmentmanagement.core, context=configurationContext)
    #     xmlconfig.file('configure.zcml', assessmentmanagement.core, context=configurationContext)

    def setUpPloneSite(self, portal):
        
        # Install Products
        quickInstallProduct(portal, 'assessmentmanagement.core')

        # Start up Selenium 
        url = "http://%s:%s/%s" % (self['host'], self['port'], PLONE_SITE_ID)
        self['selenium'] = selenium.selenium(self.seleniumHost, self.seleniumPort, self.seleniumBrowser, url)
        self['selenium'].start()

    def tearDownPloneSite(self, portal):
        self['selenium'].stop()
        del self['selenium']

SELENIUM_FIXTURE = SeleniumLayer()
SELENIUM_TESTING = FunctionalTesting(bases=(SELENIUM_FIXTURE,), name="SeleniumTesting:Functional")


class SeleniumTestCase(unittest.TestCase):
    layer = SELENIUM_TESTING

    def setUp(self):
        self.selenium = self.layer['selenium']

    def open(self, path="/", site_name=PLONE_SITE_ID):
        # ensure we have a clean starting point
        transaction.commit()
        self.selenium.open("/%s/%s" % (site_name, path,))

    def wait(self, timeout="30000"):
        self.selenium.wait_for_page_to_load(timeout)
        
    def waitForElement(self, selector, timeout="30000"):
        """Continue checking for the element matching the provided CSS
        selector."""
        self.selenium.wait_for_condition("""css="%s" """ % selector, timeout)
        