from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.ofproto import ether
from ryu.ofproto import inet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import ipv6
from ryu.lib import hub
from database import database


class final(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(final, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.port_to_mac = {}
        self.datapaths = {}
        self.update_thread = hub.spawn(self._update)

    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.info('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.info('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        self.logger.info("************ add_flow *************")
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id, priority=priority, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        self.logger.info("send to "+str(datapath)+" ("+str(datapath.id)+")"+" msg : "+str(mod))
        datapath.send_msg(mod)

    # Sub program to handle packet_in
    def L2Learning(self, msg, datapath, ofproto, parser, in_port, src, dst):
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.port_to_mac.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        self.port_to_mac[dpid][in_port] = src
        out_port = ofproto.OFPP_FLOOD
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
        actions = [parser.OFPActionOutput(out_port)]
        # auto create rela
        reverse_match = parser.OFPMatch(in_port=out_port, eth_dst=src)
        reverse_actions = [parser.OFPActionOutput(in_port)]

        if out_port != ofproto.OFPP_FLOOD:
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                self.add_flow(datapath, 1, reverse_match, reverse_actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
                self.add_flow(datapath, 1, reverse_match, reverse_actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)


    # main loop of update thread
    def _update(self):
        
        while True:
            for dp in self.datapaths.values():
                parser = dp.ofproto_parser
                ofproto = dp.ofproto
                self.logger.info("dpid="+str(dp.id));
                if dp.id == 161 :
                    
                    self.logger.info("Check SQL Database")
                    db = database()
                    list = db.db_getList()
                    for data in list:
                        print data["id"],"(",type(data["id"]),")"," ",data["address"],"(",type(data["address"]),")"," ",data["access"],"(",type(data["access"]),")"
                        if data["access"] == 1:
                             
                            self.logger.info("DENY "+str(data["address"]))
                            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=str(data["address"]))
                            actions = {}
                            self.add_flow(dp, data["id"]+10, match, actions)

                        if data["access"] == 0:
                            self.logger.info("ALLOW "+str(data["address"]))
                            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=str(data["address"]))
                            mod = parser.OFPFlowMod(dp, command=ofproto.OFPFC_DELETE, out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY, match=match)
                            dp.send_msg(mod)



            hub.sleep(10)

    def ipv4_handler(self, msg, datapath, ofproto, parser, in_port, eth, v4):
        dpid = datapath.id
        self.logger.info("ipv4_handler : packet in %s [%s] %s %s", dpid, in_port, v4.src, v4.dst)
        self.L2Learning(msg, datapath, ofproto, parser, in_port, eth.src, eth.dst)
        return
    
    def ipv6_handler(self, msg, datapath, ofproto, parser, in_port, eth, v6):
        return

    def arp_handler(self, msg, datapath, ofproto, parser, in_port, eth):
        dpid = datapath.id
        self.logger.info("arp_handler : packet in %s [%s] %s %s", dpid, in_port, eth.src, eth.dst)
        self.L2Learning(msg, datapath, ofproto, parser, in_port, eth.src, eth.dst)
        return

    def vlan_handler(self, msg, datapath, ofproto, parser, in_port, eth):
        dpid = datapath.id
        self.logger.info("vlan_handler : packet in %s [%s] %s %s", dpid, in_port, eth.src, eth.dst)
        return

    def lldp_handler(self, msg, datapath, ofproto, parser, in_port):
        # ignore lldp packet
        return

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        self.logger.info('ethernet type = '+hex(eth.ethertype)+' in_port = '+str(in_port))
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
        # LLDP
            self.logger.info('LLDP')
            self.lldp_handler(msg, datapath, ofproto, parser, in_port)
        elif eth.ethertype == 0x0800:
        # IPV4
            v4 = pkt.get_protocols(ipv4.ipv4)[0]
            if v4 :
                self.logger.info('IPV4')
                self.ipv4_handler(msg, datapath, ofproto, parser, in_port, eth, v4)
            else :
                self.logger.info('!IPV4')
        elif eth.ethertype == 0x86dd:
        # IPV6
            v6 = pkt.get_protocols(ipv6.ipv6)[0]
            if v6 :
                self.logger.info('IPV6')
                self.ipv6_handler(msg, datapath, ofproto, parser, in_port, eth, v6)
            else :
                self.logger.info('!IPV6')
        elif eth.ethertype == 0x0806:
        # ARP
            self.logger.info('ARP')
            self.arp_handler(msg, datapath, ofproto, parser, in_port, eth)
        elif eth.ethertype == 0x8100:
        # VLAN
            self.logger.info('VLAN')
            self.vlan_handler(msg, datapath, ofproto, parser, in_port, eth)
        else:
            self.logger.info('UNKNOW')

