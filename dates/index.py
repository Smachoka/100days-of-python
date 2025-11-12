with open("demo.txt","w") as f:
 f.write("Hello World!" )
with open("demo.txt","r") as f:
 content=f.read()
print(content)
