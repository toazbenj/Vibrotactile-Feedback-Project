# vibrotactileFeedbackProject
Haptic Vest and Motion Sensor Interface

Desciption

This set of programs was made to enable the user to take euler angle position data from YOST Labs 3-space sensors to calculate the relative positions of two subjects.
That relative position is used to determine the type of haptic feedback to give the second subject, the student, in order to get them to move into the same
position as the first subject, the teacher, without being able to see them. The haptics is given via the bHpatics Tactsuit, a VR gaming vest with 40 motors that encase the wearer's abdomin.  

Programs

The relevent programs for this project are named followMe and tandemControlGame. followMe includes the raw functionality of calculating the differences in position for the two
subjects and choosing the direction and intensity of the haptics recieved by the student. tandemControlGame does this while also opening up a graphics window and allowing the 
subjects to jointly control a ball object to guide it through a series of targets. The better in sync both subjects are, the more effectively they will be able to hit the 
targets in the time allowed. Both programs gather data on the positions of the subjects and the haptics and compile them within a CSV file. 

Support

All file folders and other python programs are relavant to running these two programs with few exceptions. Special emphasis is put on utilitiesMethods, threespace_api, and the 
bhaptics folder. Within this package is also contained the TACT haptics files accessed by the programs to activate the motors of the Tactsuits in proper sequence. These were 
made using the free development resource at https://designer.bhaptics.com/. bHaptics Device Player is needed to connect to the Tactsuits, though the programs can run without error while the suits are not connected for testing purposes. Both programs were written to be used with a bluetooth dongle and 2 YOSH Labs IMU sensors. Their serial numbers must be committed to the dongle using the YOSH Labs 3-Space Suit application before they can be referenced within the program. These programs work best when used with python 3.8.5 or later.
