#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import codecs
import random
import string
import datetime

from datetime import date

from selenium import webdriver
from selenium.common.exceptions     import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by   import By
from selenium.webdriver.support.ui  import WebDriverWait
from selenium.webdriver.support     import expected_conditions as EC


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = codecs.open("Log_%s_%s_%s.log" % (today.year, today.month, today.day), mode = 'a')
    def write(self, message):
        if message not in ('\n', '\r', '\r\n'):
           sDateTime = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
           message = '%s\t%s' % (sDateTime, message)
        self.terminal.write(message)
        self.log.write(message)


class WebPageParams():
    def __init__(self, sUserEmail, sUserPassw):
        self.sStartUrlPath = r'https://vk.com'
        self.sWebPageTitle = u'Добро пожаловать | ВКонтакте'
        self.sCodePage     = 'utf-8'

        # Auth params
        self.sTagEmail    = 'quick_email'
        self.sTagPass     = 'quick_pass'
        self.sTagLoginBtn = 'quick_login_button'
        self.sUserEmail   =  sUserEmail
        self.sUserPassw   =  sUserPassw
        self.sMyProfWrap  = 'myprofile_wrap'

        # Search params
        self.sSearchUrl = r'https://vk.com/search?c[age_from]=14&c[age_to]=14&c[bday]=%s&c[bmonth]=%s&c[name]=1&c[online]=1&c[photo]=1&c[section]=people&c[sort]=1'
        self.sSearchUrl = self.sSearchUrl % (today.day, today.month)
        self.sSearchPgTitle = u'Поиск людей'
        self.sUserLinksPath = '.labeled.name a'

        # Show more btn params
        self.sShowMoreBtnId = "show_more_link"

        # Profile params
        self.sProfilePhotoId = 'profile_photo_link'
        self.sLikeId         = 'pv_like_wrap'
        self.sCaptcha        = 'captcha'
        self.sIsLikedId      = 'pv_like_icon'

        # Send message
        self.sUserForSend = r'https://vk.com/id288906178'
        self.sSendMessage = '//*[contains(@class, "flat_button profile_btn_cut_left")]'
        self.MailBox      = 'mail_box_editable'


class VkEmulatorAction():
      def __init__(self):
          # Friends
          self.FriendsDivClass    = '//*[contains(@class, "p_header_bottom")]'
          self.FriendsLinksClass  = '//*[contains(@class, "fl_l people_cell")]'
          # Images
          self.ProfilePhotosClass = '//*[contains(@class, "profile_photo_img")]'
          self.ProfilePhotosClass2 = '//*[contains(@class, "page_post_thumb_sized_photo")]'

          self.sCloseImageXPath   = '//*[contains(@class, "fl_r pv_close_link")]'
          self.sCloseImageXPath2   = '//*[contains(@class, "pv_close no_select")]'

          # Wall
          self.sPostsClass = '//*[contains(@class, "post own post_copy")]'
          self.sPostsClass2 = '//*[contains(@class, "post all own post_online")]'
          self.sPostsClass3 = '//*[contains(@class, "post all own")]'
          self.sClosePost   = '//*[contains(@class, "fl_r wk_close_link")]'


# Get only new user links
def GetSearchedBeforeLinks(setUserLinks):

    if not os.path.exists(sVkUserLinksCsvPath):
       return setUserLinks
    else:
       fVkUserLinksCsv = open(sVkUserLinksCsvPath, 'r')

    for sLink in fVkUserLinksCsv.readlines():
        sLink = sLink.replace('\n', '')
        if sLink in setUserLinks and sLink <> '':
           setUserLinks.discard(sLink)

    fVkUserLinksCsv.close()

    return setUserLinks

# Update liked User list into csv
def AddNewUserIntoCsv(sUserLink):
    if not os.path.exists(sVkUserLinksCsvPath):
       print 'Create file:', sVkUserLinksCsvPath
       fVkUserLinksCsv = open(sVkUserLinksCsvPath, 'w')
    else:
       fVkUserLinksCsv = open(sVkUserLinksCsvPath, 'a')

    fVkUserLinksCsv.write('%s\n' % sUserLink)
    fVkUserLinksCsv.flush()
    fVkUserLinksCsv.close()


def RunBrowser(objWebPageParams):

    Browser = webdriver.Firefox()
    Browser.get(objWebPageParams.sStartUrlPath) # Load page

    # Check title
    if objWebPageParams.sWebPageTitle not in Browser.title:
       raise SystemExit

    return Browser


def VkAuthorization(objWebPageParams):

    # find elements, enter login/pass, press login btn
    # Input email
    EmailElem = Browser.find_element_by_id(objWebPageParams.sTagEmail)
    EmailElem.send_keys(objWebPageParams.sUserEmail)

    # Input pass
    PassElem = Browser.find_element_by_id(objWebPageParams.sTagPass)
    PassElem.send_keys(objWebPageParams.sUserPassw)

    # Press login btn
    LoginBtnElem = Browser.find_element_by_id(objWebPageParams.sTagLoginBtn)
    LoginBtnElem.click()

    MyProfWrapElem = WebDriverWait(Browser, 10).until(EC.presence_of_element_located((By.ID, objWebPageParams.sMyProfWrap)))


def RunSearchByParams(objWebPageParams):
    Browser.get(objWebPageParams.sSearchUrl) # Load page

    # Check title
    if objWebPageParams.sSearchPgTitle not in Browser.title:
       raise SystemExit


def PressShowMore(objWebPageParams):
    # Press show more btn
    ShowMoreBtnElem = WebDriverWait(Browser, 10).until(EC.presence_of_element_located((By.ID, objWebPageParams.sShowMoreBtnId)))
    ShowMoreBtnElem.click()


def GetUserLinks(objWebPageParams):

    for n in xrange(1000):
        try:
            PressShowMore(objWebPageParams)
        except:
            break

    setUserLinks = set()

    # Get all user links on page
    for elemUserLink in Browser.find_elements_by_css_selector(objWebPageParams.sUserLinksPath):
        sUserLink = elemUserLink.get_attribute("href")
        setUserLinks.add(sUserLink)

    return setUserLinks


def GoToUserProfilesAndLikeMainPhoto(objWebPageParams, setUserLinks):
    # Go to each iser and like main photo
    for sUserLink in setUserLinks:

        try:

            # Go to photo link
            print '\tGo to photo link'
            Browser.get(sUserLink) # Load page

            print '\tClick to photo'
            ProfilePhotoElem = WebDriverWait(Browser, 2).until(EC.presence_of_element_located((By.ID, objWebPageParams.sProfilePhotoId)))
            ProfilePhotoElem.click()

            time.sleep(1)

            # Search HeartElem
            print '\tSearch HeartElem'
            HeartElem = WebDriverWait(Browser, 2).until(EC.presence_of_element_located((By.ID, objWebPageParams.sIsLikedId)))

            print '\tCheck like or not before'
            if HeartElem.get_attribute("style") == 'opacity: 1;':
                print '%s\tSKIPPED!' % sUserLink
                AddNewUserIntoCsv(sUserLink)
                continue

            print '\tClick to like element'
            LikeElem = WebDriverWait(Browser, 2).until(EC.presence_of_element_located((By.ID, objWebPageParams.sLikeId)))
            LikeElem.click()

            time.sleep(1)

            # Check like exists
            print '\tCheck like exists'
            HeartElem = WebDriverWait(Browser, 2).until(EC.presence_of_element_located((By.ID, objWebPageParams.sIsLikedId)))
            if HeartElem.get_attribute("style") <> 'opacity: 1;':
                print '%s\tSOME ERROR!' % sUserLink
                raise StandardError
            else:
                AddNewUserIntoCsv(sUserLink)

            time.sleep(1)

            print '\tCheck capcha'
            if GetElemOnceByVar(By.CLASS_NAME, objWebPageParams.sCaptcha):
                print '%s\tCAPCHA DETECTED!' % sUserLink
                return

        except:
            continue

        print '%s\tOK!' % sUserLink
        nWaitDelay = random.randrange(10,20)
        print 'Waiting %s' % nWaitDelay
        time.sleep(nWaitDelay)
        EmulateActions(5, sUserLink)

        print '\tSend random message'
        SendMessage(objWebPageParams)


def GetElemAttr(Elem, AttrName):
    ResultVal = None
    try:
        ResultVal = Elem.get_attribute(AttrName)
    except:
        pass
    return ResultVal


def GetElemListByVar(sByType, sSelectorValue):
    try:
        listResElem = Browser.find_elements(sByType, sSelectorValue)
    except:
        return False
    return listResElem


def GetElemOnceByVar(sByType, sSelectorValue):
    try:
        ResElem = Browser.find_element(sByType, sSelectorValue)
    except:
        return False
    return ResElem


def FindElemAndClick(sByType, sClassName):
    FoundedElem = GetElemListByVar(sByType, sClassName)
    if FoundedElem:
       for Elem in FoundedElem:
           Elem.click()


def EmulateActions(nCntOperations = 5, sUserLink = ''):

    def ClosePhoto(objVkEmulatorAction):
        FindElemAndClick(By.XPATH, objVkEmulatorAction.sCloseImageXPath)
        FindElemAndClick(By.XPATH, objVkEmulatorAction.sCloseImageXPath2)

    def ClosePost(objVkEmulatorAction):
        FindElemAndClick(By.XPATH, objVkEmulatorAction.sClosePost)

    def GetRandomElemFromList(sElemSelector):
        listFoundedElem = GetElemListByVar(By.XPATH, sElemSelector)
        if listFoundedElem and len(listFoundedElem) > 0:
           return listFoundedElem[random.randrange(0,len(listFoundedElem) - 1)]
        return None

    # Go to random friend if exists
    def GoToRandomFriend(objVkEmulatorAction):
        RandomFriendElem = GetRandomElemFromList(objVkEmulatorAction.FriendsLinksClass)
        if RandomFriendElem:
           RandomFriendElem.click()

    # Look random photo if exists
    def LookRandomPhoto(objVkEmulatorAction):
        # Find photo
        RandomPhotoElem = GetRandomElemFromList(objVkEmulatorAction.ProfilePhotosClass)

        if not RandomPhotoElem:
           RandomPhotoElem = GetRandomElemFromList(objVkEmulatorAction.ProfilePhotosClass2)

        if RandomPhotoElem:
           # Open photo
           RandomPhotoElem.click()
           # Close photo
           time.sleep(3)
           ClosePhoto(objVkEmulatorAction)

    # Open Random post if exists
    def OpenRandomPost(objVkEmulatorAction):
      # Search any posts
      RandomPostElem = GetRandomElemFromList(objVkEmulatorAction.sPostsClass)

      if not RandomPostElem:
         RandomPostElem = GetRandomElemFromList(objVkEmulatorAction.sPostsClass2)

      if not RandomPostElem:
         RandomPostElem = GetRandomElemFromList(objVkEmulatorAction.sPostsClass3)

      if RandomPostElem:
         # Open random post
         RandomPostElem.click()
         # Close post
         time.sleep(3)
         ClosePost(objVkEmulatorAction)

    listTasks = [GoToRandomFriend, LookRandomPhoto]

    try:
        ClosePhoto(objVkEmulatorAction)
    except:
        pass

    while (nCntOperations > 0):

        time.sleep(3)

        try:
            CurrentAction = random.choice(listTasks)
            CurrentAction(objVkEmulatorAction)
        except:
            Browser.get(sUserLink)

        nCntOperations -= 1


def SendMessage(objWebPageParams):
    try:
        Browser.get(objWebPageParams.sUserForSend)
        time.sleep(2)
        FindElemAndClick(By.XPATH, objWebPageParams.sSendMessage)
        time.sleep(2)
        MailBoxElem = Browser.find_element_by_id(objWebPageParams.MailBox)
        sRandomString = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(16))
        time.sleep(2)
        MailBoxElem.send_keys(sRandomString + Keys.CONTROL + Keys.RETURN)
    except:
          print 'Error with send message'


# Run if the module not imported but call from bat file
if __name__ == '__main__':

    # Define global constants
    today = date.today()
    objWebPageParams    = WebPageParams(sys.argv[1].split(';')[0], sys.argv[1].split(';')[1])
    nLikeCnt = int(sys.argv[2])
    objVkEmulatorAction = VkEmulatorAction()

    # Run browser
    print 'Run browser'
    Browser = RunBrowser(objWebPageParams)

    # [TBD:Exit if authorizated] Authorization
    print 'Authorization'
    VkAuthorization(objWebPageParams)

    # Search users by params
    print 'Search users by params'
    RunSearchByParams(objWebPageParams)

    # Get all user link on current page
    print 'Get all user link on current page'
    setUserLinks = GetUserLinks(objWebPageParams)
    print '%s Links founded' % len(setUserLinks)

    # Remove liked in the past users
    print 'Remove liked in the past users'
    setUserLinks = GetSearchedBeforeLinks(setUserLinks)
    print '%s Links after filter' % len(setUserLinks)

    # Go each user profile and "Like" main photo
    # Get next users while not end users list
    print 'Start like users total cnt = %s' % nLikeCnt
    setUserLinks = set(list(setUserLinks)[0:nLikeCnt])
    GoToUserProfilesAndLikeMainPhoto(objWebPageParams, setUserLinks)

    print 'Quit browser'
    Browser.quit()

