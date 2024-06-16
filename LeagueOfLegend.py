from __future__ import print_function
import requests
from riotwatcher import LolWatcher,ApiError
from discord.ext import commands 
from bson.objectid import ObjectId
from datetime import *
from bs4 import BeautifulSoup


Unix = 0


def control(summoner_name,watcher,region):
    #controlla gli eventuali errori e nel casso ci fossere ritorna un messaggio per ogni errore 
    try:
        response = watcher.summoner.by_name(region, summoner_name)
    except ApiError as err:
        if err.response.status_code == 429:
            return 'We should retry in {} seconds. :timer: '.format(err.headers['Retry-After'])
        elif err.response.status_code == 404:
            return 'Summoner **NON** trovato, riprovare. :x:'
        elif err.response.status_code == 400:
            return f'si è verificato un errore'
        else:
            raise
    return None


def unix():
    global Unix
    response = requests.get(f"https://www.unixtimestamp.com/") #tempo Unix in secondi
    src = response.content
    soup = BeautifulSoup(src, 'lxml')
    print(soup)
    Unix = soup.find("div", {"class": "value epoch"})
    Unix = int(Unix.get_text())
    
    


def unix_convert(time):
    time =(int(Unix)*1000) - time  #sotrare il unix tempo al tempo fornito da riot
 
    last_game = ((time)/1000)/60
    

    if int('%.0f' %  last_game) >= 60:
        last_game=last_game/60
        if int('%.0f' %  last_game) >= 24:
            last_game=last_game/24
            if int('%.0f' %  last_game) >= 7:
                last_game = last_game/7
                if int('%.0f' %  last_game) >= 4:
                    last_game =last_game/4
                    if '%.0f' %  last_game == "1" and  last_game != "684":
                        return '%.0f Mese fa' %  last_game
                    else:
                        return "in caricamento"

                else:
                    if '%.0f' %  last_game == "1":
                        return '%.0f Settimana fa' %  last_game
                    else:
                        return '%.0f Settimane fa' %  last_game
            else:
                if '%.0f' %  last_game == "1":
                    return '%.0f Giorno fa' %  last_game
                else:
                    return '%.0f Giorni fa' %  last_game
        else:
            if '%.0f' %  last_game == "1":
                return '%.0f ora fa' %  last_game
            else:
                return '%.0f ore fa' %  last_game
    else:
        if '%.0f' %  last_game == "1":
            return '%.0f minuto fa' %  last_game
        else:
            return '%.0f minuti fa' %  last_game


def Champion_found(Champion_key, champion_list):
    for champion_name in champion_list["data"]:
        if Champion_key == champion_list["data"][champion_name]["key"]:
            return champion_list["data"][champion_name]["name"]


def summoner_champion_game_live(summoner_name,champion_list,game_live):

    champion_summoner =  ""
    for summoner in game_live["participants"]:
        if summoner["summonerName"].lower() == summoner_name.lower():
            champion_summoner = Champion_found(f"{summoner['championId']}",champion_list)
            break
    
    return champion_summoner, False

    
def summoner_icon(summoner_name,watcher,region,latest):
    me = watcher.summoner.by_name(region, summoner_name)
    icona_profilo = me['profileIconId']
    icon_link = f'http://ddragon.leagueoflegends.com/cdn/{latest}/img/profileicon/{icona_profilo}.png'
    return icon_link


def win(summoner_name,watcher,region,game_id):
    game_info = watcher.match.by_id(region,game_id)
    for info in game_info["info"]["participants"]:
        if  (info["summonerName"].lower()).replace(" ","") == (summoner_name.lower()).replace(" ",""):
            return info["win"]


def game_finish(watcher,region,game_id):
    try:
        game = watcher.match.by_id(region,game_id)
        return True, game["info"]["gameDuration"]/60
    except ApiError as err:
        if err.response.status_code:
            return False, None
    

def cacolo_modalita(gamequeueID):
    response = requests.get(f"https://static.developer.riotgames.com/docs/lol/queues.json") #statistiche del game
    json_data = response.json()
    for i in json_data:
        if i["queueId"] == gamequeueID:
            return i["description"]


def rank_gamelive(game_live,watcher,region):
    #Nome_rank = ["IRON","BRONZE","SILVER","GOLD","PLATINUM","DIAMOND","MASTER","GRANDMASTER","CHALLENGER"]
    #Tier_rank = ["I","II","III","IV"]
    #rankss = []
    # i=0
    team_rank = {}
    for partecipats in game_live["participants"]:
        rank_piu_alto = {} 
        rank_piu_alto["Rank"] = False
        rank_piu_alto["teamId"] = partecipats["teamId"]
        team_rank[partecipats["summonerName"]] = rank_piu_alto
        summoner = watcher.league.by_summoner(region,partecipats["summonerId"]) 
        for ranks in summoner:
        
            if int(game_live["gameQueueConfigId"]) == 420: 
                if ranks["queueType"] == "RANKED_SOLO_5x5":
                    rank_piu_alto["Rank"] = ranks["tier"] + " " + ranks["rank"]
                    team_rank[partecipats["summonerName"]] = rank_piu_alto
                    break
                
            elif int(game_live["gameQueueConfigId"]) == 440: 
                if ranks["queueType"] == "RANKED_FLEX_SR":
                    rank_piu_alto["Rank"] = ranks["tier"] + " " + ranks["rank"]
                    team_rank[partecipats["summonerName"]] = rank_piu_alto
                    break
            else:
                if ranks["queueType"] == "RANKED_SOLO_5x5":
                    rank_piu_alto["Rank"] = ranks["tier"] + " " + ranks["rank"]
                    team_rank[partecipats["summonerName"]] = rank_piu_alto
                    break

    return team_rank         


def all_summoners_champions(champion_list,game_live):
    champion_summoner =  {}
    for summoner in game_live["participants"]:
        temp = {}
        temp["teamId"] = summoner["teamId"]
        temp["champ"] = Champion_found(f"{summoner['championId']}",champion_list)
        champion_summoner[summoner["summonerName"]] = temp

    return champion_summoner

                    
                       

                
            
    