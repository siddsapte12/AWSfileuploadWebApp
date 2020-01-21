import json
import sys
import logging
import rds_config
from rds_config import checkDBconn 
import pymysql
import collections
import boto3
import base64
def lambda_handler(event, context):
    
    print(event)
 
    if((event['path'] == "/login") and (event['httpMethod'] == "POST")):
        userObject = json.loads(event['body'])
        print(userObject['Username'])
        print(userObject['Password'])
        return loginUser(userObject['Username'],userObject['Password'])
    elif((event['path'] == "/register") and (event['httpMethod'] == "POST")):
        userObject = json.loads(event['body'])
        return register(userObject)
    elif((event['path'] == "/plan") and (event['httpMethod'] == "POST")):
        userObject = json.loads(event['body'])
        print(userObject['username'])
        return planSelect(userObject)
    elif((event['path']=="/upload") and (event['httpMethod']=="POST")):
        return upload(event,context)
  
    
def checkUserFromDatabase(username):
    ## Query database with username and password
    conn = checkDBconn()
    cursor = conn.cursor()
    #user = event['body'].Username
    print(cursor)
    val = cursor.execute("SELECT user_name from users where user_name = '"+username+"'") 
    cursor.close()
    conn.close()
    print(val)
    if  val == 1:
        return True;    
        
    else:
        return False;
    


def register(userObject):
    """
    This function inserts content into mysql RDS instance
    """
    conn = checkDBconn()
    cursor = conn.cursor()
    
  
    item_count = 0
    username=userObject['username']
    email=userObject['email']
    password=userObject['password']
    
    print("username", username+email+password)
    status = checkUserFromDatabase(username)
    print(status)
    if(status):
        d = collections.OrderedDict()
        d['statusMessage'] = "User Exists"
        d['statusCode'] = 500
        return   {
        'statusCode': 500,
        'headers': {
        'Content-Type': 'application/json',
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(d)
        }
    else:
        val = cursor.execute("insert into users (user_name, email, pwd) values( '"+username+"','"+email+"','"+password+"')")
        print("affected rows = {}".format(cursor.rowcount))
        
        # Get the primary key value of the last inserted row
        print("Primary key id of the last inserted row:")
        print(cursor.lastrowid)

        print("val::",val)
    
        cursor.close()
        conn.close()
        if val == 1:
            d = collections.OrderedDict()
            d['statusMessage'] = "Success"
            d['statusCode'] = 200
            
            return {
            'statusCode': 200,
            'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            'Content-Type': 'application/json',
            "Set-Cookie":"succes",
            "set-Cookie":"succeeded"
            },
            'body': json.dumps(d)
            }
        
        else:
            d = collections.OrderedDict()
            d['statusMessage'] = "User Exists"
            d['statusCode'] = 500
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                'body': json.dumps(d)
            }
        
def loginUser(username, password):
    conn = checkDBconn()
    cursor = conn.cursor()
    #user = event['body'].Username
    val = cursor.execute("SELECT user_name from users where user_name = '"+username+"' and pwd = '"+password+"'") 
    sqlStmt = "SELECT userid,user_name,email,plan_select from users where user_name = '"+username+"'"
    rows = cursor.execute(sqlStmt)
    usr = cursor.fetchall() 
    print(usr)
    cursor.close()
    conn.close()
    
    if  val == 1:
        
        objects_list = []
        for row in usr:
            print(row)
            d = collections.OrderedDict()
            d['userid'] = row[0]
            d['user_name'] = row[1]
            d['email'] = row[2]
            d['plan_select'] = row[3]
            objects_list.append(d)
        j = json.dumps(objects_list)

        
        return {
        'statusCode': 200,
        'headers': {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        'Content-Type': 'application/json',
        "Set-Cookie":"HttpOnly;Secure;SameSite=Strict",
        "set-Cookie":"HttpOnly;Secure;SameSite=Strict"
        },
        'body': json.dumps(objects_list)
        }
        
    else:
        return {
        'statusCode': 401,
        'headers': {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps("Invalid login credentials")
        }
  
def planSelect(userObject):
    conn = checkDBconn()
    cursor = conn.cursor()
    
    cardname = userObject['cardname']
    amount = userObject['amount']
    plan = userObject['plan']
    image = userObject['image']
    username = userObject['username']
    sqlStmt = "SELECT userid,user_name,email,plan_select,up_plan_id from users where user_name = '"+username+"'"
    rows = cursor.execute(sqlStmt)
    usr = cursor.fetchall() 
    print(usr)
        
    if  rows == 1:
        sqlStmt="UPDATE users SET up_plan_id='"+plan+"',plan_select=1,up_remainder='"+image+"'WHERE user_name = '"+username+"'";
        cursor.execute(sqlStmt)
        cursor.close()
        conn.close()
        return {
        'statusCode': 200,
        'headers': {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,filename",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        'Content-Type': 'application/json',
        "Set-Cookie":"HttpOnly;Secure;SameSite=Strict",
        "set-Cookie":"HttpOnly;Secure;SameSite=Strict"
        },
        'body': json.dumps("updated")
        }
    else:
        cursor.close()
        conn.close()
        return {
        'statusCode': 401,
        'headers': {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps("not updated")
        }

def upload(event, context):
    conn = checkDBconn()
    cursor = conn.cursor()
    
    BUCKET_NAME = '<bucketname>'
    print(event['content'])
    file_content = base64.b64decode(event['content'])
    list_of_events = event['params'].split("/")
    username = list_of_events[0]
    print(username)
    sqlStmt = "SELECT up_remainder from users where user_name = '"+username+"'"
    rows = cursor.execute(sqlStmt)
    usr = cursor.fetchall()
    count = int(usr[0][0])-1
    print(str(count))
    if count > 0 :
        sqlStmt="UPDATE users SET up_remainder='"+str(count)+"'WHERE user_name = '"+username+"'";
        cursor.execute(sqlStmt)
        cursor.close()
        conn.close()
        print(usr)
        file_path = event['params']
        s3 = boto3.client('s3')
        try:
            s3_response = s3.put_object(Bucket=BUCKET_NAME, Key=file_path, Body=file_content)
        except Exception as e:
            raise IOError(e)
        textract(event,context)
        return {
            'statusCode': 200,
             'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Filename",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            'Content-Type': 'application/json',
            "Set-Cookie":"HttpOnly;Secure;SameSite=Strict",
            "set-Cookie":"HttpOnly;Secure;SameSite=Strict"
            },
            'body': {
                'file_path': file_path,
                'count' : count
            }
        }
    else:
         return {
            'statusCode': 400,
             'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Filename",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            'Content-Type': 'application/json',
            "Set-Cookie":"HttpOnly;Secure;SameSite=Strict",
            "set-Cookie":"HttpOnly;Secure;SameSite=Strict"
            },
            'body': {
               'error':'user not present or you dont have image count left'
            }
        }
def textract(event,context):
    
    BUCKET_NAME = '<bucketname>'
    print(event['content'])
    file_content = base64.b64decode(event['content'])
    list_of_events = event['params'].split("/")
    username = list_of_events[0]
    filename = list_of_events[1]
    file_path = username+filename
    s3 = boto3.client('s3')
    try:
        s3_response = s3.put_object(Bucket=BUCKET_NAME, Key=file_path, Body=file_content, ContentType='image/jpeg')
    except Exception as e:
        raise IOError(e)
