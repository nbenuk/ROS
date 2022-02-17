#!/usr/bin/env python


import rospy
from geometry_msgs.msg import Twist
from math import radians

def drive_square():
    pub = rospy.Publisher('mobile_base/commands/velocity', Twist)
    rospy.init_node('Square', anonymous=True)
    rate = rospy.Rate(5) 
    desired_velocity = Twist()
    desired_velocity.linear.x = 0.2
    desired_velocity.linear.y = 0.0 
    desired_velocity.angular.z = 0.0
    
    while not rospy.is_shutdown():
        # drive straight
        for i in range (10):
            pub.publish(desired_velocity)
            rate.sleep()
        # turn 90 degrees
        for i in range(10):
            desired_velocity.linear.x = 0.2
            desired_velocity.angular.z = radians(45)
            pub.publish(desired_velocity)
            rate.sleep()
        desired_velocity.linear.x = 0.2
        desired_velocity.linear.y = 0 
        desired_velocity.angular.z = 0.0

if __name__ == "__main__":
	try:
		drive_square()
	except rospy.ROSInterruptException:
		pass