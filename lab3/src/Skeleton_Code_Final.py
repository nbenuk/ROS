#!/usr/bin/env python

# Exercise 4 - following a colour (green) and stopping upon sight of another (blue).

from __future__ import division
import cv2
import numpy as np
import rospy
import sys

from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class colourIdentifier():

    def __init__(self):
        # Initialise a publisher to publish messages to the robot base
        # We covered which topic receives messages that move the robot in the 2nd Lab Session
        self.pub = rospy.Publisher('mobile_base/commands/velocity', Twist, queue_size=10)
        # rospy.init_node('Square', anonymous=True)

        self.rate = rospy.Rate(5)

        # Initialise any flags that signal a colour has been detected (default to false)
        self.colour1_flag = 0
        self.colour2_flag = 0

        # Initialise the value you wish to use for sensitivity in the colour detection (10 should be enough)
        self.sensitivity = 10

        # Initialise some standard movement messages such as a simple move forward and a message with all zeroes (stop)
        self.forward = Twist()
        self.forward.linear.x = 0.2
        self.back = Twist()
        self.back.linear.x = -0.2
        self.stop = Twist()
        self.stop.linear.x = 0.0



        # Remember to initialise a CvBridge() and set up a subscriber to the image topic you wish to use
        self.bridge = CvBridge()

        # We covered which topic to subscribe to should you wish to receive image data
        self.image_sub = rospy.Subscriber("camera/rgb/image_raw",Image, self.callback)

    def callback(self, data):
        # Convert the received image into a opencv image
        # But remember that you should always wrap a call to this conversion method in an exception handler
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        # Set the upper and lower bounds for the two colours you wish to identify
        #hue value = 0 to 179
        hsv_colour1_lower = np.array([60- self.sensitivity, 100, 100])
        hsv_colour1_upper = np.array([60 + self.sensitivity, 255, 255])
        hsv_colour2_lower = np.array([100 - self.sensitivity, 100, 100])
        hsv_colour2_upper = np.array([120+ self.sensitivity, 255, 255])

        # Convert the rgb image into a hsv image
        Hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

        # Filter out everything but a particular colour using the cv2.inRange() method
        mask1 = cv2.inRange(Hsv_image, hsv_colour1_lower, hsv_colour1_upper)
        mask2 = cv2.inRange(Hsv_image, hsv_colour2_lower, hsv_colour2_upper)

        # Apply the mask to the original image using the cv2.bitwise_and() method
        # As mentioned on the worksheet the best way to do this is to bitwise and an image with itself and pass the mask to the mask parameter
        mask1_image = cv2.bitwise_and(Hsv_image, Hsv_image, mask=mask1)
        mask2_image = cv2.bitwise_and(Hsv_image, Hsv_image, mask=mask2)

        # Find the contours that appear within the certain colour mask using the cv2.findContours() method
        # For <mode> use cv2.RETR_LIST for <method> use cv2.CHAIN_APPROX_SIMPLE
        contours, heirachical = cv2.findContours(mask1 ,cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
            # Loop through the list and keep track of which contour is biggest or
            # Use the max() method stopto find the largest contour
            #c = max(<contours>, key=cv2.contourArea)
            biggest_contour = max(contour_sizes, key=lambda x: x[0])[1]

            #Check if the area of the shape you want is big enough to be considered
            M = cv2.moments(biggest_contour)
            cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            # If it is then change the flag for that colour to be True(1)
            if cv2.contourArea(biggest_contour) > 5 : #<What do you think is a suitable area?>:
                # Alter the value of the flag
                self.colour1_flag = 1

        contours, heirachical = cv2.findContours(mask2 ,cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            contour_sizes = [(cv2.contourArea(contour), contour) for contour in contours]
            # Loop through the list and keep track of which contour is biggest or
            # Use the max() method stopto find the largest contour
            #c = max(<contours>, key=cv2.contourArea)
            biggest_contour2 = max(contour_sizes, key=lambda x: x[0])[1]

            #Check if the area of the shape you want is big enough to be considered
            M = cv2.moments(biggest_contour2)
            cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            # If it is then change the flag for that colour to be True(1)
            if cv2.contourArea(biggest_contour2) > 5 : #<What do you think is a suitable area?>:
                # Alter the value of the flag
                self.colour2_flag = 1
        #Check if a flag has been set = colour object detected - follow the colour object
        if self.colour1_flag == 1:
            if cv2.contourArea(biggest_contour) > 20000:
                # Too close to object, need to move backwards
                self.pub.publish(self.back)
                self.rate.sleep()
            elif cv2.contourArea(biggest_contour) < 20000:
                # Too far away from object, need to move forwards
                self.pub.publish(self.forward)
                self.rate.sleep()
            else:
                self.pub.publish(self.stop)
                self.rate.sleep()
            self.colour1_flag = 0


                # Too close to object, need to move backwards
        # Be sure to do this for the other colour as well
        #Setting the flag to detect blue, and stop the turtlebot from moving if blue is detected
        if self.colour2_flag == 1:

        # Publish moves
            self.pub.publish(self.stop)
            self.rate.sleep()
            self.colour2_flag = 0

        #Show the resultant images you have created. You can show all of them or just the end result if you wish to.
        cv2.imshow("massk1",mask1_image)
        cv2.waitKey(3)
# Create a node of your class in the main and ensure it stays up and running
# handling exceptions and such
def main(args):
    # Instantiate your class
    # And rospy.init the entire node
    rospy.init_node('colourIdentifier', anonymous=True)

    cI = colourIdentifier()
    # Ensure that the node continues running with rospy.spin()
    # You may need to wrap it in an exception handler in case of KeyboardInterrupts
    # Remember to destroy all image windows before closing node

    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
    cv2.destroyAllWindows()
# Check if the node is executing in the main path
if __name__ == '__main__':
    main(sys.argv)
