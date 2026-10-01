import serial

# ✅ Apna correct port yahan set hai (macOS)
PORT = '/dev/cu.usbserial-0001'   # agar change ho to update kar lena
BAUD = 115200                    # ESP32 ke baudrate ke mutabiq

ser = serial.Serial(PORT, BAUD, timeout=1)

print("Listening to ESP32...")

while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        # ✅ sirf valid framed data process hoga
        if line.startswith('*') and line.endswith('*'):

            # remove * from start/end
            data = line[1:-1]

            # split and convert to int
            temps = [int(x) for x in data.split(',')]

            print("Received:", temps)

    except Exception as e:
        print("Error:", e)