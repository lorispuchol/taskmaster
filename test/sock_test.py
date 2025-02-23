import socket, time

test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
test.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
test.bind(("0.0.0.0", 55557))
while True:
    time.sleep(1)