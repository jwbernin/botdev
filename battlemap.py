import requests
import re
import json
import time
from enum import Enum
import pprint

class Battlemap(object):

  def get_cookies(self):
      """ opens a fake browser to get the cookies needed """
      from robobrowser import RoboBrowser
      browser = RoboBrowser(user_agent='Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5', parser='html.parser')
      browser.open('https://battlemap.deltatgame.com/home#')
      link = browser.find('a')
      browser.follow_link(link)
      form=browser.get_form(0)

      with open('battlecreds.json') as credentialfile:
          credentials = json.load(credentialfile)
          form['Email'] = credentials['email']
          browser.submit_form(form)
          form=browser.get_form(0)
          form['Passwd'] = credentials['password']
          browser.submit_form(form)
          browser.open('https://battlemap.deltatgame.com/home')

      self.battlemap_token = browser.session.cookies.get('battlemap_session')
      self.xsrf = browser.session.cookies.get('XSRF-TOKEN')
      self.cookietimeout = time.time() + 60*60*1.95
      # GET csrf-token META HERE
      self.csrf = ''
      self.brow = browser
      from bs4 import BeautifulSoup
      soup = BeautifulSoup(str(browser.parsed()), "html.parser")
      for tag in soup.find_all('meta'):
        if 'name' in tag.attrs and tag.attrs['name'] == 'csrf-token':
          self.csrf = tag.attrs['content']


  def __init__ (self):
    self.session = requests.Session()
    headers = {
      'authority' : 'battlemap.deltatgame.com',
      'method':'GET',
      'scheme':'https',
      'accept':'*/*',
      'accept-encoding':'gzip, deflate, br',
      'accept-language':'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4',
      'cookie':'',
      'referer':'https://battlemap.deltatgame.com/home',
      'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
      'x-requested-with':'XMLHttpRequest'
    }
    self.session.headers.update(headers)
    self.cookietimeout = 0
    self.factions = {
      1:{
        'Faction name' : 'Nyoko Labs',
        'Color name'   : 'yellow',
        'Color code'   : '#ffa200'
      },
      2:{
        'Faction name' : 'Cosmostellar',
        'Color name'   : 'green',
        'Color code'   : '#22f233'
      },
      3:{
        'Faction name' : 'Gene X',
        'Color name'   : 'blue',
        'Color code'   : '#005eff'
      },
      4:{
        'Faction name' : 'Humanoid',
        'Color name'   : 'red',
        'Color code'   : '#f70b10'
      },
      5:{
        'Faction name' : 'Neutral',
        'Color name'   : 'white',
        'Color code'   : '#ffffff'
      }
    }

  def fetch(self, url, data):
    # get new cookies if needed
    if self.cookietimeout < time.time():
      print ("Getting new cookies")
      self.get_cookies()

    retrys = 3
    while retrys > 0:
      try:
        self.session.headers.update({'x-csrf-token': self.csrf})
        cookie_header = '_ga=GA1.2.220295278.1504376854; _gid=GA1.2.631065873.1504376854; XSRF-TOKEN=' + self.xsrf + '; battlemap_session=' + self.battlemap_token

        if data == None or data == '':
          request = self.session.post(url, headers= {'cookie': cookie_header})
        else:
          request = self.session.post(url, headers= {'cookie': cookie_header}, data=data)

        if 'set-cookie' in request.headers.keys():
          try:
            self.xsrf = re.findall(r'XSRF-TOKEN=(\S*);', request.headers['set-cookie'])[0]
          except IndexError:
            print ("Unable to set XSRF token!")
          self.battlemap_token = re.findall(r'battlemap_session=(\S*);',request.headers['set-cookie'])[0]
          self.cookietimeout = time.time() + 60*60* 1.95

        return request.json()

      except ValueError as ve:
        retrys -= 1
        time.sleep(2)
        pprint.pprint(ve)
        print("fetching request failed with ValueError")
      except KeyError:
        retrys -= 1
        time.sleep(2)
        print("KeyError")
    print("fetch failed completly\n" + url + "\n" + str(self.session.headers))
    return None
 
  def fetchRaw(self, url, data):
    # get new cookies if needed
    if self.cookietimeout < time.time():
      print ("Getting new cookies")
      self.get_cookies()

    retrys = 3
    while retrys > 0:
      try:
        self.session.headers.update({'x-csrf-token': self.csrf})
        cookie_header = '_ga=GA1.2.220295278.1504376854; _gid=GA1.2.631065873.1504376854; XSRF-TOKEN=' + self.xsrf + '; battlemap_session=' + self.battlemap_token

        if data == None or data == '':
          request = self.session.post(url, headers= {'cookie': cookie_header})
        else:
          request = self.session.post(url, headers= {'cookie': cookie_header}, data=data)

        if 'set-cookie' in request.headers.keys():
          self.xsrf = re.findall(r'XSRF-TOKEN=(\S*);', request.headers['set-cookie'])[0]
          self.battlemap_token = re.findall(r'battlemap_session=(\S*);',request.headers['set-cookie'])[0]
          self.cookietimeout = time.time() + 60*60* 1.95

        return request.text

      except ValueError as ve:
        retrys -= 1
        time.sleep(2)
        pprint.pprint(ve)
        print("fetching request failed with ValueError")
      except KeyError:
        retrys -= 1
        time.sleep(2)
        print("KeyError")
    print("fetch failed completly\n" + url + "\n" + str(self.session.headers))
    return None





  '''all-maps'''
  def getOwnDominanceData(self):
    url = 'https://battlemap.deltatgame.com/get-own-dominance-data'
    return self.fetch(url, '')
      
  def getBattlesCount(self):
    url = 'https://battlemap.deltatgame.com/get-battles-count'
    return self.fetch(url, '')
    
  def getHQs(self):
    url = 'https://battlemap.deltatgame.com/get-HQs'
    return self.fetch(url, '')
      
  def getBattles(self):
    url = 'https://battlemap.deltatgame.com/get-battles'
    return self.fetch(url, '')
      
  def getBattleDetails(self, battleID):
    url = 'https://battlemap.deltatgame.com/get-battle-details'
    payload = {}
    payload['battleID']=battleID
    return self.fetch(url, payload)

  def getOwnerDetails(self, baseID):
    url = 'https://battlemap.deltatgame.com/owner-details'
    payload = {}
    payload['id']=baseID
    return self.fetchRaw(url, payload)

  def getBaseProfile(self, baseID):
    url = 'https://battlemap.deltatgame.com/base-profile'
    payload = {}
    payload['id']=baseID
    return self.fetch(url, payload)
    
  def getBases(self, lat1, lat2, lng1, lng2, minLevel, maxLevel):
    url = 'https://battlemap.deltatgame.com/get-bases'
    payload = {}
    payload['bounds']={}
    payload['bounds']['latitude']=[]
    payload['bounds']['latitude'].append(lat1)
    payload['bounds']['latitude'].append(lat2)
    payload['bounds']['longitutde']=[]
    payload['bounds']['longitutde'].append(lng1)
    payload['bounds']['longitutde'].append(lng2)
    payload['minLevel']=minLevel
    payload['maxLevel']=maxLevel
    payload['minHealth']=0
    payload['maxHealth']=100
    payload['baseLastID']=0
    payload['faction']=0
    return self.fetch(url, payload)