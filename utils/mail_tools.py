import imaplib
import email
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')  
load_dotenv(dotenv_path)

imap_server="imap.gmail.com"
email_id=os.getenv('email_address')
password=os.getenv('email_password')

def get_email_body(msg):
    ans=[]
    for part in msg.walk():
        if part.get_content_type()=='text/plain':
            ans.append(part.get_payload(decode=True).decode())
    return ans


def get_emails(n):
    imap=imaplib.IMAP4_SSL(imap_server)

    imap.login(email_id,password)


    imap.select("inbox")

    status,messages=imap.search(None,'ALL')
    email_ids=messages[0].split()

    primary_emails=[]

    for id in email_ids[-n:]:
        status,data=imap.fetch(id,"(RFC822)")
        
        raw_email=data[0][1]
        
        msg=email.message_from_bytes(raw_email)
        
        primary_emails.append({
            
            "from":msg["from"],
            "date":msg["date"],
            "subject":msg["subject"],
            "body":get_email_body(msg)
        })
        
    imap.close()
    imap.logout()
    return(primary_emails)