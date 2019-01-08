# SDN_NetCut
A Software Defined Network technique to reach a powerful NetCut capability
<pre>
SDN-based Netcut

Introduction :
有鑒於現在亂用頻寬的人很多，需要讓管理者能夠切斷亂用網路的人的頻寬，
一個方便的斷網工具是十分有必要的。NetCut雖然簡單易用，但是容易防禦，
又會製造垃圾封包。本專題目的為開發一套基於SDN的斷網工具，不僅簡單易用，
而且一般使用者完全無力反抗。

Dependency :
ryu-sdn-framework
python
python sqlite library
mininet

How to use :
// Create BlackList Database
python init.py
// Check out BlackList
python read.py
// Open user interface web server 
python http.py
// Start ryu controller
ryu-manager main.py
// Use mininet to start experiment
sudo mn ...

</pre>
