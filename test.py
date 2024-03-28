test = [
    {
        "test": ''
    },
    {
        "test": ''
    },
    {
        "test": ''
    },
    {
        "test": ''
    },
    {
        "test": ''
    },
]


def check_genres(list):
    counter = 0
    for item in list:
        if "key" not in item.keys():
            counter += 1
    return counter


print(test)
counter = 0
while check_genres(test) != 0:
    for i, item in enumerate(test):
        if "key" not in item.keys():
            if counter == 0:
                if i == 1:
                    continue
            item["key"] = "key"
    counter += 1
    print(test)
