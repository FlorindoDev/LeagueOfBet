import discord,json,pymongo
from riotwatcher import ApiError, LolWatcher
from discord.ext import commands , tasks
from datetime import *
import LeagueOfLegend, asyncio


class bolletta(commands.Cog):

    def __init__(self, client,Richiesto):
        
            
        self.client = client 
        self.Richiesto = Richiesto
        self.watcher = LolWatcher(Richiesto["API_RIOT"]) #assegnazione api alla metodo Lolwatcher = Riot_API
        client_DB = pymongo.MongoClient(self.Richiesto["SERVER_LINK"]) 
        self.db = client_DB["Bot_bollete"] #seleziona il file "file_json"
        self.latest = self.watcher.data_dragon.versions_for_region(self.Richiesto["REGION_RIOT"])['n']['champion']
        self.static_champ_list = self.watcher.data_dragon.champions(self.latest, False, 'it_IT')
    

    @commands.command()
    async def live(self, ctx, *,Summoner_Name="_"):
        error = LeagueOfLegend.control(Summoner_Name,self.watcher,self.Richiesto["REGION_RIOT"]) #richiama la funzione control , se non ci sara nessun errore restituira None
        if error != None:
            await ctx.send(error)
            return
        Error= False
        
        
        try:
            id_summoner = self.watcher.summoner.by_name(self.Richiesto["REGION_RIOT"], Summoner_Name)
            game_live = self.watcher.spectator.by_summoner(self.Richiesto["REGION_RIOT"], id_summoner["id"])
            game_mode = LeagueOfLegend.cacolo_modalita(game_live["gameQueueConfigId"])
            game_time = LeagueOfLegend.unix_convert(game_live["gameStartTime"])
            ranks = LeagueOfLegend.rank_gamelive(game_live,self.watcher,self.Richiesto["REGION_RIOT"]) 
            champion_summoner = LeagueOfLegend.all_summoners_champions(self.static_champ_list,game_live)

        except ApiError as err:
            if err.response.status_code == 503:
                embed = discord.Embed(title=f"Servizi lol offline")
                await ctx.send(embed=embed)
                return
            if err.response.status_code == 404:
                Error = True


        if Error == True:
            outgame = discord.utils.get(self.client.emojis, name="loss")
            embed = discord.Embed(title=f"{outgame} {Summoner_Name} non è in partita ", description=f"")
            #embed.set_footer(text="᲼",icon_url=LeagueOfLegend.summoner_icon(Summoner_Name,self.watcher,self.Richiesto["REGION_RIOT"],self.latest))
            #embed.set_author(name=f"{Summoner_Name}", icon_url=f'{LeagueOfLegend.summoner_icon(Summoner_Name,self.watcher,self.Richiesto["REGION_RIOT"],self.latest)}')
            

        else:
            team = ""
            team2 = ""
            ingame = discord.utils.get(self.client.emojis, name="Win")
            embed = discord.Embed(title=f"{ingame} {Summoner_Name} è in partita ", description=f"**{game_mode}**")
            #embed.set_author(name=f"{Summoner_Name}", icon_url=f'{LeagueOfLegend.summoner_icon(Summoner_Name,self.watcher,self.Richiesto["REGION_RIOT"],self.latest)}')
            embed.set_footer(text=f"Game iniziato " + game_time,icon_url=LeagueOfLegend.summoner_icon(Summoner_Name,self.watcher,self.Richiesto["REGION_RIOT"],self.latest))
            for summoner in ranks:

                if ranks[summoner]["teamId"] == 100:
                    if ranks[summoner]['Rank'] != False:
                        emoji_rank = discord.utils.get(self.client.emojis, name=f"{(ranks[summoner]['Rank'].split(' '))[0]}")
                        team += f"{emoji_rank} `{summoner}" + f" - {ranks[summoner]['Rank']}" + f" - {champion_summoner[summoner]['champ']}` \n"
                    else:
                        emoji_rank = discord.utils.get(self.client.emojis, name="Unrank")
                        team += f"{emoji_rank} `{summoner}" + f" - {champion_summoner[summoner]['champ']}` \n"
                else:
                    if ranks[summoner]['Rank'] != False:
                        emoji_rank = discord.utils.get(self.client.emojis, name=f"{(ranks[summoner]['Rank'].split(' '))[0]}")
                        team2 += f"{emoji_rank} `{summoner}" + f" - {ranks[summoner]['Rank']}" + f" - {champion_summoner[summoner]['champ']}` \n"
                    else:
                        emoji_rank = discord.utils.get(self.client.emojis, name="Unrank")
                        team2 += f"{emoji_rank} `{summoner}" + f" - {champion_summoner[summoner]['champ']}` \n"
        
            embed.add_field(name="Team 1:", value=team, inline= False)
            embed.add_field(name="Team 2:", value=team2, inline= False)
            embed.set_thumbnail(url=LeagueOfLegend.summoner_icon(Summoner_Name,self.watcher,self.Richiesto["REGION_RIOT"],self.latest))
        await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        id = member.id
        money =  2500
        collection = self.db["user"]
        user = collection.find_one({"_id": id})
        if user == None:
            collection.insert_one({"_id": id, "soldi": money, "daily":str(datetime.now()),"rank":"Iron", "tier":4, "exp_attuale": 0, "exp_rankup": 500})

            
    @commands.command()
    async def registrazione(self, ctx):
        id = ctx.author.id
        money =  2500
        collection = self.db["user"]
        user = collection.find_one({"_id": id})
        if user == None:
            collection.insert_one({"_id": id, "soldi": money, "daily":str(datetime.now()),"rank":"Iron", "tier":4, "exp_attuale": 0, "exp_rankup": 500})
            embed = discord.Embed(title="✅ " +  " Tutto è andato a buon fine", url="", description=f"Sei stato registrato con questo nome utente `{ctx.author.name}`. \n", color=0x000000)
            await ctx.send(embed = embed)

        else:
            outgame = discord.utils.get(self.client.emojis, name="commands")
            embed = discord.Embed(title=f"{outgame} Registrazione",description="sei gia registrato")
            await ctx.send(embed=embed)


    @commands.command()
    async def profile(self,ctx):
        name = ctx.author.name
        img = ctx.author.display_avatar
        collection = self.db["user"]
        user = collection.find_one({"_id": ctx.author.id})
        if user != None:
            collection_bol = self.db["bolletta"]
            collection_exp = self.db["exp_rank"]
            
            for bol in collection_bol.find({"id_user": ctx.author.id,"exp_ritirata": False}):
                all = {}
                rank = {}
                user["exp_attuale"] += bol["exp_bol"]
                collection_bol.find_one_and_update({"_id": bol["_id"]},{"$set": {"exp_ritirata": True}})

            while user["exp_attuale"] > user["exp_rankup"] and user["rank"] != "Challenger":
                user["exp_attuale"] -= user["exp_rankup"]
                user["exp_rankup"] *= 2
                user["tier"] -= 1
                if user["tier"] <= 0 and user["rank"] != "Challenger":
                    rank = collection_exp.find_one({"_id": user["rank"]})
                    all = collection_exp.find()
                    collection.find_one_and_update({"_id": ctx.author.id},{"$set": {"exp_attuale":user["exp_attuale"],"rank": all[int(rank["num"])+1]["_id"], "tier": 4, "exp_rankup": user["exp_rankup"]}})
                else:
                    collection.find_one_and_update({"_id": ctx.author.id},{"$set": {"exp_attuale":user["exp_attuale"],"tier":user["tier"], "exp_rankup": user["exp_rankup"]}})
                       
            collection.find_one_and_update({"_id": ctx.author.id},{"$set": {"exp_attuale":user["exp_attuale"]}})            

            user = collection.find_one({"_id": ctx.author.id})
            euro = discord.utils.get(self.client.emojis, name="euro")
            black = discord.utils.get(self.client.emojis, name="black")
            emoji_rank = discord.utils.get(self.client.emojis, name=f"{user['rank'].upper()}")
            embed = discord.Embed(title=f"Profilo di {name}:", description="{} Hai `{:,}`".format(euro,user['soldi']))
            embed.add_field(name="Livello Ludopatia:", value=f"{black} `{user['rank']} {user['tier']}` {emoji_rank}",inline=False)
            embed.add_field(name="Exp attuale:", value=f"{black} `{user['exp_attuale']} Exp`",inline=False)
            embed.add_field(name="RankUp Exp:", value=f"{black} `{user['exp_rankup']} Exp`",inline=False)
            embed.add_field(name="Prossimo daily:", value=f"{black} `{user['daily']}`",inline=False)
            embed.set_thumbnail(url=img)
            await ctx.send(embed=embed)
        else:
            outgame = discord.utils.get(self.client.emojis, name="commands")
            embed = discord.Embed(title=f"{outgame} Registrazione",description="Non sei gia registrato")
            await ctx.send(embed=embed)
        

    @commands.command()
    async def daily(self, ctx):
        collection = self.db["user"]
        user = collection.find_one({"_id": ctx.author.id})
        if user != None:
            datetime_object = datetime.strptime(user["daily"], '%Y-%m-%d %H:%M:%S.%f')  
            date = datetime_object.replace(microsecond=0) - datetime.now().replace(microsecond=0)
            if datetime_object < datetime.now():
                user["soldi"] += 50
                collection.find_one_and_update({"_id": ctx.author.id},{"$set": {"soldi": int(user["soldi"]), "daily": str(datetime.now() + timedelta(days=1))}})

                euro = discord.utils.get(self.client.emojis, name="euro")
                embed = discord.Embed(title="✅  " +  f"{euro} +50", url="", description="{} Ora hai `{:,}`".format(euro,user["soldi"]), color=0x000000)
                embed.set_footer(text=f"User: {ctx.author.name}")
                await ctx.send(embed = embed)
            else:

                embed = discord.Embed(title="🚫  " +  f"Hai gia preso il daily", url="", description=f"Per il prossimo daily manca `{date}`", color=0x000000)
                embed.set_footer(text=f"User: {ctx.author.name}")
                await ctx.send(embed = embed)
                return
        else:
            outgame = discord.utils.get(self.client.emojis, name="commands")
            embed = discord.Embed(title=f"{outgame} Registrazione",description="Non sei registrato")
            await ctx.send(embed=embed)


    @commands.command()
    async def b(self, ctx, puntata=None,V_S= "_",*,Summoner_name= None):
            black = discord.utils.get(self.client.emojis, name="black")
            if puntata != None  and Summoner_name != None and V_S == "vittoria" or V_S == "sconfitta":
                  
                if puntata.isnumeric()==True:
                            
                    collection = self.db["user"]
                    soldi = collection.find_one({"_id": ctx.author.id})
                    if soldi != None:
                        error = LeagueOfLegend.control(Summoner_name,self.watcher,self.Richiesto["REGION_RIOT"])
                        if error != None:
                            await ctx.send(error)
                            return
                        try:
                            id_summoner = self.watcher.summoner.by_name(self.Richiesto["REGION_RIOT"], Summoner_name)
                            game_live = self.watcher.spectator.by_summoner(self.Richiesto["REGION_RIOT"], id_summoner["id"])
                            game_time = LeagueOfLegend.unix_convert(game_live["gameStartTime"]).split(" ")
                        except ApiError as err:
                                if err.response.status_code == 404:
                                    outgame = discord.utils.get(self.client.emojis, name="loss")
                                    embed = discord.Embed(title=f"{outgame} {Summoner_name} non è in partita ", description=f"")

                                    await ctx.send(embed = embed)
                                    return
                        if game_live["gameType"] != "CUSTOM_GAME":
                            if  game_time[0].isnumeric()== True:
                                if int(game_time[0]) > 20:
                                    loss = discord.utils.get(self.client.emojis, name="loss")
                                    embed = discord.Embed(title=f"{loss} Non puoi giocare la Bolletta su {Summoner_name}:", description="Non puoi fare la bolletta perchè il game ha superato i 20 minuti")
                                    await ctx.send(embed = embed)
                                    return

                            else:
                                await ctx.send("**Summoner in caricamento**")
                                return

                            
                            if int(puntata) <= soldi["soldi"] and int(puntata) > 0 :
                                if V_S.lower() == "vittoria" or V_S.lower() == "sconfitta":
                                    outgame = discord.utils.get(self.client.emojis, name="loss")
                                    if game_time[0] == "in":
                                        ingame = discord.utils.get(self.client.emojis, name="Win")
                                        embed = discord.Embed(title=f"{ingame} Bolletta giocata su {Summoner_name}:", description="Hai giocato `{:,}` per la `{}` nel minuto `{}` della partita".format(int(puntata),V_S,"0"))
                                        await ctx.send(embed = embed) 
                                    else:
                                        ingame = discord.utils.get(self.client.emojis, name="Win")
                                        embed = discord.Embed(title=f"{ingame} Bolletta giocata su {Summoner_name}:", description="Hai giocato `{:,}` per la `{}` nel minuto `{}` della partita".format(int(puntata),V_S,game_time[0]))
                                        img = LeagueOfLegend.summoner_icon(Summoner_name,self.watcher,self.Richiesto["REGION_RIOT"],self.latest)
                                        embed.set_thumbnail(url=img)
                                        embed.set_footer(text=f"User: {ctx.author.name}")
                                        await ctx.send(embed = embed) 

                                    collection.find_one_and_update({"_id": ctx.author.id},{"$set": {"soldi": int(soldi["soldi"]) - int(puntata)}})
                                    collection = self.db["bolletta"]
                                    count = collection.find_one({"_id": "count"})
                                    collection.find_one_and_update({"_id": "count"},{"$set": {"val": count["val"]+1}})
                                    collection.insert_one({"_id": count["val"], "Summoner_Giocato": Summoner_name, "id_game":game_live["gameId"],"puntata": int(puntata),"Tipo_puntata": V_S,"Ritiro": False,"Giorno_scadenza": str(datetime.now() + timedelta(days=1)),"Tempo_puntata":game_time[0],"id_user": ctx.author.id,"gametype":game_live["gameQueueConfigId"]})
                                else:
                                    embed = discord.Embed(title="🚫 " +  " Errore essenze blu", url="", description="Non hai abbastanza essenze blu o la puntata e pari a 0 o inferiore \n `.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`", color=0x000000)
                                    emojis = discord.utils.get(self.client.emojis, name=f"black")
                                    embed.add_field(name="Consigli:", value=f"{emojis} Gioca di meno `.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`\n{emojis}Aspetta il daily `.daily`\n {emojis} Punta piu di 0 `.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`\n {emojis} Riccorda di puntare per la vittoria o sconfitta `.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`")
                                    await ctx.send(embed = embed)
                                    return
                                
                            else:
                                embed = discord.Embed(title="🚫 " +  " Errore essenze blu", url="", description="Non hai abbastanza essenze blu o la puntata e pari a 0 o inferiore \n `.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`", color=0x000000)
                                emojis = discord.utils.get(self.client.emojis, name=f"black")
                                embed.add_field(name="Consigli:", value=f"{emojis} Gioca di meno `.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`\n{emojis}Aspetta il daily `.daily`\n {emojis} Punta piu di 0 `.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`\n {emojis} Riccorda di puntare per la vittoria o sconfitta `.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`")
                                await ctx.send(embed = embed)
                                return
                        else:
                            outgame = discord.utils.get(self.client.emojis, name="loss")
                            embed = discord.Embed(title=f"{outgame} {Summoner_name} è in personalizzata ",description="")
                            await ctx.send(embed=embed)  

                    else:
                        outgame = discord.utils.get(self.client.emojis, name="commands")
                        embed = discord.Embed(title=f"{outgame} Registrazione",description="Non sei registrato")
                        await ctx.send(embed=embed)     
                else:
                    embed = discord.Embed(title="🚫 " +  " Errore commands", url="", description="comando sbagliato\n`.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`", color=0x000000)
                    embed.add_field(name="Consigli:", value=f"{black} Prova a scrivere bene il comando")
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="🚫 " +  " Errore commands", url="", description="comando sbagliato\n`.b [prezzo puntata] [Vittoria o Sconfitta] [nome]`", color=0x000000)
                embed.add_field(name="Consigli:", value=f"{black} Prova a scrivere bene il comando")
                await ctx.send(embed=embed)      
      

    @commands.command()
    async def claim(self, ctx):
        loss = discord.utils.get(self.client.emojis, name="loss")
        euro = discord.utils.get(self.client.emojis, name="euro")
        ingame = discord.utils.get(self.client.emojis, name="Win")
        arancione = discord.utils.get(self.client.emojis, name="arancione")
        black = discord.utils.get(self.client.emojis, name="black")

        collection_user = self.db["user"]
        user =  collection_user.find_one({"_id": ctx.author.id})
        if user != None:
            collection_rank = self.db["exp_rank"]
            collection = self.db["bolletta"]
            bollette_claim = collection.find_one({"Ritiro": False,"id_user": ctx.author.id})
            if bollette_claim != None:
                bollette_claim = collection.find({"Ritiro": False,"id_user": ctx.author.id})
                for bol in bollette_claim:
                    user =  collection_user.find_one({"_id": ctx.author.id})
                    soldi = user["soldi"]
                    finish,time = LeagueOfLegend.game_finish(self.watcher,self.Richiesto["REGION_RIOT"],f"EUW1_{bol['id_game']}")
                    datetime_object = datetime.strptime(bol["Giorno_scadenza"], '%Y-%m-%d %H:%M:%S.%f')  
                    if datetime_object > datetime.now():
                        if finish == True:
                            if int(time) > 5:
                                win = LeagueOfLegend.win(bol["Summoner_Giocato"],self.watcher,self.Richiesto["REGION_RIOT"],f"EUW1_{bol['id_game']}")
                                bet = bol["puntata"]
                                if win == True and bol["Tipo_puntata"] == "vittoria" or win == False and bol["Tipo_puntata"] == "sconfitta":
                                    if int(bol["gametype"]) == 440 or int(bol["gametype"]) == 420 or int(bol["gametype"]) == 700: 
                                        if int(bol["Tempo_puntata"]) <= 20 and 10 <= int(bol["Tempo_puntata"]):
                                            bol["puntata"] *= 1.4
                                            moltiplicatore = 1.4

                                        elif int(bol["Tempo_puntata"]) < 10 and int(bol["Tempo_puntata"]) >= 5:
                                            bol["puntata"] *= 1.8
                                            moltiplicatore = 1.8

                                        elif int(bol["Tempo_puntata"]) < 5:
                                            bol["puntata"] *= 2
                                            moltiplicatore = 2
                                        
                                    else:
                                        if int(bol["Tempo_puntata"]) <= 20 and 10 <= int(bol["Tempo_puntata"]):
                                            bol["puntata"] *= 1.2
                                            moltiplicatore = 1.2
                                        elif int(bol["Tempo_puntata"]) < 10  and int(bol["Tempo_puntata"]) >= 5:
                                            bol["puntata"] *= 1.3
                                            moltiplicatore = 1.3

                                        elif int(bol["Tempo_puntata"]) < 5:
                                            bol["puntata"] *= 1.4
                                            moltiplicatore = 1.4
                                    

                                    exp_x = collection_rank.find_one({"_id": user["rank"]})
                                    collection_user.find_one_and_update({"_id": ctx.author.id},{"$set": {"soldi": soldi + bol["puntata"]}})
                                    collection.find_one_and_update({"_id": bol["_id"]},{"$set": {"Ritiro": True,"vittoria_bolletta": True,"exp_ritirata": False,"exp_bol": bol["puntata"] * exp_x["exp"]}})
                                    embed = discord.Embed(title=f"{ingame} Hai vinto la bolletta", description="Hai vinto {} `{:,}`".format(euro,bol["puntata"]))
                                    embed.add_field(name=f"{black} Guadagno:", value=f"Moltiplicatore di `{moltiplicatore}x`\n", inline=False)
                                    embed.add_field(name=f"{black} Esperienza :", value=f"`{bol['puntata'] * exp_x['exp']} Exp`\n", inline=False)
                                    embed.add_field(name=f"{black} Scadenza:", value=f"`{bol['Giorno_scadenza']}`\n", inline=False)
                                    embed.add_field(name=f"{black} Bolletta:",value="Hai puntato `{:,}` per la `{}` di `{}` nel minuto `{}`\n".format(bet,bol["Tipo_puntata"],bol["Summoner_Giocato"],bol["Tempo_puntata"]), inline=False)
                                    embed.set_footer(text=f"User: {ctx.author.name}, ID_bolletta: {bol['_id']}")
                                    embed.set_thumbnail(url=ctx.author.display_avatar)
                                    await ctx.send(embed=embed)
                                    
                                else:
                                    collection.find_one_and_update({"_id": bol["_id"]},{"$set": {"Ritiro": True,"vittoria_bolletta": False}})
                                    embed = discord.Embed(title=f"{loss} Hai perso la bolletta", description="Hai perso {} `{:,}`".format(euro,bol["puntata"]))
                                    embed.add_field(name=f"{black} Guadagno:", value=f"Moltiplicatore di `0x`\n", inline=False)
                                    embed.add_field(name=f"{black} Scadenza:", value=f"`{bol['Giorno_scadenza']}`\n", inline=False)
                                    embed.add_field(name=f"{black} Bolletta:",value="Hai puntato `{:,}` per la `{}` di `{}` nel minuto `{}`\n".format(bet,bol["Tipo_puntata"],bol["Summoner_Giocato"],bol["Tempo_puntata"]), inline=False)
                                    embed.set_footer(text=f"User: {ctx.author.name}, ID_bolletta: {bol['_id']}")
                                    embed.set_thumbnail(url=ctx.author.display_avatar)
                                    await ctx.send(embed=embed)
                            else:
                                collection_user.find_one_and_update({"_id": ctx.author.id},{"$set": {"soldi": soldi + bol["puntata"]}})
                                collection.find_one_and_update({"_id": bol["_id"]},{"$set": {"Ritiro": True,"vittoria_bolletta": False}})
                                embed = discord.Embed(title=f"{arancione} Bolletta annullata perché una delle due squadre ha fatto ramake", description="")
                                embed.set_footer(text=f"User: {ctx.author.name}, ID_bolletta: {bol['_id']}")
                                await ctx.send(embed=embed)
                                
                        else:
                            embed = discord.Embed(title=f"{arancione} La partita di {bol['Summoner_Giocato']} è incorso", description="")
                            embed.set_footer(text=f"User: {ctx.author.name}, ID_bolletta: {bol['_id']}")
                            await ctx.send(embed=embed)
                    else:
                        
                        collection.find_one_and_update({"_id": bol["_id"]},{"$set": {"Ritiro": True,"vittoria_bolletta": False}})
                        embed = discord.Embed(title=f"{loss} Bolletta scaduta", description=f"bolletta scaduta nel `{bol['Giorno_scadenza']}`")
                        embed.set_footer(text=f"User: {ctx.author.name}, ID_bolletta: {bol['_id']}")
                        await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f"{loss} Non hai bollette",description="")
                await ctx.send(embed=embed)
        else:
            outgame = discord.utils.get(self.client.emojis, name="commands")
            embed = discord.Embed(title=f"{outgame} Registrazione",description="Non sei registrato")
            await ctx.send(embed=embed)


    @commands.command()
    async def classifica(self, ctx):
        collection = self.db["user"]
        pipe = [{"$group": {"_id": "$_id", "puntata_tot":{"$sum": "$soldi"}}}]
        user_rich = collection.aggregate(pipeline=pipe)
        classifica = {}
        i = 0
        for soldi_tot in user_rich:
            classifica[soldi_tot["_id"]] = soldi_tot["puntata_tot"]
        

        classifica = dict( sorted( classifica.items(), key = lambda item: item[1], reverse=True) )
        i = 0
        out = ""
        euro = discord.utils.get(self.client.emojis, name="euro")
        for user in classifica:
            username = await self.client.fetch_user(user)
            out += f"{i+1}. `{username.name}` con {euro}"  + "`{:,}` \n".format(classifica[user])
            i += 1
            if i == 5:
                break

        embed = discord.Embed(title=":trophy: Classifica")

        er = True

        if ctx.author.id in list(classifica.keys()):
            utente = list(classifica.keys()).index(ctx.author.id)
        else:
            er = None

            
        
        if utente > 5 and er != None:
            embed.add_field(name=":top: Persone piu ricche", value=out + f"{utente}. `{ctx.author.name}` con {euro}" + "`{:,}` \n".format(classifica[ctx.author.id]) , inline=False)
        else:
            embed.add_field(name=":top: Persone piu ricche", value=out, inline=False)
        

        collection = self.db["bolletta"]
        pipe = [{"$group": {"_id": "$id_user", "puntata_tot":{"$sum": "$puntata"}}}]
        user_rich = collection.aggregate(pipeline=pipe)
        classifica = {}
        i = 0
        for soldi_tot in user_rich:
            classifica[soldi_tot["_id"]] = soldi_tot["puntata_tot"]
        

        classifica = dict( sorted( classifica.items(), key = lambda item: item[1], reverse=True) )
        i = 0
        out = ""
        euro = discord.utils.get(self.client.emojis, name="euro")
        for user in classifica:
            username = await self.client.fetch_user(user)
            out +=  f"{i+1}. `{username.name}` con {euro}"  + "`{:,}` \n".format(classifica[user])
            i += 1
            if i == 5:
                break

        er = True
        if ctx.author.id in list(classifica.keys()):
            utente = list(classifica.keys()).index(ctx.author.id)
        else:
            er = None


        if utente > 5 and er != None:
            embed.add_field(name=":top: Perosne che hanno puntato di piu", value=out + f"{utente}. `{ctx.author.name}` con {euro}" + "`{:,}` \n".format(classifica[ctx.author.id]) , inline=False)
        else:
            embed.add_field(name=":top: Perosne che hanno puntato di piu", value=out, inline=False)
        await ctx.send(embed=embed)



        
        
        
        
        


    


       