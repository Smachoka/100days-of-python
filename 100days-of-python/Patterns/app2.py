def pattern(number):

    for index in range ( number, -1, -1):
        for space_count in range(0, index + 1):
         print("* ", end="")
        print()
    
pattern(5)        