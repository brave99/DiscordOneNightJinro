# DiscordOneNightJinro


## Overview
This is a discord bot that can be a GM of OneNightJinro game.
Required libraly is only "discord.py".
Have fun with your BOT!!

Now text message from BOT is all in Japanese, but English version is coming soon.

This software is released under the MIT License, see LICENSE.


Discordでワンナイト人狼のGMをやってくれるBOTです。
現在、言語は日本語のみですが、英語版も作成中です。
動作環境はPython3です。

## 導入方法
1. ダウンロードorクローン

2. 要求ライブラリのインストール

    `$ pip install discord`


## 遊び方
##### ０. 準備
Discordの開発者ページから、BOTを作成し、自分のサーバーに招待する。
option.iniの[BOT]以下の
`TOKEN= `と`CHANNEL= `
のところに使用するBOTのTOKENと、BOTとのやりとりに使いたいテキストチャンネルのIDをコピペする。

##### １. 起動
解凍したディレクトリで、
`$ python run_Bot.py`

##### ２. ゲームをプレイ
起動するとoption.iniで指定したチャンネルにBOTが現れます。
次に何をすればいいのかなどはすべてチャットで教えてくれるようになっています。

## ルール
### 役職一覧
人狼(werewolf),
吊り人(hangman),
占い師(fortune teller),
怪盗(thief),
市民(citizen)

### 勝利条件
人狼：市民陣営が処刑される。

吊り人：自分自身が処刑される。

市民陣営(占い師、怪盗、市民)：人狼を処刑する。あるいは、人狼がいない状態で平和村*を宣言する。

*平和村は、処刑の投票で各プレーヤーに1票ずつ入っていると自動的に平和村宣言になる。
このとき、人狼がいなければ市民陣営の勝利となり、1人でも人狼がいれば人狼の勝利になる。

### 投票
話し合いの後、誰を処刑するかは投票で決める。
被投票数が並んだ場合は、複数人が処刑されることもあり得る。
その場合の勝者判定は、吊り人＞市民陣営＞人狼となる。

誰が誰に入れたかなどは見えないようになっている。


## その他
MITライセンスの範囲内で、改変・再配布・宣伝等ご自由にしていただいて構いません。その際はお知らせいただけると喜びます。
不具合や不明な点等がありましたら、気軽にissueを開いてください。
