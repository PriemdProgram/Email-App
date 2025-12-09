import sys
from graph import Graph
import configparser
import asyncio
import html
import datetime
import time
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

'''
Things I have left to do:

Tool bar for preferences (what folders to search from, where to save outputs, how much to fetch?)
getUser (make it return user again because currently it is not - due to it being completed before the last inbox call so it's not called [maybe a time.sleep() to slow it down])
UI design? (Potentially)

'''

selected = []
inbox = []
display = []
config = configparser.ConfigParser()
config.read(['config.cfg', 'config.dev.cfg'])
azure_settings = config['azure']

graph: Graph = Graph(azure_settings)


def clean_tags(text):
    # Remove HTML tags
    import re
    clean = re.compile('<.*?>')
    text.replace('&nbsp;','')
    text = re.sub(clean, '', text)
    return html.unescape(text)
    

def getUserSync(graph):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(getUser(graph))
    return result

async def getUser(graph):
    user = await graph.get_user()
    if user:
        print(f"Username: {user.display_name}")
        print(f"Email : {user.mail or user.user_principal_name}\n")
    
    return user

def listInboxSync(graph):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(list_inbox(graph))

async def list_inbox(graph: Graph, chooseBox):
    message_page = await graph.get_inbox(chooseBox)
    if message_page and message_page.value:
        # Output each message's details
        for message in message_page.value:
            curr = [message.from_.email_address, message.subject, message.body, message.received_date_time, message.to_recipients, message.cc_recipients, message.unique_body]
            inbox.append(curr)
        # If @odata.nextLink is present
        more_available = message_page.odata_next_link is not None
        print('\nMore messages available?', more_available, '\n')

class Email(QWidget):
    displayChanged = pyqtSignal(list)
    def __init__(self, sender, subject, content, date, to, cc, uniqueBody, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.subject = subject
        self.content = content
        self.date = date
        self.to = to
        self.cc = cc 
        self.uniqueBody = uniqueBody

        # Create checkbox for selection
        self.checkbox = QCheckBox()

        # Create button for email preview
        self.email_button = QPushButton(f"""Sender: {self.sender.name} ({self.sender.address})
Subject: {self.subject}
Date: {self.date}""")
        self.email_button.setFixedSize(500,150)
        self.email_button.setMinimumHeight(150)
        #self.email_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Layout to arrange checkbox and button horizontally
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.addWidget(self.email_button)
        layout.setContentsMargins(0, 0, 0, 0)  # Adjust padding
        self.setLayout(layout)

        self.email_button.clicked.connect(self.click)
        self.checkbox.clicked.connect(self.check)
    def check(self):
        state = self.checkbox.isChecked()

        if state == True:
            selected.append(self)
        else:
            if self in selected:
                selected.remove(self)

        print(selected)

    def click(self):
        display = [self.sender,self.subject,self.content,self.date,self.to,self.cc,self.uniqueBody]
        self.displayChanged.emit(display)


class DisplayWidget(QWidget):
    def __init__(self, sender, subject, content, date, to, cc, uniqueBody, parent=None):
        super().__init__(parent)
        self.sender = sender
        self.subject = subject
        self.content = content
        self.date = date
        self.to = to 
        self.cc = cc
        self.uniqueBody = uniqueBody

        container = QWidget()

        self.label1 = QTextBrowser()
        self.label1.setOpenExternalLinks(True)
        self.label1.setText("")
        self.label1.setMaximumHeight(150)

        self.label2 = QTextBrowser()
        self.label2.setText("")
        self.label2.setOpenExternalLinks(True)
        self.label2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.label2.setSizeAdjustPolicy(QTextBrowser.SizeAdjustPolicy.AdjustToContents)
        self.label2.setWordWrapMode(QTextOption.WrapMode.WordWrap)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.label2)

        layout = QVBoxLayout(container)
        layout.addWidget(self.label1)
        layout.addWidget(scroll)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def displayChanged(self, display):


        res = ""
        if len(display[5]) > 0:
            for i in range(len(display[5])):
                res += str(f"{display[5][i].email_address.name} ({display[5][0].email_address.address})")

        self.label1.setHtml(f"""<b>To</b>: {display[4][0].email_address.name} ({display[4][0].email_address.address}) <br>
<b>From</b>: {display[0].name} ({display[0].address})<br>
<b>Date</b>: {display[3]}<br>
<b>Subject</b>: {display[1]}<br>
<b>CC</b>: {res}""")

        if display[6]:
            self.label2.setHtml(str(display[6].content))
        else:
            self.label2.setHtml(str(display[6].content))

#listInboxSync(graph)
#user = getUserSync(graph)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1500, 810)
        
        self.setWindowTitle("Thread Compilation")
        
        horizontal = QHBoxLayout()
        self.email_display = DisplayWidget(None,None,None,None,None,None,None)
        self.email_display.setFixedSize(640,790)


        container = QWidget()
        vertical = QVBoxLayout(container)
        
        inbox.sort(key=lambda m: m[3],reverse=True)
        for m in inbox:
            self.button = Email(m[0],m[1],m[2],m[3],m[4],m[5],m[6])
            self.button.displayChanged.connect(self.email_display.displayChanged)
            vertical.addWidget(self.button)
            vertical.addStretch(30)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        scroll.setMinimumHeight(790)
        scroll.setFixedWidth(575)

        horizontal.addWidget(scroll)

        self.label2 = QPushButton()
        self.label2.setText("Compile Selected Emails")
        self.label2.clicked.connect(self.click)

        self.userLabel = QLabel()
        #self.userLabel.setText(f"{user[1].display_name}")
        self.userLabel.setText("Max Ricketts")

        horizontal.addWidget(self.label2)
        horizontal.addWidget(self.userLabel)

        horizontal.addWidget(self.email_display)

        horizontal.setContentsMargins(0,0,0,425)
        horizontal.setSpacing(20)
        horizontal.addStretch()

        widget = QWidget()
        widget.setLayout(horizontal)

        self.setCentralWidget(widget)
    def click(self):
        if not selected:
            print("None selected")
        else:
            name = str(datetime.datetime.now())
            name = name.replace('.',':')
            name = name.replace(':','-')
            f = open(f"{name}.txt",'x')
            f.close()
            selected.sort(key = lambda m:m.date)
            res = ""

            for email in selected:
                f = open(f"{name}.txt",'a')
                temp = f"\nTo:"
                for i in range(len(email.to)):
                    temp += f"{email.to[i].email_address.name} ({email.to[i].email_address.address}),"
                temp += "\nCC:"
                for i in range(len(email.cc)):
                    temp += f"{email.cc[i].email_address.name} ({email.cc[i].email_address.address})"
                temp += f"\nFrom: {email.sender.name} ({email.sender.address})"
                temp += f"\nSubject: {email.subject}"
                temp += f"\nDate: {email.date}"
                if email.uniqueBody:
                    text = str(email.uniqueBody.content)
                else:
                    text = str(email.body.content)
                text = clean_tags(text)
                temp += text
                temp += "----------------------------------------------------------------------------------------------"
                f.write(temp)
                f.close()

app = QApplication(sys.argv)
'''
sign = SignUp(graph.user_code, graph.verification_url)
sign.show()
app.exec()
'''

async def collection(graph):
    results = await asyncio.gather(
        list_inbox(graph, 'inbox'),
        list_inbox(graph, 'sentitems'),
        getUser(graph)
    )
    return results

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
user = loop.run_until_complete(collection(graph))

window = MainWindow()
window.show()
app.exec()


'''
Things I have left to do:

Tool bar for preferences (what folders to search from, where to save outputs, how much to fetch?)
getUser (make it return user again because currently it is not - due to it being completed before the last inbox call so it's not called [maybe a time.sleep() to slow it down])
UI design? (Potentially)

'''