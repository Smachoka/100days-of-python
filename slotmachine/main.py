def deposit():
    while True:
        amount =  input("what amount would you like to deposit? Ksh ")
        if amount.isdigit():
            amount =int(amount)
            if amount >0:
                break
            else:
                print("amount must be greater than 0")
        else:
            print("please enter a valid amount")
    return amount
deposit()
        