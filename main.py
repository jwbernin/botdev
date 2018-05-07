
from __future__ import print_function
import discord
from discord.ext import commands
import pprint
from battlemap import Battlemap
from datetime import datetime
import calendar
import time

battleMap = Battlemap()

TOKEN = 'NDM2MjA3NzA0NTM3Njk0MjIz.DbkTug.EWyPpHxNnBAPP4k0eESwSs94mfo'
spreadsheet_url='https://docs.google.com/spreadsheets/d/1i-tw8TcZNHxNHzu3r_tqe1bT7yzimXWRc_JQQJBXS5c'
spreadsheet_key='1i-tw8TcZNHxNHzu3r_tqe1bT7yzimXWRc_JQQJBXS5c'

Client = discord.Client()
bot_prefix = "?"

battleCache = {}
completedCache = {}
lastCacheUpdate = 0

client = commands.Bot(command_prefix=bot_prefix)

def updateBattleCache():
  curTime = int(calendar.timegm(time.gmtime()))
  if ( curTime - lastCacheUpdate) < 300:
    return
  (active, completed) = getAllBattles()
  for battle in active:
    battleCache[battle['battleUniqueID']] = battle
  for battle in completed:
    completedCache[battle['battleUniqueID']] = battle
  lastCacheUpdate = curTime


@client.event
async def on_ready():
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')

@client.command(pass_context=True)
async def ping(ctx):
  print ("Ping command noticed")
  await client.say("Pong")

@client.command(pass_context=True)
async def getLiveBattles(ctx):
  battles = battleCache
  await client.say("I can display information on "+str(len(battles))+" battles. Those battles include:")
  for bID in battles.keys():
    await client.say("Battle ID "+bID)
  updateBattleCache()
  
@client.command(pass_context=True)
async def getBattleInfo(ctx):
  battleID = ctx.message.content[15:]
  if battleID not in battleCache.keys():
    await client.say("Couldn't get information for that battle!")
    return
  if battleID in completedCache.keys():
    await client.say("Battle completed - no information available")
    return
  battle = battleCache[battleID] 
  battleInfo = battle['mapInfo']
  ownBasePlayer = battle['nlPlayer']
  oppoBasePlayer = battle['oppoPlayer']
  now = datetime.utcnow()
  battleEnd = datetime.strptime(battleInfo['attack_on'], '%Y-%m-%d %H:%M:%S')
  timeToEnd = str(battleEnd-now)
  await client.say("Battle "+battleID+" is between base "+battleInfo['ownBaseDetails']['name']+" owned by "+ownBasePlayer+" and opponent base "+battleInfo['oppoBaseDetails']['name']+" owned by "+oppoBasePlayer)
  await client.say("It will resolve in "+timeToEnd.split('.')[0])
  await client.say("There are currently "+str(battle['reservedPower'])+" Battle Points at stake")
  await client.say("Nyoko cluster has "+str(battleInfo['ownClusterStrength'])+" strength, enemy cluster has "+str(battleInfo['oppoClusterStrength'])+" strength")

@client.command(pass_context=True)
async def getNextEndingBattle(ctx):
  battles = battleCache
  sortOn = "resolutionTime"
  decorated = [(dict_[sortOn], dict_) for dict_ in battles]
  decorated.sort()
  result = [dict_ for (key, dict_) in decorated]
  activeBattles = []
  for battle in result:
    if battle['finished'] == 0:
      activeBattles.append(battle)
  battle = activeBattles[0]
  await client.say("The next ending battle is "+battle['battleUniqueID'])
  battleInfo = battle['mapInfo']
  ownBasePlayer = battle['nlPlayer']
  oppoBasePlayer = battle['oppoPlayer']
  now = datetime.utcnow()
  battleEnd = datetime.strptime(battleInfo['attack_on'], '%Y-%m-%d %H:%M:%S')
  timeToEnd = str(battleEnd-now)
  await client.say("Battle "+battle['battleUniqueID']+" is between base "+battleInfo['ownBaseDetails']['name']+" owned by "+ownBasePlayer+" and opponent base "+battleInfo['oppoBaseDetails']['name']+" owned by "+oppoBasePlayer)
  await client.say("It will resolve in "+timeToEnd.split('.')[0])
  await client.say("There are currently "+str(battle['reservedPower'])+" BattlePoints at stake")
  await client.say("Nyoko cluster has "+str(battleInfo['ownClusterStrength'])+" strength, enemy cluster has "+str(battleInfo['oppoClusterStrength'])+" strength")

def getAllBattles():
  battles = battleMap.getBattles()
  activeBattles = []
  completedBattles = []
  for battle in battles:
    if battle['finished'] == 0:
      activeBattles.append(battle)
    else:
      completedBattles.append(battle)
  for battle in activeBattles:
    battleInfo = battleMap.getBattleDetails(battle['id'])
    ownBasePlayer = battleMap.getOwnerDetails(battle['ownBase'])
    oppoBasePlayer = battleMap.getOwnerDetails(battle['oppoBase'])
    now = datetime.utcnow()
    battleEnd = datetime.strptime(battleInfo['attack_on'], '%Y-%m-%d %H:%M:%S')
    timeToEnd = str(battleEnd-now)
    battle['nlPlayer'] = ownBasePlayer
    battle['oppoPlayer'] = oppoBasePlayer
    nlBase = battleMap.getBaseProfile(battleInfo['own_base'])
    oppoBase = battleMap.getBaseProfile(battleInfo['oppo_base'])
    battle['nlBaseName'] = nlBase['dt']['nm']
    battle['oppoBaseName'] = oppoBase['dt']['nm']
    battle['mapInfo'] = battleInfo
    battle['timeToEnd'] = timeToEnd
  return [activeBattles, completedBattles]
  
@client.command(pass_context=True)
async def getPlayerBattles(ctx):
  playerName = ctx.message.content[18:]
  battleSets = getAllBattles()
  for battle in battleSets[0]:
    if battle['nlPlayer'].upper() == playerName.upper():
      await client.say("NL player "+playerName+" is involved in battle "+battle['battleUniqueID'])
    if battle['oppoPlayer'].upper() == playerName.upper():
      await client.say("Opposition player "+playerName+" is involved in battle "+battle['battleUniqueID'])
  await client.say("Finished searching battles. Results (if any) above.")
      
@client.command(pass_context=True)
async def debug(ctx):
  print("Context args:")
  print (ctx.message.content)
  pprint.pprint(ctx.__dict__)
  
client.run(TOKEN)


