import logging
import pymysql
import json
import sys
def checkDBconn():
    #config file containing credentials for RDS MySQL instance
    db_username = "<username>"
    db_password = "<password>"
    db_name = "<db_name>"
    rds_host  = "<rds_host>"
    ## Write code for DB Connection

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    try:
        conn = pymysql.connect(rds_host, user=db_username, passwd=db_password, db=db_name, connect_timeout=15, autocommit = True)
        return conn
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
