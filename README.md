SDN-NetCut
===

## 簡介

此作品為進入中央實驗室之前的SDN應用專案，有鑑於現在內網亂用頻寬的人很多，需要讓管理者能夠切斷亂用網路頻寬的人，因此一個方便的斷網工具是十分必要的，SDN具有將網路行為程式化的能力，因此可以下Flow把目標使用者封鎖。基於ARP Spoofing的Netcut雖然簡單易用，但會製造很多垃圾封包，故本專案旨在提供一套基於SDN斷網設定，可透過Web進行設定，十分簡單易用，而且讓惡意使用者無力抵抗。

## 所需套件

1. ryu-sdn-framework

2. python sqlite 

3. mininet

## 如何啟動

1. 創建 BlackList DB `python createdb.py`

2. 確認 BlackList 是否有欲封鎖 IP `python blacklist.py`

3. 開啟 Web Server 端 `python webserver.py`

4. 開啟 Ryu Controller `ryu-manager main.py`

5. 啟動 Mininet 環境，也可以自己弄在真實環境