from pynput import keyboard

barcode_data = ""

def on_press(key):
    global barcode_data

    try:
        # Check if the key is a printable character
        if key.char:
            barcode_data += key.char
    except AttributeError:
        # Check if the key is Enter (newline)
        if key == keyboard.Key.enter:
            print(f"Scanned Barcode: {barcode_data}")
            barcode_data = ""

# Create a keyboard listener
listener = keyboard.Listener(on_press=on_press)

# Start the listener
listener.start()

# Keep the program running
listener.join()
