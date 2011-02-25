## Sumarry

python-net-weathermap is a python tool that create visual map of the network
links utilization, using MRTG data aggregation.
If you are the Internet Provider or network operator and you are using MRTG tool
to logging your network, just try to use this package for creating a network
weather map of your network.

## Dependencies

python-net-weathermap requires [pycairo][1] Python bindings for the cairo library
and [py-rrdtool][2] Python Interface to RRDTool

## Usage

        from net_weathermap import Node, Link, Map
        
        # First, we need to define our nodes
        a = Node(x=40,y=240,label='Device A')
        b = Node(x=600,y=240,label='Device B')
        
        # Second, we define the link with a and b nodes and bandwidth 1000 Mb/s
        # myrrdfile.rrd is a MRTG data aggregation of this link
        
        link = Link(a,b,1000,rrdfile='myrrdfile.rrd')
        
        # Third, we place our link to the map and draw all elements
        map = Map([link])
        map.draw_arrows()
        map.draw_labels()
        
        # Saving our map to the file
        
        map.save('mymap.png')


[1]: http://cairographics.org/releases/
[2]: http://sourceforge.net/projects/py-rrdtool/