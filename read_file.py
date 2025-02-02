with open('stats.txt', 'r', encoding="UTF-8") as file:
    data = file.read()
    data = data.split("]")
    print(data[0])
    