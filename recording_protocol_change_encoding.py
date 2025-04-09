import os
import time
import csv
import serial
import pandas as pd
from datetime import datetime

# Setup serial connection (Modify COM port as needed)
SERIAL_PORT = "COM4"  # Change this for your system
BAUD_RATE = 115200

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def record_data(sequence, file_path, duration=3, transition_time=3):
    try:
        # filename = f"{participant}_{hand}_{position}_{sequence}_{timestamp}.csv"
        # file_path = os.path.join(base_folder, filename)

        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
        time.sleep(1)
        ser.flushInput()

        print(f"You will keep each position during {duration} seconds.")
        time.sleep(3)
        print(f"You will have {transition_time} seconds to change position.")
        time.sleep(3)
        print(f"It is enough time, don't rush...")
        time.sleep(3)
        input(f"Press ENTER to start sequence...")
        countdown()
        
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Channel1", "Channel2", "Action1", "Action2"])  # Modify headers as needed
            
            print("Waiting for first valid data...")
            first_data = None
            while first_data is None:
                raw_data = ser.readline().decode('utf-8').strip()
                print(raw_data)
                channel1, channel2 = float(raw_data.split(" ")[0]), float(raw_data.split(" ")[1])
                if isinstance(channel1, float) and isinstance(channel2, float):  # Ensure it's valid numeric data
                    first_data = [channel1, channel2]

            start_sequence_time = time.time()

            for i in range(len(sequence)):
                print(f"Perform '{sequence[i]}'")

                start_action_time = time.time()

                # Pose recording
                while time.time() - start_action_time < duration:
                    current_time = round(time.time() - start_sequence_time, 3)
                    data = ser.readline().decode('utf-8').strip()
                    channel1, channel2 = float(data.split(" ")[0]), float(data.split(" ")[1])
                    if data:
                        writer.writerow([current_time, channel1, channel2, sequence[i], None])
                    else:
                        print("No data received.")
                
                if i == len(sequence) - 1:
                    break

                # Transition zone
                print(f"Transitioning to '{sequence[i+1]}'")

                while time.time() - start_action_time < duration + transition_time:
                    current_time = round(time.time() - start_sequence_time, 3)
                    data = ser.readline().decode('utf-8').strip()
                    channel1, channel2 = float(data.split(" ")[0]), float(data.split(" ")[1])
                    if data:
                        writer.writerow([current_time, channel1, channel2, sequence[i], sequence[i+1]])
                    else:
                        print("No data received.")
        
        ser.close()

        print(f"Data recorded successfully to '{file_path}'")

    except serial.SerialException as e:
        print(f"Error: {e}")
        return

def countdown(n=3):
    for i in range(n, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)

# def run_sequence(sequence, base_folder, participant, hand, position):
#     timestamp = datetime.now().strftime("%y%m%d%H%M%S")
#     input(f"Press ENTER to start sequence...")
#     countdown()
#     for action in sequence:
#         print(f"Perform '{action}'")
#         countdown()
        
#         # Format filename based on naming convention
#         filename = f"{participant}_{hand}_{position}_{action}_{timestamp}.csv"
#         filepath = os.path.join(base_folder, filename)
#         record_data(filepath)
#         print(f"Recorded '{action}' successfully!\n")



duration=3
transition_time=3

# Load Excel file with sequences
file_path = "EMG_recording_protocol.xlsx"
xls = pd.ExcelFile(file_path)
df_sequences = pd.read_excel(xls, sheet_name="Sequences")

# Extract sequences
sequence_1 = df_sequences.iloc[:, 0].dropna().tolist()
sequence_2 = df_sequences.iloc[:, 1].dropna().tolist()
sequence_3 = df_sequences.iloc[:, 2].dropna().tolist()

# User inputs
participant = input("Enter participant initials: ")
hand = input("Enter which hand (L or R): ").upper()
# position = input("Enter position (1-5): ")

# Create necessary folders
base_folder = os.path.join(os.getcwd(), "data")
# base_folder = os.path.join(os.getcwd(), participant, hand, position)
create_folder(base_folder)

# Choose sequence
print("Select sequence to run:")
print("1 - Single DOF Movements")
print("2 - Hand Poses")
print("3 - Grasps")
sequence_choice = int(input("Enter sequence number (1-3): "))

timestamp = datetime.now().strftime("%y%m%d%H%M%S")
filename = f"{participant}_{hand}_{sequence_choice}_{timestamp}.csv"
file_path = os.path.join(base_folder, filename)

if sequence_choice == 1:
    record_data(sequence_1, file_path, duration, transition_time)
    # run_sequence(sequence_1, base_folder, participant, hand, position)
elif sequence_choice == 2:
    record_data(sequence_2, file_path, duration, transition_time)
    # run_sequence(sequence_2, base_folder, participant, hand, position)
elif sequence_choice == 3:
    record_data(sequence_3, file_path, duration, transition_time)
    # run_sequence(sequence_3, base_folder, participant, hand, position)
else:
    print("Invalid choice.")
