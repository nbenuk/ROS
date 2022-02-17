#!/usr/bin/env python


import rospy
from geometry_msgs.msg import Twist

def drive_circle():
    pub = rospy.Publisher('mobile_base/commands/velocity', Twist)
    rospy.init_node('Circle', anonymous=True)
    rate = rospy.Rate(10) 
    desired_velocity = Twist()
    desired_velocity.linear.x = 0.5
    desired_velocity.linear.y = 0.5 
    desired_velocity.angular.z = 0.5
    
    while not rospy.is_shutdown():
        pub.publish(desired_velocity)
        rate.sleep()

if __name__ == "__main__":
	try:
		drive_circle()
	except rospy.ROSInterruptException:
		pass
