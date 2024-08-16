import serial
import time
import datetime
from datetime import timezone
import pandas as pd
import sys


arduino = serial.Serial(baudrate = 9600, timeout=.1)        # Initialising the USB comunicaton

# Reading initial values from comandline in terminal

if len(sys.argv) == 4:

    reps = str(sys.argv[1])
    measTime = str(sys.argv[2])
    port = str(sys.argv[3])

else:

# Reads initial values from user in terminal
    
    reps = input("Enter number of measurements per minute: ")
    measTime = input("Enter runtime for the program in minutes: ")
    port = input("Select port: ")


try:

    if int(reps) > 60:
        reps = str(60)
        print("\nThe number of measurements is to high. Using '60'")

    reps = "SMFST" + reps
    measTime = "SMLST" + measTime

    # Sends necessary data to arduino and conects to USB port
    
    arduino.port = port
    arduino.open()
    time.sleep(1)
    arduino.write(bytes(reps, 'utf'))
    time.sleep(0.5)
    arduino.write(bytes(measTime, 'utf'))
    time.sleep(0.5)

    print("\n Please wait while I read the data you asked for :) \n\n To stop program pres 'Ctrl + c' The data so far will be saved\n")

    clock = datetime.datetime.now(timezone.utc).isoformat()
    filename = "Datafile_" + clock[0:19] + ".csv"

except:

    print("\nEntered data is incorrect or USB port is not conected\n")

else:

    

    Data = "NV"
    EndTask = "NV"
    LogTime = "NV"
    EndMesage = "NV"

    count = 0

    time_list = []
    sensor_ID_list = []
    ID_6_bit_list = []
    data_list = []
    celsius_list = []    

    try:


        # Receives and saves the line from the arduino that is used to end the program 

        while EndTask == ("NV"):
            if arduino.in_waiting:
                rawData = arduino.readline()
                EndTask = str(rawData.decode('utf'))

        # Receives and saves the line from the arduino that is used to log the time

        while LogTime == ("NV"):
            if arduino.in_waiting:
                rawData = arduino.readline()
                LogTime = str(rawData.decode('utf'))

        # Receives and saves the line from the arduino that is used to end each datatransmition

        while EndMesage == ("NV"):
            if arduino.in_waiting:
                rawData = arduino.readline()
                EndMesage = str(rawData.decode('utf'))


        if EndTask[0:5] == "Error":

            print("Wrong data sent")

        else:

            # The while loop reads and sorts the data sent through the USB port

            while True:

                # Receives one line of data from arduino

                if arduino.in_waiting:
                    rawData = arduino.readline()
                    Data = str(rawData.decode('utf'))

                # Ends the program and saves the data as a CSV file

                    if Data == EndTask:

                        datasets = {
                            "Time": time_list,
                            "Sensor ID": sensor_ID_list,
                            "ID 6 bit": ID_6_bit_list,
                            "Sensor data": data_list,
                            "Celsius": celsius_list
                        }

                        datasets_pd = pd.DataFrame(datasets)
                        print(datasets_pd)

                        datasets_pd.to_csv(filename)
                        
                        break

                # Logs the time of temperature measurement

                    elif Data == LogTime:

                        clock = datetime.datetime.now(timezone.utc).isoformat()

                # Starts next data transmition

                    elif Data == EndMesage:
                        count = 0


                # Writes data to the coresponding list in a spesiffic order

                    else:

                        Data = Data[0:-2]

                        if count == 0:

                            time_list.append(clock)
                            sensor_ID_list.append(Data[0:-1])

                        elif count == 1:

                            ID_6_bit_list.append(Data)

                        elif count == 2:

                            data_list.append(Data[0:-1])

                        elif count >= 3:

                            celsius_list.append(Data)

                        else:

                            print("Dataerror: Please try again")
                            break

                        count = count + 1
    
    # Saves the data as a CSV file if the user presses 'Ctrl + c'

    except KeyboardInterrupt:

        listlength = len(celsius_list)

        time_list = time_list[0:listlength]
        sensor_ID_list = sensor_ID_list[0:listlength]
        ID_6_bit_list = ID_6_bit_list[0:listlength]
        data_list = data_list[0:listlength]

        datasets = {
            "Time": time_list,
            "Sensor ID": sensor_ID_list,
            "ID 6 bit": ID_6_bit_list,
            "Sensor data": data_list,
            "Celsius": celsius_list
        }

        datasets_pd = pd.DataFrame(datasets)
        print(datasets_pd)

        datasets_pd.to_csv(filename)

        print("Program was ended before it finished")