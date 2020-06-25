#!/usr/bin/env python

# A script to check the VLP 16 lidar upon powerup,
# and reset it if the lidar motor's rpm is not 600 (default).
# The script will loop until the (min) desired rpm is achieved,
# and will exit then.
# By Arif Rahman Jan 2020

import pycurl
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIOasBytesIO
try: 
    from urllib.parse import urlencode 
except ImportError: 
    from urllib import urlencode 
import urllib2 
import json 
import  time
import rospy

def sensor_do(s,url,pf,buf):
    s.setopt(s.URL,url) 
    s.setopt(s.POSTFIELDS,pf) 
    s.setopt(s.WRITEDATA,buf) 
    s.perform() 
    rcode = s.getinfo(s.RESPONSE_CODE) 
    success = rcode in range(200,207) 
    print('%s %s: %d (%s) ' %(url,pf,rcode,'OK' if success else'ERROR')) 
    return success

def rpm_check():
    rospy.init_node("vlp_rpm_check", anonymous=False)

    # Change the IP address and desired rpm here if needed
    Base_URL = 'http://192.168.1.201/cgi/'
    rpm_desired = 600*0.9 # at least 90% of desired rpm

    sensor = pycurl.Curl() 
    buffer = BytesIO() 

    rpm = 0;
    
    # give some time for lidar to turn on
    time.sleep(20)
    # then check 
    while (rpm < rpm_desired) and (not rospy.is_shutdown()):
        # get the lidar status
        response = urllib2.urlopen(Base_URL+'status.json')  
        if response:
            status = json.loads(response.read()) 
            rpm = status['motor']['rpm']
            rospy.loginfo('Sensor laser is %s, motor rpm is %s' %(status['laser']['state'], status['motor']['rpm']))

        # reset if necessary
        if rpm < rpm_desired:   
            rospy.logerr("Resetting lidar...")
            rc = sensor_do(sensor,Base_URL+'reset',urlencode({'data':'reset_system'}) ,buffer)  
            if rc: 
                for t in range(5,0,-1):
                    rospy.loginfo("Lidar restarting in {}".format(t)) 
                    time.sleep(3)
                    

    sensor.close() 


if __name__ == '__main__':
    rpm_check()