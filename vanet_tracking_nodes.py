#!/usr/bin/env python

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.sumo.runner import sumo
from mn_wifi.link import wmediumd, ITSLink
from mn_wifi.wmediumdConnector import interference

def topology():

    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    for id in range(0, 10):
        net.addCar('car%s' % (id+1), wlans=2, encrypt=['wpa2', ''])

    kwargs = {'ssid': 'vanet-ssid', 'mode': 'g', 'passwd': '123456789a',
              'encrypt': 'wpa2', 'failMode': 'standalone', 'datapath': 'user'}
              
    e1 = net.addAccessPoint('e1', mac='00:00:00:11:00:01', channel='1',
                            position='3279.02,3736.27,0', **kwargs)
    e2 = net.addAccessPoint('e2', mac='00:00:00:11:00:02', channel='6',
                            position='3620.82,3565.75,0', **kwargs)
    e3 = net.addAccessPoint('e3', mac='00:00:00:11:00:03', channel='11',
                            position='2806.42,3395.22,0', **kwargs)
    e4 = net.addAccessPoint('e4', mac='00:00:00:11:00:04', channel='1',
                            position='3332.62,3253.92,0', **kwargs)
    e5 = net.addAccessPoint('e5', mac='00:00:00:11:00:05', channel='6',
                            position='2887.62,2935.61,0', **kwargs)
    e6 = net.addAccessPoint('e6', mac='00:00:00:11:00:06', channel='11',
                            position='3651.68,3083.40,0', **kwargs)
    e7 = net.addAccessPoint('e7', mac='00:00:00:11:00:07', channel='1',
                            position='3351.68,2870.40,0', **kwargs)
    c1 = net.addController('c1')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    net.addLink(e1, e2)
    net.addLink(e2, e3)
    net.addLink(e3, e4)
    net.addLink(e4, e5)
    net.addLink(e5, e6)
    net.addLink(e6, e7)
    for car in net.cars:
        net.addLink(car, intf=car.wintfs[1].name,
                    cls=ITSLink, band=20, channel=181)

    # exec_order: Tells TraCI to give the current
    # client the given position in the execution order.
    # We may have to change it from 0 to 1 if we want to
    # load/reload the current simulation from a 2nd client
    net.useExternalProgram(program=sumo, port=8813,
                           #config_file='map.sumocfg', # optional
                           extra_params=["--start --delay 1000"],
                           clients=1, exec_order=0)

    info("*** Starting network\n")
    net.build()
    c1.start()
    e1.start([c1])
    e2.start([c1])
    e3.start([c1])
    e4.start([c1])
    e5.start([c1])
    e6.start([c1])

    for enb in net.aps:
        enb.start([])

    for id, car in enumerate(net.cars):
        car.setIP('192.168.0.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[0].name))
        car.setIP('192.168.1.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[1].name))

    # Track the position of the nodes
    nodes = net.cars + net.aps
    net.telemetry(nodes=nodes, data_type='position',
                  min_x=2500, min_y=2500,
                  max_x=4000, max_y=4000)

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
