import sys
import pandas as pd
import matplotlib.pyplot as plt

# Reads the filedirectories from comandline in terminal

if len(sys.argv) == 3:

    filename = str(sys.argv[1])
    refFilename = str(sys.argv[2])

# Reads the filedirectories from user in terminal

else:

    
    filename = input("Enter full file directory: ")
    refFilename = input("Enter file directory for referance file: ")

# Reads the referance CSV file, and separates the different columnes into series

try:

    file =  pd.read_csv(filename)
    refFile = pd.read_csv(refFilename, skiprows=26)

    refcelsius = refFile['Channel 1']
    reftime = refFile['Date and Time']
    reftime = pd.to_datetime(reftime, format="%d/%m/%Y %H:%M:%S")
    reftime = reftime.dt.tz_localize(tz = 'UTC')
    
except:

    print("Coud not read from file")

else:

    # Reads and saves sensor IDs from the sensor file

    address_list = []
    address_6_list = []

    firstID = (file.loc[0, 'Sensor ID'])
    address_list.append(firstID)

    firstID_6 = (file.loc[0, 'ID 6 bit'])
    address_6_list.append(firstID_6)

    x = 1

    while x < len(file):

        address = (file.loc[x, 'Sensor ID'])
        address_6 = (file.loc[x, 'ID 6 bit'])

        if address == firstID:
            break

        else:
            address_list.append(address)
            address_6_list.append(address_6)
            x = x + 1


    # Reads the sensor file with Sensor ID as an index

    file =  pd.read_csv(filename, index_col = "Sensor ID")

    celsius_matrix = []
    time_matrix = []

    offset_list = []
    offset_matrix = []

    offset_average = []

    # Reads all temperatures and timestamps, and saves them in separate matrixes

    for ID in address_list:

        temporary_list = file.loc[ID]
        celsius_list = temporary_list['Celsius']
        time_list = pd.to_datetime(temporary_list['Time'])

        celsius_matrix.append(celsius_list.copy())
        time_matrix.append(time_list.copy())

    # Calculates the difference between the refferance temperatures and the sensor temperatures for each refferance measurement 

    for ID in range(len(address_list)):

        offset_sum = 0

        for x in range(len(reftime)):

            for y in range(len(time_matrix[ID])):

                if time_matrix[ID][y] >= reftime[x]:

                    offset = float(refcelsius[x]) - float(celsius_matrix[ID][y])
                    offset_list.append(offset)

                    offset_sum = offset_sum + offset

                    empty = 0
                    break
                else:
                    empty = 1
            
            # Adds a 0 to the offset list for each refferance temperature that does not have a corresponding sensor temperature

            if empty:
                offset_list.append(0)

        # Saves all the calculated values in separate matrixes and lists

        offset_average.append(offset_sum / len(offset_list))

        offset_list.append("Average")
        offset_list.append(offset_average[ID])

        offset_matrix.append(offset_list.copy())
        offset_list.clear()

    reftime.loc[len(reftime.index)] = ""
    reftime.loc[len(reftime.index)] = ""

    # Saves all offset values ass a CSV file.

    datasets = pd.DataFrame({
        "Time": reftime
    })

    for i in range(len(offset_matrix)):

        column_x = "Offset: " + str(address_list[i]) + " (" + str(address_6_list[i]) + ")"

        datasets[column_x,] = offset_matrix[i]

    print(datasets)

    filename = "Offsetfile"
    for ID in address_6_list:
        filename = filename + "_" + str(ID)
    filename = filename + ".csv"

    datasets.to_csv(filename)

    
    # Plots the different datasets 

    try: 

        plt.figure()
        
        for x in range(len(celsius_matrix)):

            plt.plot(time_matrix[x], celsius_matrix[x], label = address_6_list[x])

        plt.plot(reftime[0:-2], refcelsius, label = "Ref")

        plt.legend()
        plt.xticks(rotation=45)
        
        plt.xlabel("Time")
        plt.ylabel("Temperature (C)")
        plt.title("Temperature / Time")
        
        plt.show()


        plt.figure()

        for x in range(len(offset_matrix)):

            plt.hist(offset_matrix[x][0:-2], label = address_6_list[x])

        plt.legend()

        plt.xlabel("Offset")
        plt.ylabel("Number of values")
        plt.title("Number of offsetvalues")

        plt.show()


        plt.figure()

        for x in range(len(offset_matrix)):

            plt.plot(reftime[0:-2], offset_matrix[x][0:-2], label = address_6_list[x])

        plt.legend()
        plt.xticks(rotation=45)

        plt.xlabel("Time")
        plt.ylabel("Offsettemperature")
        plt.title("Offset / Time")

        plt.show()

    except KeyboardInterrupt:

        print("\nEnding program. Plots deleted\n")
