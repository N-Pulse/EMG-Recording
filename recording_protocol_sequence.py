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

def record_data(file_path, duration=3):
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
        time.sleep(1)
        ser.flushInput()
        
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Sensor Data"])  # Modify headers as needed
            
            print("Waiting for first valid data...")
            first_data = None
            while first_data is None:
                raw_data = ser.readline().decode('utf-8').strip()
                if raw_data.isdigit():  # Ensure it's valid numeric data
                    first_data = int(raw_data)

            start_time = time.time()

            while time.time() - start_time < duration:
                current_time = round(time.time() - start_time, 3)
                data = ser.readline().decode('utf-8').strip()
                if data:
                    #print(f"Receieved: {data}")
                    writer.writerow([current_time, data])
                else:
                    print("No data received.")
        
        ser.close()
    except serial.SerialException as e:
        print(f"Error: {e}")
        return

def countdown(n=3):
    for i in range(n, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)

def run_sequence(sequence, base_folder, participant, hand, position):
    timestamp = datetime.now().strftime("%y%m%d%H%M%S")
    input(f"Press ENTER to start sequence...")
    countdown()
    for action in sequence:
        print(f"Perform '{action}'")
        countdown()
        
        # Format filename based on naming convention
        filename = f"{participant}_{hand}_{position}_{action}_{timestamp}.csv"
        filepath = os.path.join(base_folder, filename)
        record_data(filepath)
        print(f"Recorded '{action}' successfully!\n")

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
position = input("Enter position (1-5): ")

# Create necessary folders
base_folder = os.path.join(os.getcwd(), "EMG_recording/data")
# base_folder = os.path.join(os.getcwd(), participant, hand, position)
create_folder(base_folder)

# Choose sequence
print("Select sequence to run:")
print("1 - Single DOF Movements")
print("2 - Hand Poses")
print("3 - Grasps")
sequence_choice = int(input("Enter sequence number (1-3): "))

if sequence_choice == 1:
    run_sequence(sequence_1, base_folder, participant, hand, position)
elif sequence_choice == 2:
    run_sequence(sequence_2, base_folder, participant, hand, position)
elif sequence_choice == 3:
    run_sequence(sequence_3, base_folder, participant, hand, position)
else:
    print("Invalid choice.")

print("Data recording complete!")
