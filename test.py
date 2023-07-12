message = 'exchange'


if message == 'exchange':
    print(1)
elif message.split()[0] == 'exchange' and 0 < message.split()[1] <= 10:
    print(2)
else:
    print(3)

