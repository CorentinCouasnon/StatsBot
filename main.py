import json
from math import floor
import discord
from discord.utils import get
import requests

with open("tokens.txt", "r") as file:
    tokenRiot = file.readline().replace("\n", "")
    tokenBot = file.readline().replace("\n", "")
    accountId = file.readline().replace("\n", "")
    file.close()

bot = discord.Client()

@bot.event
async def on_message(message):
    emojiTop = get(message.guild.emojis, name="Top")
    emojiJungle = get(message.guild.emojis, name="Jungle")
    emojiMid = get(message.guild.emojis, name="Mid")
    emojiBot = get(message.guild.emojis, name="Bot")
    emojiSupp = get(message.guild.emojis, name="Supp")

    if message.author == bot.user:
        return

    if message.content.startswith('!stats'):
        values = message.content.split()
        offset = 0 if len(values) < 3 else int(values[2])
        nbreGames = values[1]

        teamId = 0
        winCounter = 0
        lossCounter = 0
        gameDuration = 0
        avgWin = 0
        avgLoss = 0
        avgGame = 0
        fb = 0
        fd = 0
        ft = 0
        towers = 0
        inhibs = 0
        drakes = 0
        nashs = 0
        heralds = 0
        drakesTotal = 0
        nashsTotal = 0
        heraldsTotal = 0
        totalKillsEquipe = 0

        participants = {
            "SAlmidanach": {
                "id": 0,
                "emoji": emojiTop,
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "gold": 0,
                "penta": 0,
                "cs": 0,
                "vs": 0,
                "wardPlaced": 0,
                "wardDestroyed": 0,
                "pink": 0,
                "dmgChamp": 0
            },
            "Wolfang": {
                "id": 0,
                "emoji": emojiJungle,
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "gold": 0,
                "penta": 0,
                "cs": 0,
                "vs": 0,
                "wardPlaced": 0,
                "wardDestroyed": 0,
                "pink": 0,
                "dmgChamp": 0
            },
            "Quantums Wreck": {
                "id": 0,
                "emoji": emojiMid,
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "gold": 0,
                "penta": 0,
                "cs": 0,
                "vs": 0,
                "wardPlaced": 0,
                "wardDestroyed": 0,
                "pink": 0,
                "dmgChamp": 0
            },
            "MrSuNGG": {
                "id": 0,
                "emoji": emojiBot,
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "gold": 0,
                "penta": 0,
                "cs": 0,
                "vs": 0,
                "wardPlaced": 0,
                "wardDestroyed": 0,
                "pink": 0,
                "dmgChamp": 0
            },
            "Supreme CPT": {
                "id": 0,
                "emoji": emojiSupp,
                "kills": 0,
                "deaths": 0,
                "assists": 0,
                "gold": 0,
                "penta": 0,
                "cs": 0,
                "vs": 0,
                "wardPlaced": 0,
                "wardDestroyed": 0,
                "pink": 0,
                "dmgChamp": 0,
                "totalHeal": 0
            }
        }

        url = "https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/"
        url += accountId + "?endIndex=" + str(offset + int(nbreGames))

        headerLine = {'X-Riot-Token': tokenRiot}

        req = requests.get(url, headers=headerLine)

        if req.status_code != 200:
            await message.channel.send('Went wrong! Code:' + str(req.status_code))
        else:
            gameIds = []
            for matches in req.json()["matches"]:
                gameIds.append(matches["gameId"])

            if offset != 0:
                del gameIds[:offset]

            for i in gameIds:
                url = 'https://euw1.api.riotgames.com/lol/match/v4/matches/' + str(i)
                req = requests.get(url, headers=headerLine)

                if req.status_code != 200:
                    await message.channel.send('Went wrong [2]! Code:' + str(req.status_code))
                else :
                    gameDuration = req.json()["gameDuration"]
                    avgGame += gameDuration

                    for participant in req.json()["participantIdentities"]:
                        if participant["player"]["summonerName"] in participants.keys():
                            participants[participant["player"]["summonerName"]]["id"] = participant["participantId"]

                    if participants['MrSuNGG']['id'] < 6:
                        teamId = 100
                    else:
                        teamId = 200

                    for team in req.json()["teams"]:
                        if team["teamId"] == teamId:
                            if team["win"] == "Win":
                                winCounter += 1
                                avgWin += gameDuration
                            else:
                                lossCounter += 1
                                avgLoss += gameDuration

                            fb += 1 if team["firstBlood"] else 0
                            ft += 1 if team["firstTower"] else 0
                            fd += 1 if team["firstDragon"] else 0
                            towers += team["towerKills"]
                            inhibs += team["inhibitorKills"]
                            drakes += team["dragonKills"]
                            nashs += team["baronKills"]
                            heralds += team["riftHeraldKills"]

                        drakesTotal += team["dragonKills"]
                        nashsTotal += team["baronKills"]
                        heraldsTotal += team["riftHeraldKills"]

                    for participant in req.json()["participants"]:
                        player = next((item for item in list(participants.values()) if item["id"] == participant["participantId"]), False)

                        if player:
                            player["kills"] += participant["stats"]["kills"]
                            totalKillsEquipe += participant["stats"]["kills"]
                            player["deaths"] += participant["stats"]["deaths"]
                            player["assists"] += participant["stats"]["assists"]
                            player["gold"] += participant["stats"]["goldEarned"]
                            player["penta"] += participant["stats"]["pentaKills"]
                            player["cs"] += (participant["stats"]["totalMinionsKilled"] + participant["stats"]["neutralMinionsKilled"]) / (gameDuration / 60)
                            player["vs"] += participant["stats"]["visionScore"]
                            player["wardPlaced"] += participant["stats"]["wardsPlaced"]
                            player["wardDestroyed"] += participant["stats"]["wardsKilled"]
                            player["pink"] += participant["stats"]["visionWardsBoughtInGame"]
                            player["dmgChamp"] += participant["stats"]["totalDamageDealtToChampions"]

                            if participants["Supreme CPT"]["id"] == participant["participantId"]:
                                player["totalHeal"] += participant["stats"]["totalHeal"]

            avgGame = round(avgGame / int(nbreGames))
            avgWin = round(avgWin / winCounter) if winCounter != 0 else 0
            avgLoss = round(avgLoss / lossCounter) if lossCounter != 0 else 0

            avgGame = str(floor(avgGame / 60)) + ":" + str(avgGame - (floor(avgGame / 60) * 60)).zfill(2)
            avgWin = str(floor(avgWin / 60)) + ":" + str(avgWin - (floor(avgWin / 60) * 60)).zfill(2)
            avgLoss = str(floor(avgLoss / 60)) + ":" + str(avgLoss - (floor(avgLoss / 60) * 60)).zfill(2)

            towers = "%g" % (round(towers / int(nbreGames), 1))
            inhibs = "%g" % (round(inhibs / int(nbreGames), 1))

            titre = "Statistiques d'une session de " + nbreGames + " partie(s) ! \r\n\r\n"
            footer = "Supreme CPT a heal " + str(participants["Supreme CPT"]["totalHeal"]) + " points de dégats sur les "
            footer += nbreGames + " parties !"

            msgResultatObjectifs = "Nombre de victoires : " + str(winCounter) + "\r\n"
            msgResultatObjectifs += "Nombre de défaites : " + str(lossCounter) + "\r\n\r\n"
            msgResultatObjectifs += "Temps de jeu : " + avgGame + "\r\n"
            msgResultatObjectifs += "Temps de jeu victoires : " + avgWin + "\r\n"
            msgResultatObjectifs += "Temps de jeu défaites : " + avgLoss + "\r\n\r\n"
            msgResultatObjectifs += "Tours détruites : " + towers + "\r\n"
            msgResultatObjectifs += "Inhib détruits : " + inhibs + "\r\n\r\n"
            msgResultatObjectifs += "Drake tués : " + "{:.0%}".format(drakes / drakesTotal)
            msgResultatObjectifs += " (" + str(drakes) + " sur " + str(drakesTotal) + ")\r\n"
            msgResultatObjectifs += "Nash tués : " + "{:.0%}".format(nashs / nashsTotal)
            msgResultatObjectifs += " (" + str(nashs) + " sur " + str(nashsTotal) + ")\r\n"
            msgResultatObjectifs += "Herald tués : " + "{:.0%}".format(heralds / heraldsTotal)
            msgResultatObjectifs += " (" + str(heralds) + " sur " + str(heraldsTotal) + ")\r\n\r\n"
            msgResultatObjectifs += "First blood : " + "{:.0%}".format(fb / int(nbreGames)) + "\r\n"
            msgResultatObjectifs += "First tower : " + "{:.0%}".format(ft / int(nbreGames)) + "\r\n"
            msgResultatObjectifs += "First drake : " + "{:.0%}".format(fd / int(nbreGames)) + "\r\n"

            msgStats = "\r\nKDA :\r\n"
            for participant in participants:
                msgStats += "    " + f"{participants[participant]['emoji']}  " + "%g" % (round((participants[participant]['kills'] + participants[participant]['assists']) / participants[participant]['deaths'], 1)) + "\r\n"
            msgStats += "\r\nK ~ D ~ A :\r\n"
            for participant in participants:
                msgStats += "    " + f"{participants[participant]['emoji']}  " + "%g" % (round(participants[participant]['kills'] / int(nbreGames), 1)) + " ~ "
                msgStats += "%g" % (round(participants[participant]['deaths'] / int(nbreGames), 1)) + " ~ "
                msgStats += "%g" % (round(participants[participant]['assists'] / int(nbreGames), 1)) + "\r\n"
            msgStats += "\r\nGold :\r\n"
            for participant in participants:
                gold = "%g" % (round(participants[participant]['gold'] / int(nbreGames)))
                msgStats += "    " + f"{participants[participant]['emoji']}  " + f'{int(gold):,}'.replace(',', ' ') + "\r\n"
            msgStats += "\r\nPentakills:\r\n"
            for participant in participants:
                msgStats += "    " + f"{participants[participant]['emoji']}  " + "%g" % (round(participants[participant]['penta'] / int(nbreGames))) + "\r\n"
            msgMoreStats = "\r\nCS/mn :\r\n"
            for participant in participants:
                msgMoreStats += "    " + f"{participants[participant]['emoji']}  " + "%g" % (round(participants[participant]['cs'] / int(nbreGames), 1)) + "\r\n"
            msgMoreStats += "\r\nVS ~ Kill ~ Placés ~ Pink :\r\n"
            for participant in participants:
                msgMoreStats += "    " + f"{participants[participant]['emoji']}  " + "%g" % (round(participants[participant]['vs'] / int(nbreGames))) + " ~ "
                msgMoreStats += "%g" % (round(participants[participant]['wardDestroyed'] / int(nbreGames))) + " ~ "
                msgMoreStats += "%g" % (round(participants[participant]['wardPlaced'] / int(nbreGames))) + " ~ "
                msgMoreStats += "%g" % (round(participants[participant]['pink'] / int(nbreGames), 1)) + "\r\n"
            msgMoreStats += "\r\nKill participation :\r\n"
            for participant in participants:
                totalParticipation = participants[participant]['kills'] + participants[participant]['assists']
                msgMoreStats += "    " + f"{participants[participant]['emoji']}  " + "{:.0%}".format(totalParticipation / totalKillsEquipe) + "\r\n"
            msgMoreStats += "\r\nDamage dealt aux champions :\r\n"
            for participant in participants:
                damageDealt = "%g" % (round(participants[participant]['dmgChamp'] / int(nbreGames)))
                msgMoreStats += "    " + f"{participants[participant]['emoji']}  " + f'{int(damageDealt):,}'.replace(',', ' ') + "\r\n"

            embed = discord.Embed(title=titre, color=0x23e7e3)
            embed.add_field(name="RÉSULTAT & OBJECTIFS", value=msgResultatObjectifs, inline=True)
            embed.add_field(name="STATS", value=msgStats, inline=True)
            embed.add_field(name="TOUJOURS PLUS DE STATS", value=msgMoreStats, inline=True)
            embed.set_footer(text=footer)

            await message.channel.send(embed=embed)

    elif message.content.startswith('!save'):
        values = message.content.split()
        nbreGames = values[1]
        offset = 0 if len(values) < 3 else int(values[2])

        url = 'https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountId + '?endIndex=' + str(int(nbreGames) + offset)

        headerLine = {'X-Riot-Token': tokenRiot}

        req = requests.get(url, headers=headerLine)

        if req.status_code != 200:
            await message.channel.send('Went wrong! Code:' + str(req.status_code))
        else:
            data = {}

            with open('data.json') as json_file:
                data = json.load(json_file)

            with open('data_save.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)

            gameIds = []
            for matches in req.json()["matches"]:
                gameIds.append(matches["gameId"])

            if offset != 0:
                del gameIds[:offset]

            for i in gameIds:
                url = 'https://euw1.api.riotgames.com/lol/match/v4/matches/' + str(i)
                req = requests.get(url, headers=headerLine)

                if req.status_code != 200:
                    await message.channel.send('Went wrong [2]! Code:' + str(req.status_code))
                else:
                    participants = {
                        "SAlmidanach": {"playerId": 0, "champId": 0},
                        "Wolfang": {"playerId": 0, "champId": 0},
                        "Quantums Wreck": {"playerId": 0, "champId": 0},
                        "MrSuNGG": {"playerId": 0, "champId": 0},
                        "Supreme CPT": {"playerId": 0, "champId": 0}}

                    win = False

                    for participant in req.json()["participantIdentities"]:
                        if participant["player"]["summonerName"] in participants.keys():
                            participants[participant["player"]["summonerName"]]["playerId"] = participant["participantId"]

                    if participants['MrSuNGG']['playerId'] < 6:
                        teamId = 100
                    else:
                        teamId = 200

                    for team in req.json()["teams"]:
                        if team["teamId"] == teamId:
                            win = True if team["win"] == "Win" else False

                    for participant in req.json()["participants"]:
                        player = next((item for item in list(participants.values()) if
                                       item["playerId"] == participant["participantId"]), False)

                        if player:
                            player["champId"] = participant["championId"]

                    with open('data.json') as json_file:
                        data = json.load(json_file)

                        for participant in participants:
                            if str(participants[participant]["champId"]) in data[participant].keys():
                                data[participant][str(participants[participant]["champId"])]["nbreWins"] += 1 if win else 0
                                data[participant][str(participants[participant]["champId"])]["nbreGames"] += 1
                            else:
                                newChampEntry = {participants[participant]["champId"]: {
                                    "nbreWins": 1 if win else 0,
                                    "nbreGames": 1
                                }}
                                data[participant].update(newChampEntry)

                    with open('data.json', 'w') as json_file:
                        json.dump(data, json_file, indent=4)

            embed = discord.Embed(title="Sauvegarde effectué !", color=0x1feadd)
            await message.channel.send(embed=embed)

    elif message.content.startswith('!champs'):
        with open('data.json') as json_file:
            data = json.load(json_file)

            if "-wr" in message.content:
                embed = discord.Embed(title="Winrate ! (minimum 5 parties jouées)", color=0x1feadd)
            else:
                embed = discord.Embed(title="Winrate - Trier par nombre de parties jouées !", color=0x1feadd)

            for participant in data:
                arr = []
                for key in data[participant]:
                    arr.append([key, data[participant][key]["nbreWins"], data[participant][key]["nbreGames"]])

                if "-wr" in message.content:
                    arr = sorted(arr, key=lambda x: x[2], reverse=True)
                    arr = [i for i in arr if i[2] >= 5]
                    arr = sorted(arr, key=lambda x: x[1] / x[2], reverse=True)
                else:
                    arr = sorted(arr, key=lambda x: x[1], reverse=True)
                    arr = sorted(arr, key=lambda x: x[2], reverse=True)

                msg = ""
                for i in range(5 if len(arr) >= 5 else len(arr)):
                    if len(arr[i][0]) < 2:
                        emojiIcon = get(message.guild.emojis, name=str(arr[i][0]) + "_")
                    else:
                        emojiIcon = get(message.guild.emojis, name=str(arr[i][0]))

                    if emojiIcon is not None:
                        msg += f"{emojiIcon}" + " " + "{:.0%}".format(arr[i][1] / arr[i][2]) + " (" + str(arr[i][2]) + ")\r\n"
                    else:
                        msg += str(arr[i][0]) + " " + "{:.0%}".format(arr[i][1] / arr[i][2]) + " (" + str(arr[i][2]) + ")\r\n"

                if msg:
                    embed.add_field(name=participant, value=msg, inline=True)

        embed.add_field(name="GG", value="WP", inline=True)
        await message.channel.send(embed=embed)

    return

bot.run(tokenBot)
