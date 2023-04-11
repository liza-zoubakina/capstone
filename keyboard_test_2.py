import keyboard

state = 0
while True:
    if keyboard.read_key()=="a":
        state= state +1

    print(state)
    if state == 5:
        state = 0
