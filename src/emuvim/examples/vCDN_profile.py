"""
Copyright (c) 2015 SONATA-NFV
ALL RIGHTS RESERVED.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written
permission.

This work has been performed in the framework of the SONATA project,
funded by the European Commission under Grant number 671517 through
the Horizon 2020 and 5G-PPP programmes. The authors would like to
acknowledge the contributions of their colleagues of the SONATA
partner consortium (www.sonata-nfv.eu).
"""
"""
One datacenter switch where VNFs are added for profiling tests.

        (dc1) <<-->> VNF1,2,..

- SAP deployment enabled
- learning switch enabled
"""

import logging
from mininet.log import setLogLevel
from emuvim.dcemulator.net import DCNetwork
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from emuvim.api.sonata import SonataDummyGatekeeperEndpoint
from mininet.node import RemoteController

logging.basicConfig(level=logging.INFO)

# sudo python src/emuvim/examples/vCDN_profile.py

def create_topology1():
    # create topology
    net = DCNetwork(controller=RemoteController, monitor=True, enable_learning=True)
    dc1 = net.addDatacenter("dc1")


    # add the command line interface endpoint to each DC (REST API)
    rapi1 = RestApiEndpoint("0.0.0.0", 5001)
    rapi1.connectDCNetwork(net)
    rapi1.connectDatacenter(dc1)
    # run API endpoint server (in another thread, don't block)
    rapi1.start()

    # add the SONATA dummy gatekeeper to each DC
    #sdkg1 = SonataDummyGatekeeperEndpoint("0.0.0.0", 5000, deploy_sap=True)
    #sdkg1.connectDatacenter(dc1)
    # run the dummy gatekeeper (in another thread, don't block)
    #sdkg1.start()

    # start the emulation platform
    net.start()  # here the docker host default ip is configured

    # topology must be started before hosts are added
    cache = dc1.startCompute('cache', image="squid-vnf", network=[{"ip": "10.10.0.1/24", "id": "client", 'mac': "aa:aa:aa:00:00:01"},
                                                                  {"ip": "10.20.0.1/24", "id": "server", "mac": "aa:aa:aa:00:00:02"}])

    client = dc1.startCompute('client', image='vcdn-client', network=[{"ip": "10.10.0.2/24", "id": "client"}])

    server = dc1.startCompute('server', image='webserver', network=[{"ip": "10.20.0.2/24", "id": "server"}])


    
    #client = net.addDocker('client', ip='10.10.0.1/24', dimage="vcdn-client") 
    #cache = net.addDocker('cache', dimage="squid-vnf")
    #server = net.addDocker('server', ip='10.20.0.1/24', dimage="webserver")
    #net.addLink(dc1, client,  intfName1='dc-cl', intfName2='client')
    #net.addLink(dc1, server,  intfName1='dc-sv', intfName2='server')
    #net.addLink(dc1, cache,  intfName1='dc-ccl', intfName2='client', params1={'ip': '10.10.0.2/24'})
    #net.addLink(dc1, cache,  intfName1='dc-csv', intfName2='server',params1={'ip': '10.20.0.2/24'})

    # initialise VNFs
    cache.cmd("./start.sh", detach=True)
    client.cmd("./start.sh", detach=True)
    server.cmd('./start.sh', detach=True)

# startup script hangs if we use other startup command
# command="./start.sh"

    net.CLI()
    net.stop()
    while not net.exit:
        pass



def main():
    setLogLevel('debug')  # set Mininet loglevel
    create_topology1()


if __name__ == '__main__':
    main()
