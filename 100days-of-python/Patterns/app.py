def pattern(number):
    
    spaces_before_asterisks = 2 * number - 2

    for index in range(0, number):
        for space_count in range(0, spaces_before_asterisks):
            print(end=" ")

        spaces_before_asterisks = spaces_before_asterisks - 1
        for space_count in range(0, index + 1):
            print("* ", end="")
        print("\r")

    spaces_before_asterisks = number - 2

    for index in range(number, -1, -1):
        for space_count in range(spaces_before_asterisks, 0, -1):
            print(end=" ")

        spaces_before_asterisks = spaces_before_asterisks + 1

        for space_count in range(0, index + 1):
            print("* ", end="")
        print("\r")

pattern(5)
