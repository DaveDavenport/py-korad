"""This sample program will use the kel103 to test a batteries capacity and
show this information in matplotlib. This method is an aproximation and its resolution
can be increase with sampling rate.
"""
import socket
import time
import re
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from korad import kel103

#test proporties
cutOffVoltage = 2.5
dischargeRate = 1.0
MISSED_LIMIT = 10 # amount of missed samples that is allowed

# setup the device (the IP of your ethernet/wifi interface, the IP of the Korad device)
kel = kel103.kel103("192.168.1.56", "10.10.10.186", 18190)
if not kel.checkDevice():
    raise Exception("Failed to connect to device!")

# a quick battery test
kel.setOutput(False)
#voltage = kel.measureVolt()
#kel.setCurrent(dischargeRate)
kel.setBatteryMode(4,10,dischargeRate,cutOffVoltage,100,60*10)
kel.setBatteryRecall(4)
kel.getBatteryRecall()


voltageData = []
timeData = []
capacityData = []
current = 0
capacity = 0
kel.setOutput(True)

# run the test
startTime = time.time()
missedSuccessiveSamples = 0

logfile = open("test_" + str(time.time()) + ".png", "x")

while kel.checkOutput():
    try:
        # store the time before measuring volt/current
        current_time = (time.time() - startTime)
        voltage = kel.measureVolt()
        current = kel.measureCurrent()
        power   = kel.measurePower()
        voltageData.append(voltage)
        print('a')
        # Only append the timedata when volt/current measurements went fine.
        # This is because the voltage or current measurement could fail
        # and then the x and y-axis would have different dimentions
        timeData.append(current_time)

        print('b')
        # solve the current stuff as a running accumulation
        capacity = kel.getBatteryCapacity() #((startTime - time.time()) / 60 / 60) * current
        runtime = kel.getBatteryTime()
        capacityData.append(capacity)
        print('c')

        print("Voltage: " + str(voltage) + " V DC, Capacity: " + str(capacity) + " Ah")

        logfile.write(str(runtime)+','+str(voltage)+','+str(current)+','+str(power)+','+str(capacity)+'\n')
        logfile.flush()

        time.sleep(0.50)
        missedSuccessiveSamples = 0
    except Exception as e:
        print(e)
        missedSuccessiveSamples += 1
        if missedSuccessiveSamples >= MISSED_LIMIT:
            raise Exception("Too many missed samples!")

# disable the output
kel.setOutput(False)
kel.endComm()

logfile.close()

# plot the finished data
fig, ax = plt.subplots()
ax.plot(timeData, capacityData)

ax.set(xlabel='time (s)', ylabel='capacity (AH)',
    title='Battery Discharge Test {}A: {:.4f}Ah'.format(dischargeRate, capacity))
ax.grid()

fig.savefig("test_" + str(time.time()) + ".png")
plt.show()
