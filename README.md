# tachyon-lang
next generation ion
```
/*
 * hello this is tachyon
 * it is wonderful to be here
 * this is a comment
 * the stars at the end of the line are unnecesary
 * they are prefered
 */

someInt = 10
varriable = 'easy'
print('you already get it')

/*
 * so lets say you want to write a fuction
 * its easy, just set how you want to see it to what you want to execute
 * you'll see
 */

double(number) = number * 2

/*
 * what about non default arguments
 * they can be expressions
 */

factorial(number) = factorial(number-1)*number
factorial(1) = 1

/*
 * this could be factorial(4 - 3) = 1
 * the python vm doesnt optimize tail recursion
 * so thats why factorial fails above 900
 * this is where while, loop, and if comes in
 * to exit a loop just return
 * to return just type the expression
 * it will auto return
 */

factorialInf(x) = {
  return = 1
  while x > 0{
    return *= x
    x -= 1
  }
  return
}

/* macros
 * macros = functions - optional args - expresion args + unevaluation + excamation point
 */

factorialMacro!(x) = {
  factorialInf(x)
}

/*
 * a backslash before a newline is compeltely ignored
 * now for some fun with the emoji vars
 * did i mention varriable names can include any nondefinded unicode charactor
 */

😀 = 'happy'
🚀 = ' '
💻 = 'programming'
🖨(📄) = print(📄)
🖨(😀+🚀+💻)
```
