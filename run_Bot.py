#===== description =====#
"""
DiscordJinroGame
Copyright (c) 2018 brave99
This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php


This script is a discord bot that can be a GM of OneNightJinro game.
Required libraly is only "discord.py"
Have fun with your BOT!!
English version is coming soon...
"""
#===== modules =====#
import discord
from time import sleep
from threading import Thread, Event
from queue import Queue
import configparser
import random

#===== global =====#
config = configparser.SafeConfigParser()
config.read('option.ini', encoding = 'utf8')
client = discord.Client()
GAME = discord.Game(name = "OneNightJinro")
CHANNEL = None#discord.channel(id=config["BOT"]["CHANNEL"])
STARTED = False
STATEMENT = "hoge"
send = Queue()
receive = Queue()
#receive for discord to game, send for game to discord

#===== gameplay =====#
players = []

#===== script =====#

#===== bot =====#
@client.event
async def on_ready():
    global CHANNEL
    CHANNEL = client.get_channel(config["BOT"]["CHANNEL"])
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(CHANNEL)
    print('------')
    await client.send_message(CHANNEL, 'ブンブンハローDISCORD')
    await client.send_message(CHANNEL, '"/start" でゲームを開始します。\n"/restart"で再起動、"/shutdown"で終了します。')

@client.event
async def on_message(message):
    global STARTED
    global CHANNEL
    global players
    if message.content.startswith("/restart"):
        await client.send_message(message.channel, "I'll be back...")
        client.change_presence(game = None)
        client.logout()
        client.close()
        sleep(3)
        client.run(config["BOT"]["TOKEN"])
        STARTED = False
        players = []

    elif message.content.startswith("/shutdown"):
        if client.user != message.author:
            await client.send_message(message.channel, "Bye!!")
            client.close()
            client.logout()
            exit(0)

    if not STARTED:
        if message.content.startswith("/start"):
            if client.user != message.author:
                await client.send_message(CHANNEL, "ワンナイト人狼ゲームを始めます。")
                await client.change_presence(game = GAME)
                await client.send_message(CHANNEL, '参加したい人は"/join"と入力。')
                await client.send_message(CHANNEL, '全員の入力が終わったら"/go"と入力。')
                STARTED = True

    elif STARTED:
        if message.content.startswith("/join"):
            if client.user != message.author:
                p = []
                for player in players:
                    p.append(player.discord)
                if message.author in p:
                    await client.send_message(CHANNEL, "{} はもう登録済みです。".format(message.author.name))
                else:
                    hoge = Player(message.author)
                    players.append(hoge)
                    await client.send_message(CHANNEL, "{} を登録しました。".format(send.get()))

        elif message.content.startswith("/go"):
            if len(players)<3:
                await client.send_message(CHANNEL, "3人以上いないとプレイできません。再度/startからやりなおしてください。")
            else:
                await client.send_message(CHANNEL, "全員の準備が完了しました。夜のアクションに入ります。\nアクションはDMで行います。")
                deck = makeDeck(len(players))
                playable, remaining = decideRole(deck)
                for x, player in enumerate(players):
                    player.role = playable[x]

                for player in players:
                    await client.send_message(player.discord, '{} のターンです。'.format(player.name))
                    act = Thread(target = player.action, args = (players,remaining,), name = "act")
                    act.start()
                    while True:
                        state = send.get()
                        if state[0] == "end":
                            await client.send_message(player.discord, state[1])
                            break
                        elif state[0] == "exc":
                            await client.send_message(player.discord, state[1])
                        else:
                            await client.send_message(player.discord, state[1])
                        message = await client.wait_for_message(author = player.discord)#, content=state[0])
                        receive.put(message.content)

                players = swapThief(players)
                await client.send_message(CHANNEL, '全員のアクションが完了したので、誰を処刑するか話し合いを始めてください。\n話し合いが終わったら"/ready"と入力。')
                message = await client.wait_for_message(channel = CHANNEL, content = "/ready")

                await client.send_message(CHANNEL, 'それでは、投票に入ります。\n投票もDMで行います。')
                for player in players:
                    v = Thread(target = vote, args = (player, players, remaining,),name = "vote")
                    v.start()
                    while True:
                        state = send.get()
                        if state[0] == "end":
                            await client.send_message(player.discord, state[1])
                            break
                        elif state[0] == "exc":
                            await client.send_message(player.discord, state[1])
                        else:
                            await client.send_message(player.discord, state[1])
                        message = await client.wait_for_message(author = player.discord)
                        receive.put(message.content)
                results = getVoteResult(players, playable)
                await client.send_message(CHANNEL, '全員の投票が終わりました。')
                await client.send_message(CHANNEL, send.get())
                await client.send_message(CHANNEL, 'それでは、結果発表です。')
                getres = Thread(target = getGameresult, args = (players, results, remaining,), name = "getres")
                getres.start()
                while True:
                    state = send.get()
                    if state[0] == "end":
                        await client.send_message(CHANNEL, state[1])
                        break
                    else:
                        await client.send_message(CHANNEL, state[1])
            STARTED = False
            players = []


#===== JinroGame =====#
class Player():
    def __init__(self, discord):
        self.role = ""
        self.type = ""
        self.thiefflag = False
        self.thiefbuff = ""
        self.discord = discord
        self.name = self.discord.name
        self.voted = 0
        send.put(self.name)

    def action(self, players, remaining):
        if self.role == "fortune teller":
            send.put(["/fortune", 'あなたは##### fortune teller #####です。\n\n占いをするか、残りの2枚のカードを見るか選択してください。\n1 占う\n2 カードを見る'])#\n\n返答は"/fortune [content]"のフォーマットで行ってください。'])
            while True:
                choice = receive.get()
                if choice not in ["1", "2"]:
                    send.put(["exc", "入力が正しくありません。"])
                else:
                    choice = int(choice)
                    break

            if choice == 1:
                list = []
                sentence = "占いたい人の番号を入力してください。\n"
                for i, player in enumerate(players):
                    if player.name == self.name:
                        None
                    else:
                        sentence += (str(i+1) + " " + player.name + "\n")
                        list.append(str(i+1))
                send.put(["/fortune", sentence])
                while True:
                    target = receive.get()
                    if target is None:
                        None
                    elif target in list:
                        target = int(target) - 1
                        send.put(["end", players[target].name + " を占ったところ、 " + players[target].role + " だとわかりました。\n\nこれであなたのアクションは完了しました。"])
                        break
                    else:
                        send.put(["exc", "入力が正しくありません。"])

            elif choice == 2:
                sentence = "残りの2枚のカードは、" + str(remaining) + "です。\n\nこれであなたのアクションは完了しました。"
                send.put(["end", sentence])


        elif self.role == "werewolf":
            send.put(["/werewolf", "あなたは##### werewolf #####です。\n仲間を確認するため、カモフラージュも兼ねて何か適当に入力してください。\n"])
            lonely = True
            sentence = ""
            for player in players:
                if player.role == "werewolf":
                    if not player.name == self.name:
                        sentence += ("werewolf: " + player.name + "\n")
                        lonely = False
            if lonely:
                sentence = "仲間はいないようだ。\n"
            hoge = receive.get()
            sentence += "\nこれであなたのアクションは完了しました。"
            send.put(["end", sentence])


        elif self.role == "thief":
            sentence = "あなたは##### thief #####です。\n役職を交換したいプレイヤーの番号を入力してください。\n"
            list = []
            for i, player in enumerate(players):
                if player.name == self.name:
                    None
                else:
                    sentence += (str(i+1) + " " + player.name + "\n")
                    list.append(str(i+1))
            send.put(["/thief", sentence])
            while True:
                target = receive.get()
                if target is None:
                    None
                elif target in list:
                    target = int(target) - 1
                    newrole = players[target].role
                    players[target].thiefflag = True
                    self.thiefflag = True
                    self.thiefbuff = newrole
                    send.put(["end", players[target].name + " からカードを奪い、あなたは " + newrole + " になりました。\nこのことは相手には通知されません。\n\nこれであなたのアクションは完了しました。"])
                    break

                else:
                    send.put(["exc", "入力が正しくありません。"])


        elif self.role == "hangman":
            send.put(["/hangman", "あなたは##### hangman #####です。\nやることはないので、カモフラージュのために何か適当に打ち込んでください。"])
            hoge = receive.get()
            send.put(["end", "\nこれであなたのアクションは完了しました。"])

        elif self.role == "citizen":
            send.put(["/citizen","あなたは##### citizen #####です。\nやることはないので、カモフラージュのために何か適当に打ち込んでください。"])
            hoge = receive.get()
            send.put(["end", "\nこれであなたのアクションは完了しました。"])

    def killed(self, players, playable):#returnは勝利プレイヤーの属性
        if self.role == "hangman":
            return "hangman"
        elif self.role == "werewolf":
            return "citizen"
        elif "werewolf" not in playable:
            return "nobody"
        else:
            return "werewolf"

def makeDeck(num_player):
    num_player = int(num_player)
    deck = []
    role = []
    roles = config["roles{}".format(num_player)]
    for i in roles:
        role.append(i)
    for i in role:
        a = int(roles[i])
        for j in range(a):
            deck.append(i)
    return deck

def decideRole(deck):
    random.shuffle(deck)
    playable = deck[:-2]
    remaining = deck[-2:]

    return playable, remaining

def swapThief(players):
    for player in players:
        if player.thiefflag == True:
            if player.role == "thief":
                player.role = player.thiefbuff
            else:
                player.role = "thief"

    return players

def vote(player, players, playable):
    sentence = player.name + " さんの投票です。\n投票したいプレイヤーの番号を入力してください。\n"
    list = []
    for x, i in enumerate(players):
        if player.name != i.name:
            sentence += (str(x+1) + " " + i.name + "\n")
            list.append(str(x+1))

    send.put(["/vote", sentence])
    while True:
        tar = receive.get()
        if tar.isdigit() and tar in list:
            players[int(tar)-1].voted += 1
            send.put(["end", players[int(tar)-1].name+" に投票しました。"])
            break
        else:
            send.put(["exc", "入力が正しくありません。"])

def getVoteResult(players, playable):
    judge = []
    names = []
    most = players[0].voted
    for player in players:
        if player.voted == most:
            judge.append(player)
            names.append(player.name)
        elif player.voted > most:
            judge = []
            names = []
            judge.append(player)
            names.append(player.name)
            most = player.voted

    if len(names) == len(players):
        send.put("あなたたちは平和村を宣言しました。")
        if "werewolf" in playable:
            return ["werewolf"]
        else:
            return ["peaceful"]

    send.put("投票の結果、処刑されるプレイヤーは " + str(names) + " です。")
    results = []
    for i in judge:
        results.append(i.killed(players, playable))
    return results


def judgement(players, playable):#投票なしの場合
    sentence = "\nそれでは、処刑するプレイヤーの番号を入力してください。\n平和村だと思う場合は、0を入力してください。\n\n"
    sentence += "0 平和村宣言\n"
    for i, player in enumerate(players):
        sentence += (str(i+1) + " " + player.name + "\n")
    while True:
        judge = receive.get()
        if judge is None:
            None
        elif judge == "0":
            send.put(["end","あなたたちは平和村を宣言しました。"])
            if "werewolf" not in playable:
                return "peaceful"
            else:
                return "werewolf"
        elif judge not in list:
            send.put(["exc", "入力が正しくありません。"])
        else:
            send.put(["end", players[int(judge)-1].name + " を処刑します。"])
            result = players[int(judge)-1].killed(players, playable)
            break
    return result

def getGameresult(players, results, remaining):
    sentence = ""
    sleep(3)
    if "hangman" in results:
        send.put([" ", "### 吊り人 ### の勝利です。\n\n勝利プレイヤー\t役職"])
        for player in players:
            if player.role == "hangman":
                sentence += (player.name + "\t" + player.role + "\n")
        send.put([" ", sentence])

    elif "citizen" in results:
        send.put([" ", "### 市民チーム ### の勝利です。\n\n勝利プレイヤー\t役職"])
        for player in players:
            if player.role not in ["hangman", "werewolf"]:
                sentence += (player.name + "\t" + player.role + "\n")
        send.put([" ", sentence])

    elif "werewolf" in results:
        send.put([" ", "### 人狼チーム ### の勝利です。\n\n勝利プレイヤー\t役職"])
        for player in players:
            if player.role == "werewolf":
                sentence += (player.name + "\t" + player.role + "\n")
        send.put([" ", sentence])
    elif "peaceful" in results:
        send.put([" ", "### 平和村 ### でした。\n"])

    elif "nobody" in results:
        send.put([" ", "### 勝者なし ###\n"])

    sentence = "\n\n各プレイヤーの役職は以下の通りでした。\n"
    for i, player in enumerate(players):
        sentence += (player.name + "\t" + player.role + "\n")
    sentence += ("\nそして、残っていた2枚のカードは" + str(remaining) + "でした。\n\nお疲れさまでした。")
    send.put(["end", sentence])


#===== main =====#
def main():
    client.run(config["BOT"]["TOKEN"])

if __name__ == "__main__":
    main()
