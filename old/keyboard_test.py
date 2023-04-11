from pynput.keyboard import Key, Listener


global state = 0
def on_press(key):
    print('{0} pressed'.format(
        key))
    # return False

def on_release(key):
    print('{0} release'.format(
        key))
    print(key)
    if key == Key.enter:
        print("heyo")
        state = state + 1
        return False
    if key == Key.esc:
        state = -1
        return False

#nonblocking version
listener = Listener( on_press=on_press, on_release=on_release)
listener.start()

print ("hhhhh")
# state = 0
# Collect events until released
while True:
    # with Listener(on_press=on_press, on_release=on_release) as listener:
    #     listener.join()
    if state == 1:
        print("hello")
    elif state == 2:
        print("bye")
    elif state == 3:
        state = 0
    elif state == -1:
        print("exit")
