# Vibrotactile Feedback Project
Haptic Vest and Motion Sensor Interface

<p align="center">
![bhaptics](https://github.com/toazbenj/Vibrotactile-Feedback-Project/assets/90994176/2dd1d1f2-bb7b-43d1-8375-138a39e7c8e1)
</p>

Description

This set of programs was made to enable the user to take euler angle position data from YOST Labs 3-space sensors to calculate the relative positions of two subjects.
That relative position is used to determine the type of haptic feedback to give the second subject, the student, in order to get them to move into the same
position as the first subject, the teacher, without being able to see them. The haptics is given via the bHpatics Tactsuit, a VR gaming vest with 40 motors that encase the wearer's abdomin.  

Programs

The relevent programs for this project are finalTandemControlGame and 2ndVestClient. finalTandemControlGame creates a graphics window that allows the subjects to jointly control a ball object to guide it through a series of targets. The better in sync both subjects are, the more effectively they will be able to hit the 
targets in the time allowed. Control of the ball is done by bending the upper body in the four cardinal directions, but the x and y coordinates are reversed within the program, forcing the participants to adapt. Haptics are employed to help guide a less experienced participant using the movements of a seasoned player. In order to run individualized haptics on the teacher's vest, 2ndVestClient is run on a separate computer with the respective vest connected to a second bHaptics Player program.

Support

More information on the IMU API can be found at https://yostlabs.com/3-space-application-programming-interface/. Within this repository are the TACT haptics files accessed by the programs to activate the motors of the Tactsuits in proper sequence. These were made using the free development resource at https://designer.bhaptics.com/. bHaptics Device Player is needed to connect to the Tactsuits, though the programs can run without error while the suits are not connected for testing purposes. See https://www.bhaptics.com/support/downloads. Both programs were written to be used with a bluetooth dongle and 2 YOST Labs IMU sensors. Their serial numbers must be committed to the dongle using the YOST Labs 3-Space Suit application before they can be referenced within the program. Download at https://yostlabs.com/yost-labs-3-space-sensor-software-suite/. Information on setup and operation is included in the Tandem Control Game Setup document. These programs work best when used with python 3.8.5 or later.
