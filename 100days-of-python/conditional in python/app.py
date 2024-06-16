secret_guess = 9
gues_count = 0
guess_limit = 3
while gues_count < guess_limit:
    guess = int(input("Guess a number: "))
    gues_count += 1
    if guess == secret_guess:
        print("you won")
        break
    else:
        print("you lost")
    