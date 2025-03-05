# CS 262 - Logical Clocks
This repository contains the code for Design Exercise 3: Logical Clocks for Harvard's CS 2620: Distributed Programming class. You can access the design document and engineering notebook [here](https://docs.google.com/document/d/1vJeS7PuXCz1lkp-FrzXvrbb7IFf1vcbZgZWthI5IdKU/edit?usp=sharing). Our Logical Clocks program supports the following features and operates on the following contingencies: 
- Three virtual machine simulations each running their own logical clock on a different port/process with a different randomized tick rate of processing (randomly selected from the range 1 through 6)
- Each virtual machine uses a server socket and client sockets that try to connect to receive and send messages to one another. We the string byte decode and encode to pass data over the wire
- On each clock cycle, if there is a message in the message queue for the machine, the virtual machine should take one message off the queue, update the local logical clock, and write in the log that it received a message, the global time, the length of the message queue, and the logical clock time.
- If there is no message in the queue, the virtual machine should generate a random number in the range of 1-10, and
  - if the value is 1, send to one of the other machines a message that is the local logical clock time, update it’s own logical clock, and update the log with the send, the system time, and the logical clock tim
  - if the value is 2, send to the other virtual machine a message that is the local logical clock time, update it’s own logical clock, and update the log with the send, the system time, and the logical clock time.
  - if the value is 3, send to both of the other virtual machines a message that is the logical clock time, update it’s own logical clock, and update the log with the send, the system time, and the logical clock time.
  - if the value is other than 1-3, treat the cycle as an internal event; update the local logical clock, and log the internal event, the system time, and the logical clock value.
 
## Set Up 
Clone our repository first 
```
git clone https://github.com/mxiang04/CS-262-Clocks.git
```
Install the necessary dependencies. Most of the dependencies and packages that we use are inherent to the system and should have already been downloaded, but if you are receiving import errors, you should check the `clocks.py` folder to see which packages we utilize. 

You can now run our app! In the terminal, type in 
```
python clocks.py
```
You will then see the logs generate not only in the terminal but in the `logs` folder on the side, separated by date of run and then by each machine. 

## Architecture 
`clocks.py` - where the bulk of our program lies and where the virtual machines are instantiated and run 
`constants.py` - houses the host and ports we use to run our virtual machines 
`test.py` - our tests for this program 
`utils.py` - setting up utilities such as logging, creating the necessary log folders, etc. 
