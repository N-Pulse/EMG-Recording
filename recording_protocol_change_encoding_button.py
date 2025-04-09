import os
import time
import csv
import serial
import pandas as pd
import keyboard
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
        time.sleep(1)
        print(f"You will have to press the space while you change position.")
        time.sleep(1)
        print(f"It is enough time, don't rush...")
        time.sleep(1)
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

            for i in range(len(sequence) - 1):
                print(f"Recording '{sequence[i]}'")
                start_action_time = time.time()
                prompted = False
                transition_started = False

                while True:
                    current_time = round(time.time() - start_sequence_time, 3)
                    data = ser.readline().decode('utf-8').strip()

                    if not data:
                        continue

                    try:
                        channel1, channel2 = float(data.split(" ")[0]), float(data.split(" ")[1])
                    except ValueError:
                        continue

                    # Prompt for transition after 2 seconds
                    if not prompted and time.time() - start_action_time > 2:
                        print(f"Press and hold SPACE to transition to '{sequence[i+1]}'...")
                        prompted = True

                    # Read spacebar state
                    if keyboard.is_pressed('space'):
                        transition_started = True
                        writer.writerow([current_time, channel1, channel2, sequence[i], sequence[i+1]])
                    else:
                        writer.writerow([current_time, channel1, channel2, sequence[i], None])
                        if transition_started:
                            print(f"Transition complete. Starting '{sequence[i+1]}'\n")
                            break
        
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
sequence_4 = df_sequences.iloc[:, 3].dropna().tolist()

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
print("4 - Simple Gestures")
sequence_choice = int(input("Enter sequence number (1-4): "))

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
elif sequence_choice == 4:
    record_data(sequence_4, file_path, duration, transition_time)
    # run_sequence(sequence_4, base_folder, participant, hand, position)
else:
    print("Invalid choice.")
