from core.client_class import Client, elasticsearch_required
from core.basic_utils  import dotkeys
from core.search_utils import doctype_first, doctype_last
import json
from sqlalchemy import create_engine
import logging

logger = logging.getLogger("INCA.%s" %__name__)

class sql_ingest(Client):
    '''Class defined to ingest data from MySQL'''

    service_name = "sql_ingest"

    @elasticsearch_required
    def add_application(self, appname="default"):
        """Add a new app to generate credentials for SQL ingestion"""

        app_prompt = {
            'header' : "Add a new app to generate credentials for SQL ingestion",
            'description':
                "Please provide your credentials for the MySQL connection",

            'inputs' : [
                {
                    'label': 'Application name',
                    'description': "Name for internal use",
                    'help' : "Just a string to denote the application within INCA",
                    'input_type':'text',
                    'mimimum' : 4,
                    'maximum' : 15,
                    'default' : appname,
                },
                {
                    'label': 'host',
                    'description': "Host/IP address",
                    'help' : "Provide the IP of the MySQL server",
                    'input_type':'text',
                    'mimimum' : 4,
                    'maximum' : 20,
                    'default' : 'XXX.XXX.XXX.XXX',
                },
                {
                    'label': 'port',
                    'description': "MySQL port",
                    'help' : "MySQL port",
                    'input_type':'text',  #this should be int???
                    'mimimum' : 4,
                    'maximum' : 20,
                    'default' : '3306',
                },
                {
                    'label': 'username',
                    'description': "Username of the MySQL user",
                    'help' : "Username of the MySQL user",
                    'input_type':'text',
                },
                {
                    'label': 'password',
                    'description': "Password of the MySQL user",
                    'help' : "Password of the MySQL user",
                    'input_type':'text',
                    'mimimum' : 8,
                },
                {
                    'label': 'db_name',
                    'description': "Name of MySQL database",
                    'help' : "Password of the MySQL user(default: twittercapture)",
                    'input_type':'text',
                    'default' : 'twittercapture',
                },
                {
                    'label': 'encoding',
                    'description': "encoding",
                    'help' : "encoding (default: utf8mb4)",
                    'input_type':'text',
                    'default' : 'utf8mb4',
                },

                ]

        }
        response = self.prompt(app_prompt, verify=True)
        return self.store_application(
                app_credentials={
                                'host'    : response['host'],
                                'port' : response['port'],
                                'username'    : response['username'],
                                'password' : response['password'],
                                'db_name'    : response['db_name'],
                                'encoding' : response['encoding'],
                                }, 
                appname=response['Application name'])
    
    
    @elasticsearch_required
    def add_credentials(self, appname='default'):
        '''Add credentials to a specified app '''

        logger.info("Adding credentials to {appname}".format(**locals()))

        application = self.load_application(app=appname)
        if not application:
            logger.warning("Sorry, no application found")
            return False

        credentials = {
            'host': dotkeys(application, '_source.credentials.host'),
            'port': dotkeys(application, '_source.credentials.port'),
            'username': dotkeys(application, '_source.credentials.username'),
            'password': dotkeys(application, '_source.credentials.password'),
            'db_name': dotkeys(application, '_source.credentials.db_name'),
            'encoding': dotkeys(application, '_source.credentials.encoding')
        }

        return self.store_credentials(app=appname, credentials=json.dumps(credentials), id=credentials['username'])



class get_sql(sql_ingest):
    '''
    Class to ingest SQL data from a server into ES.
    Option to retrieve all docs, from a specific ID/date onwards 
    or from last found in ES instance. 
    In case of overlapping 'since'
    and force restrictions, the most strick will apply (the newest 
    docs than all parameters will be retrieved). 

    Arguments:
    ----------
    table:              str
                        Name of SQL table to ingest
    since_column:       str
                        Namme of column table within SQL db to be used as identifier 
                        (for IDs or dates)
    since:              str
                        optional: If given, start from this date/ID onwards
                        Possible date formats: 
                        '2017-01-01' / '2017-01-01T11:35:00'
    force:              Boolean
                        default: False
                        Skip checking ES for last retrieved document (will only be
                        restricted from 'since' argument - if provided)
    ascending:          Boolean
                        default: True
                        Order to retrieve items. Default & recommended:
                        oldest to newest
    limit:              int
                        Number of items (rows) to retrieve
    '''

    def get(self, credentials, table, since_column, force=False, since=None, ascending = True, limit=100000): 
        '''
        Method to ingest SQL data from a server into ES. 
        Special treatment for tables downloaded from twitter API (based on heuristics)
        '''

        self._credentials = json.loads(credentials['_source']['credentials'])
        self.tablename = table

        self.version = "0.1"
        self.functiontype = "sql_ingestion_client"

        # section to provide special treatment for twitter data saved on SQL databases (based on heuristics)
        company_tweet_attr = ['hashtags', 'media', 'mentions', 'places', 'tweets', 'urls', 'withheld']
        if ((len(table.split('_'))>2) &(table.split('_')[-1] in company_tweet_attr)): # check if table_name format == NL_HEMA_tweets
            self.table_attr = table.split('_')[-1]
            self.company = '_'.join(table.split('_')[:-1])
            if self.table_attr=='tweets': 
                self.doctype = 'tweets'
            else:
                self.doctype = 'twitter_'+self.table_attr

        else:
            self.doctype =  "sql_row"


        # MySQL connection
        logger.info('Establishing connection to {c[db_name]} db @ {c[host]} :{c[port]} (user: {c[username]})'.format( c = self._credentials))
        connection_str = "mysql+pymysql://{c[username]}:{c[password]}@{c[host]}/{c[db_name]}?charset={c[encoding]}".format( c = self._credentials)
        engine = create_engine(connection_str)
        try:
            con = engine.connect()
        except:
            logger.warning('Could not connect to the MySQL db. Make sure credentials are correct and your IP is in the whitelist')
        logger.info("Connected succesfully!")

        #check if given table exists
        try:
            con.execute('SELECT 1 FROM {} LIMIT 1;'.format(table))
        except:
            logger.warn('Table {} does not exist in database'.format(table))
            return {}


        #parse columns to pass as dict keys to ES
        columns = [i[0] for i in con.execute('SHOW COLUMNS FROM %s '%self.tablename)]

        # MySQL query construction

        # select all columns of table
        query = 'SELECT * FROM ' + self.tablename

        # restrict SQL results
        if not force:
            try:
                last_ES = doctype_last(doctype=self.doctype, by_field = since_column, query = 'tablename:'+self.tablename)[0]['_source'][since_column]
            except IndexError:
                logger.info("Could not find last item in ES. Are you sure the given doctype (%s) has a %s column?\n\Hit CTRL+C to cancel"%(self.doctype,since_column) )
                last_ES = 0 
        else:
            last_ES=0

        if since:
            last_arg = since
        else:
            last_arg = 0
        last = max(last_ES, last_arg)

        if last==0:
            pass
        else:
            query += " WHERE {}>\'{}\' ".format( str(since_column), last)

        # add order and limit to query
        query += ' ORDER BY \'{}\' '.format(since_column)
        if ascending:
            query += ' ASC '
        else:
            query += ' DESC '
        if limit:
            query += ' LIMIT '+ str(limit) +' '

        # close SQL query
        query += ';'

        nr_items = list(con.execute(query.replace("SELECT * FROM", "SELECT COUNT(*) FROM")))[0][0]
        logger.info("Found {} items in the database. \n".format(nr_items))
        if nr_items>limit:
            logger.info("Only {} items will be downloaded. \nTo retrieve more items (another {} remaining) run again or change the limit in the parameters".format(limit,nr_items-limit))

        # logger.info("\n-----------\nQUERY:\n-----------\n%s\n"%query)
        results = list(con.execute(query))

        for i,r in enumerate(results):
            item = dict(zip(columns, r))
            item['tablename'] = self.tablename
            if self.table_attr:
                item['table_attr'] = self.table_attr
            if self.company:
                item['company'] = self.company
            #logger.info("\n-----------\nRESULT %i:\n-----------\n\n %s: %s \n"%(i+1,since_column,item[since_column]))
            if (i%100==0):
                logger.info('Downloaded {} items'.format(i))
            yield item

        logger.info('\n----------------\nFinished\n----------------\nLast downloaded item has {}={}\n'.format(since_column,item[since_column]))
