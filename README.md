# Email-App
An email app utilising Azure to solve a usability issue with existing email clients. 

The email client is built in Python, using PyQt6 for the GUI, rather than Tkinter, due to it's responsiveness. 

Fetching is done through connecting to the Microsoft REST API. Authentication is done through OAuth and Token Flow. Some quality of life settings are missing. 
The main use is to compile various different email threads onto one file, improving the current email client's process to do this. 
