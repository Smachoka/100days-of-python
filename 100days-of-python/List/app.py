fruit = ["banana",  "cherry", "kiwi", "mango"]
print(len(fruit))
print(fruit[1]) # accessing list
if "kiwi" in fruit:
    print("yes kiwi exist") # checking if item exist
    # fruit[1] = "watermelon" #changing item
    print(fruit)
fruit.append("oranges") # adding elements
print(fruit)