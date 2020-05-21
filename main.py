import argparse
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from time import strftime
import sys
import pandas as pd
from pandas import json_normalize
import smtplib, email, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from email.mime.application import MIMEApplication

JIRA_API_TOKEN='<API TOKEN>'
JIRA_API_USERNAME='<API TOKEN OWNER USERNAME>'
SEARCH_URL = 'https://<SITE-URL>/rest/api/2/search'
# Jira Cloud API V2 ref: https://developer.atlassian.com/cloud/jira/platform/rest/v2/

parser = argparse.ArgumentParser(description="Collect Jira faults and export to CSV")
parser.add_argument("customer", type=str, help="Customer name (as in Jira)")
parser.add_argument("description", type=str, help="Description LIKE <var>")
parser.add_argument("smtp_server", type=str, help="SMTP server address/hostname")
parser.add_argument("port", type=int, help="SMTP port")
parser.add_argument("recipient", type=str, help="Report recipient email address")
parser.add_argument("sender", type=str, help="Send from address")
args = parser.parse_args()

# Set SMTP vars from arg values
smtpServer = args.smtp_server
port = args.port
recipient = args.recipient
sender = args.sender

# Define parameters for API search
# paramstring1 must be in JQL format, see Atlassian ref for syntax: https://support.atlassian.com/jira-service-desk-cloud/docs/use-advanced-search-with-jira-query-language-jql/
# paramstring2 lists field names desired for return
paramstring1 = "project = EXAMPLE AND Organizations="+args.customer+" AND created >= -7d AND Description ~ "+args.description
paramstring2 = "key,status,summary,description,creator,created,updated"

# Define parameter string for requests.get
searchParams = {'jql':paramstring1,'fields':paramstring2}

#get tenant detail JSON
searchResponse = requests.get(SEARCH_URL, params=searchParams, auth=(JIRA_API_USERNAME, JIRA_API_TOKEN))

# Graceful shut down if API call fails with status code info
if searchResponse.status_code != 200:
    print("Tenants API call not successful", file=sys.stderr)
    print(searchResponse.status_code, file=sys.stderr)
    sys.exit(1)

# Parse JSON response
searchResults = searchResponse.json()
#print(searchResults)

# Results returned may be zero
# If so, send email stating as such to distinguish from case where report failed to generate/send
if searchResults['total'] == 0:
    #TODO: Encapsulate sendmail in function

    # Build a subject string and body
    subject = "Jira Issues Report: " + args.customer + " " + args.description
    body = "No Jira Issues created in the last 7 days for " + args.customer + " with search term: " + args.description

    # So, no header?
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject

    # add body as defined above
    message.attach(MIMEText(body, "plain"))
    # define server, send mail, catch exceptions, close SMTP session
    server = smtplib.SMTP(smtpServer,port)
    #Uncomment line below to increase smtp debug level for testing/troubleshooting sendmail
    #server.set_debuglevel(1)
    try:
        server.sendmail(sender, recipient, message.as_string())
    except:
        print("Email send failed", file=sys.stderr)
        server.close()
        sys.exit(1)
    server.close()
    sys.exit(0)

# Normalize JSON, delete unecessary columns
searchResults = json_normalize(searchResults['issues'])
if 'id' in searchResults:
    del searchResults['id']
if 'expand' in searchResults:
    del searchResults['expand']
if 'self' in searchResults:
    del searchResults['self']
if 'fields.status.self' in searchResults:
    del searchResults['fields.status.self']
if 'fields.status.description' in searchResults:
    del searchResults['fields.status.description']
if 'fields.status.iconUrl' in searchResults:
    del searchResults['fields.status.iconUrl']
if 'fields.status.id' in searchResults:
    del searchResults['fields.status.id']
if 'fields.status.statusCategory.self' in searchResults:
    del searchResults['fields.status.statusCategory.self']
if 'fields.status.statusCategory.id' in searchResults:    
    del searchResults['fields.status.statusCategory.id']
if 'fields.status.statusCategory.key' in searchResults:    
    del searchResults['fields.status.statusCategory.key']
if 'fields.status.statusCategory.colorName' in searchResults:
    del searchResults['fields.status.statusCategory.colorName']
if 'fields.status.statusCategory.name' in searchResults:
    del searchResults['fields.status.statusCategory.name']
if 'fields.creator.self' in searchResults:
    del searchResults['fields.creator.self']
if 'fields.creator.accountId' in searchResults:
    del searchResults['fields.creator.accountId']
if 'fields.creator.avatarUrls.48x48' in searchResults:
    del searchResults['fields.creator.avatarUrls.48x48']
if 'fields.creator.avatarUrls.32x32' in searchResults:
    del searchResults['fields.creator.avatarUrls.32x32']
if 'fields.creator.avatarUrls.24x24' in searchResults:
    del searchResults['fields.creator.avatarUrls.24x24']
if 'fields.creator.avatarUrls.16x16' in searchResults:
    del searchResults['fields.creator.avatarUrls.16x16']
if 'fields.creator.active' in searchResults:
    del searchResults['fields.creator.active']
if 'fields.creator.timeZone' in searchResults:
    del searchResults['fields.creator.timeZone']
if 'fields.creator.accountType' in searchResults:
    del searchResults['fields.creator.accountType']

#Rename and reorder columns
searchResults.rename(columns={'key':'Ticket Number','fields.summary':'Summary','fields.creator.emailAddress':'Creator Email','fields.creator.displayName':'Creator Name','fields.created':'Created Time','fields.description':'Description','fields.updated':'Updated Time','fields.status.name':'Status'}, inplace=True)
newIndex = ['Ticket Number','Status','Summary','Description','Created Time','Updated Time','Creator Name','Creator Email']
searchResults = searchResults[newIndex]

#Generate filename and export CSV
now = datetime.now()
now = now.strftime('%Y.%m.%d_%H.%M')
outputFileName = args.description + "." + now +'.csv'
searchResults.to_csv(outputFileName,index=False)

# Build a subject string and body
subject = "Jira Issues Report: " + args.customer + " " + args.description
body = "Jira Issues created in the last 7 days for " + args.customer + " and search term: " + args.description

# So, no header?
message = MIMEMultipart()
message["From"] = sender
message["To"] = recipient
message["Subject"] = subject

# add body as defined above
message.attach(MIMEText(body, "plain"))

# Read CSV and add ass attachment
filename = outputFileName
with open(filename, "rb") as fil:
    part = MIMEApplication(fil.read(),Name=basename(filename))
part['Content-Disposition'] = 'attachment; filename="%s"' % basename(filename)
message.attach(part)


# define server, send mail, catch exceptions, close SMTP session
server = smtplib.SMTP(smtpServer,port)
#Uncomment line below to increase smtp debug level for testing/troubleshooting sendmail
#server.set_debuglevel(1)
try:
    server.sendmail(sender, recipient, message.as_string())
except:
    print("Email send failed", file=sys.stderr)
    server.close()
    sys.exit(1)
server.close()