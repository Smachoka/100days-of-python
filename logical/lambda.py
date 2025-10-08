def defensive_calculator():
    try:
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        operation = input("Enter operation (+, -, *, /): ")
        
        if operation == '+':
            result = num1 + num2
        elif operation == '-':
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        elif operation == '/':
            result = num1 / num2
        else:
            raise ValueError("Invalid operation")  # Intentionally cause an exception!
            
    except ValueError as e:
        print(f"Input error: {e}")
    except ZeroDivisionError:
        print("Cannot divide by zero!")
    else:
        print(f"Result: {result}")