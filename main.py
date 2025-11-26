import json
from math import floor
import discord
from discord.utils import get
import requests

with open("tokens.json", "r") as json_file:
    data = json.load(json_file)
    tokenRiot = data["Riot"]
    tokenBot = data["Discord"]
    accountIds = [data["toplaner"]["id"], data["jungler"]["id"], data["midlaner"]["id"], data["botlaner"]["id"], data["support"]["id"]]
    toplaner = data["toplaner"]["summonerName"]
    jungler = data["jungler"]["summonerName"]
    midlaner = data["midlaner"]["summonerName"]
    botlaner = data["botlaner"]["summonerName"]
    support = data["support"]["summonerName"]
    json_file.close()

bot = discord.Client()

headerLine = {'X-Riot-Token': tokenRiot}

@bot.event
async def on_message(message):
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
            toplaner: {
                "id": 0,
                "emoji": get(bot.emojis, name="Top"),
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
            jungler: {
                "id": 0,
                "emoji": get(bot.emojis, name="Jungle"),
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
            midlaner: {
                "id": 0,
                "emoji": get(bot.emojis, name="Mid"),
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
            botlaner: {
                "id": 0,
                "emoji": get(bot.emojis, name="Bot"),
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
            support: {
                "id": 0,
                "emoji": get(bot.emojis, name="Supp"),
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
        url += accountIds[3] + "?endIndex=" + str(offset + int(nbreGames))

        req = requests.get(url, headers=headerLine)

        if req.status_code != 200:
            await message.channel.send('Went wrong! Code:' + str(req.status_code))
        else:
            gameIds = []
            for matches in req.json()["matches"]:
                gameIds.append(matches["gameId"])

            if offset != 0:
                del gameIds[:offset]

            # Insert games ID in case of custome games
            # gameIds = [4755554519, 4755704576, 4755555267]

            for i in gameIds:
                url = 'https://euw1.api.riotgames.com/lol/match/v4/matches/' + str(i)
                req = requests.get(url, headers=headerLine)

                if req.status_code != 200:
                    await message.channel.send('Went wrong [2]! Code:' + str(req.status_code))
                else:
                    gameDuration = req.json()["gameDuration"]
                    avgGame += gameDuration

                    for participant in req.json()["participantIdentities"]:
                        if participant["player"]["summonerName"] in participants.keys():
                            participants[participant["player"]["summonerName"]]["id"] = participant["participantId"]

                    # Uncomment in case of custom games
                    # if i == 4755704576:
                    #    participants[toplaner]["id"] = 1
                    #    participants[jungler]["id"] = 2
                    #    participants[midlaner]["id"] = 3
                    #    participants[botlaner]["id"] = 4
                    #    participants[support]["id"] = 5
                    # else:
                    #    participants[toplaner]["id"] = 6
                    #    participants[jungler]["id"] = 7
                    #    participants[midlaner]["id"] = 8
                    #    participants[botlaner]["id"] = 9
                    #    participants[support]["id"] = 10

                    if participants[botlaner]['id'] < 6:
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
                        player = next((item for item in list(participants.values()) if
                                       item["id"] == participant["participantId"]), False)

                        if player:
                            player["kills"] += participant["stats"]["kills"]
                            totalKillsEquipe += participant["stats"]["kills"]
                            player["deaths"] += participant["stats"]["deaths"]
                            player["assists"] += participant["stats"]["assists"]
                            player["gold"] += participant["stats"]["goldEarned"]
                            player["penta"] += participant["stats"]["pentaKills"]
                            player["cs"] += (participant["stats"]["totalMinionsKilled"] + participant["stats"][
                                "neutralMinionsKilled"]) / (gameDuration / 60)
                            player["vs"] += participant["stats"]["visionScore"]
                            player["wardPlaced"] += participant["stats"]["wardsPlaced"]
                            player["wardDestroyed"] += participant["stats"]["wardsKilled"]
                            player["pink"] += participant["stats"]["visionWardsBoughtInGame"]
                            player["dmgChamp"] += participant["stats"]["totalDamageDealtToChampions"]

                            if participants[support]["id"] == participant["participantId"]:
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
            footer = support + " a heal " + str(
                participants[support]["totalHeal"]) + " points de dégats sur les "
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
                kda = "%g" % (round((participants[participant]['kills'] + participants[participant]['assists']) /
                                    participants[participant]['deaths'], 1)) if participants[participant][
                                                                                    'deaths'] != 0 else "Perfect"
                msgStats += "    " + f"{participants[participant]['emoji']}  " + kda + " ("
                msgStats += "%g" % (round(participants[participant]['kills'] / int(nbreGames))) + "/"
                msgStats += "%g" % (round(participants[participant]['deaths'] / int(nbreGames))) + "/"
                msgStats += "%g" % (round(participants[participant]['assists'] / int(nbreGames))) + ")\r\n"
            msgStats += "\r\nKP :\r\n"
            for participant in participants:
                totalParticipation = participants[participant]['kills'] + participants[participant]['assists']
                msgStats += "    " + f"{participants[participant]['emoji']}  " + "{:.0%}".format(
                    totalParticipation / totalKillsEquipe) + "\r\n"
            msgStats += "\r\nDégâts :\r\n"
            for participant in participants:
                damageDealt = "%g" % (round(participants[participant]['dmgChamp'] / int(nbreGames)))
                msgStats += "    " + f"{participants[participant]['emoji']}  " + f'{int(damageDealt):,}'.replace(',',
                                                                                                                 ' ') + "\r\n"
            msgStats += "\r\nPentakills :\r\n"
            for participant in participants:
                msgStats += "    " + f"{participants[participant]['emoji']}  " + "%g" % (
                    round(participants[participant]['penta'] / int(nbreGames))) + "\r\n"
            msgMoreStats = "\r\nCS/mn :\r\n"
            for participant in participants:
                msgMoreStats += "    " + f"{participants[participant]['emoji']}  " + "%g" % (
                    round(participants[participant]['cs'] / int(nbreGames), 1)) + "\r\n"
            msgMoreStats += "\r\nGold :\r\n"
            for participant in participants:
                gold = "%g" % (round(participants[participant]['gold'] / int(nbreGames)))
                msgMoreStats += "    " + f"{participants[participant]['emoji']}  " + f'{int(gold):,}'.replace(',',
                                                                                                              ' ') + "\r\n"
            msgMoreStats += "\r\nVision Score ~ Pink achetés :\r\n"
            for participant in participants:
                msgMoreStats += "    " + f"{participants[participant]['emoji']}  " + "%g" % (
                    round(participants[participant]['vs'] / int(nbreGames))) + " ~ "
                msgMoreStats += "%g" % (round(participants[participant]['pink'] / int(nbreGames), 1)) + "\r\n"
            msgMoreStats += "\r\nWards détruites ~ Wards placés :\r\n"
            for participant in participants:
                msgMoreStats += "    " + f"{participants[participant]['emoji']}  " + "%g" % (
                    round(participants[participant]['wardDestroyed'] / int(nbreGames))) + " ~ "
                msgMoreStats += "%g" % (round(participants[participant]['wardPlaced'] / int(nbreGames))) + "\r\n"

            embed = discord.Embed(title=titre, color=0x23e7e3)
            embed.add_field(name="RÉSULTAT & OBJECTIFS", value=msgResultatObjectifs, inline=True)
            embed.add_field(name="STATS", value=msgStats, inline=True)
            embed.add_field(name="TOUJOURS PLUS DE STATS", value=msgMoreStats, inline=True)
            embed.set_footer(text=footer)

            await message.channel.send(embed=embed)

    elif message.content.startswith('!champs'):
        values = message.content.split()
        queue = values[1]

        arr = []

        for i in range(0, 5):
            url = 'https://euw1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + accountIds[
                i] + '?queue=' + str(queue)
            req = requests.get(url, headers=headerLine)

            if req.status_code != 200:
                await message.channel.send('Went wrong! Code:' + str(req.status_code) + ". Message: " + req.json()["status"]["message"])
            else:
                arr.append(set())

                for matches in req.json()["matches"]:
                    arr[i].add(matches["gameId"])

        gameIds = arr[0].intersection(arr[1], arr[2], arr[3], arr[4])

        if len(gameIds) > 95:
            gameIds = gameIds[:94]

        data = {
            toplaner: {},
            jungler: {},
            midlaner: {},
            botlaner: {},
            support: {}
        }

        for i in gameIds:
            url = 'https://euw1.api.riotgames.com/lol/match/v4/matches/' + str(i)
            req = requests.get(url, headers=headerLine)

            if req.status_code != 200:
                await message.channel.send('Went wrong [2]! Code:' + str(req.status_code))
            else:
                participants = {
                    toplaner: {"playerId": 0, "champId": 0},
                    jungler: {"playerId": 0, "champId": 0},
                    midlaner: {"playerId": 0, "champId": 0},
                    botlaner: {"playerId": 0, "champId": 0},
                    support: {"playerId": 0, "champId": 0}}

                win = False

                for participant in req.json()["participantIdentities"]:
                    if participant["player"]["summonerName"] in participants.keys():
                        participants[participant["player"]["summonerName"]]["playerId"] = participant["participantId"]

                if participants[botlaner]['playerId'] < 6:
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

                for participant in participants:
                    if participants[participant]["champId"] in data[participant].keys():
                        data[participant][participants[participant]["champId"]]["nbreWins"] += 1 if win else 0
                        data[participant][participants[participant]["champId"]]["nbreGames"] += 1
                    else:
                        newChampEntry = {participants[participant]["champId"]: {
                            "nbreWins": 1 if win else 0,
                            "nbreGames": 1
                        }}
                        data[participant].update(newChampEntry)

        embed = discord.Embed(title="Queue : " + queue + " (440: Flex, 450: ARAM, 700: Clash)", color=0x1feadd)

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
            for i in range(10 if len(arr) >= 10 else len(arr)):
                if arr[i][0] < 10:
                    emojiIcon = get(bot.emojis, name=str(arr[i][0]) + "_")
                else:
                    emojiIcon = get(bot.emojis, name=str(arr[i][0]))

                if emojiIcon is not None:
                    msg += f"{emojiIcon}" + " " + "{:.0%}".format(arr[i][1] / arr[i][2]) + " (" + str(
                        arr[i][2]) + ")\r\n"
                else:
                    msg += str(arr[i][0]) + " " + "{:.0%}".format(arr[i][1] / arr[i][2]) + " (" + str(
                        arr[i][2]) + ")\r\n"

            if msg:
                embed.add_field(name=participant, value=msg, inline=True)

        nbreWinsTotal = 0
        nbreGamesTotal = 0

        for key in data[botlaner].keys():
            nbreWinsTotal += data[botlaner][key]["nbreWins"]
            nbreGamesTotal += data[botlaner][key]["nbreGames"]

        wrGeneral = "{:.0%}".format(nbreWinsTotal / nbreGamesTotal)

        embed.add_field(name="Winrate général:", value=wrGeneral + " (" + str(nbreGamesTotal) + ")", inline=True)
        await message.channel.send(embed=embed)

    elif message.content.startswith('!team'):
        values = message.content.split()

        if len(values) == 6:
            with open("tokens.json", "r") as json_file:
                data = json.load(json_file)

            for i in range(1, 6):
                url = 'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + values[i]
                req = requests.get(url, headers=headerLine)

                if req.status_code != 200:
                    await message.channel.send('Went wrong! Code:' + str(req.status_code))
                else:
                    if i == 1:
                        data["toplaner"]["id"] = req.json()["accountId"]
                        data["toplaner"]["summonerName"] = req.json()["name"]
                    elif i == 2:
                        data["jungler"]["id"] = req.json()["accountId"]
                        data["jungler"]["summonerName"] = req.json()["name"]
                    elif i == 3:
                        data["midlaner"]["id"] = req.json()["accountId"]
                        data["midlaner"]["summonerName"] = req.json()["name"]
                    elif i == 4:
                        data["botlaner"]["id"] = req.json()["accountId"]
                        data["botlaner"]["summonerName"] = req.json()["name"]
                    else:
                        data["support"]["id"] = req.json()["accountId"]
                        data["support"]["summonerName"] = req.json()["name"]

            with open("tokens.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
                json_file.close()

            await message.channel.send('Fait !')

        elif "-base" in message.content:
            with open("tokens.json", "r") as json_file:
                data = json.load(json_file)

            data["toplaner"]["id"] = "kLunZ5XPnnnnqqlyaWESFtGu8MxsWNxydEyHG4BrC1hi5VI"
            data["toplaner"]["summonerName"] = "SAlmidanach"
            data["jungler"]["id"] = "bpuluOERRbgLG4HRq82PHasOMq9wZhXd0aspy00Vl6VUdEI"
            data["jungler"]["summonerName"] = "Wolfang"
            data["midlaner"]["id"] = "USU5qVMDUK-E_bopa5qvJX56WWa7Z76TFC_O2APwriLp8ko"
            data["midlaner"]["summonerName"] = "Quantums Wreck"
            data["botlaner"]["id"] = "NqDa9eKyuzPP2i7ttqjLji-jAnQ4STI-rAFWv2Li3-qrf4Y"
            data["botlaner"]["summonerName"] = "Krantt"
            data["support"]["id"] = "RTjnyoR3D3Vvy46KqspGJCC6iqGl4x58maGtjDd580RsmA"
            data["support"]["summonerName"] = "Supreme CPT"

            with open("tokens.json", "w") as json_file:
                json.dump(data, json_file, indent=4)
                json_file.close()

            await message.channel.send('Fait !')

        else:
            await message.channel.send('Invalid command')
    return

bot.run(tokenBot)
