import _mysql
import numpy as np
import re
import json
from pylab import *

"""
Connect to a MySQL db and get all tables in a database

Arguments
---------
host: string
    the ip address or hostname of the mysql server
port: int
    the port number to access the MySQL server.  Typically 3306
user: string
    the username to access the database
passwd: string
    the passwd associated with the username
db: string
    the database to use
"""
def connect_to_mysql_db(host, port, user, passwd, db):
    db=_mysql.connect(host=host, user=user, port=port,
                      passwd=passwd, db=db)
    db.query("SHOW TABLES")
    table_names = db.use_result()
    table_names = table_names.fetch_row(0)
    tables = [t[0] for t in table_names]
    return (db, tables)

"""
Convert time series data stored in MySQL tables to a multivariate
time series matrix.  This means stretching each time series by
adding NaNs so that all time series  are on the same level.

Arguments
---------
host: string
    the ip address or hostname of the mysql server
port: int
    the port number to access the MySQL server.  Typically 3306
user: string
    the username to access the database
passwd: string
    the passwd associated with the username
db: string
    the database to use
time_field_name: string
    the field name of the tables that stores the time
value_field_name: string
    the field name of the tables that stores the value
interval: int or float
    How far apart successive observations are in time.
    If the time series are on different intervals, this value should
    be the least common multiple of them
include: array of strings
    Default None.  Names of tables that should be queried
exclude: array of strings
    Default None.  Names of tables that should not be queried
write_to_file: string
    If not None, then write the multivariate time series matrix as a
    csv to this file
ts_aggregate_fn: function
    Default None.  If the time series stored in db are on different
    intervals, then the data will be stretched so that they are on the
    same interval.  ts_aggregate_fn is the function applied when stretching
verbose: boolean
    Default False.  If True, print the name of the table that is currently
    being queried
batch: boolean
    Default True.  If False, write multiple csv files, one for each time series.
    If True, write one csv file representing the mts
extra_sql: string
    Default None.  If set, appends this string to the SQL query.  This can
    be used to restrict data retrieval to certain time periods, i.e. 
    extra_sql = "WHERE TIME > 5 AND TIME < 10"
"""
def mysql_to_mts_matrix(host, port, user, passwd, db,
                        time_field_name, value_field_name, interval,
                        include = None, exclude = None, write_to_file = None,
                        ts_aggregate_fn = None, verbose = False, batch = True,
                        extra_sql = None):
    
    db, tables = connect_to_mysql_db(host, port, user, passwd, db)
    if include is not None:
        tables = include
    if exclude is not None:
        for e in exclude:
            tables.remove(e)
    tables.sort()
    ts_name_to_col = { }
    col = 0
    for n in tables:
        ts_name_to_col[n] = col
        col += 1

    tmin = None
    tmax = None
    for table in tables:
        if verbose:
            print(table)
        if extra_sql is not None:
            query = "SELECT min(%s), max(%s) FROM %s %s" %\
                    (time_field_name, time_field_name, table, extra_sql)
        else:
            query = "SELECT min(%s), max(%s) FROM %s" %\
                    (time_field_name, time_field_name, table)
        db.query(query)
        result = db.use_result()
        result = result.fetch_row()
        if(float(result[0][0]) < tmin or tmin is None):
            tmin = float(result[0][0])
        if(float(result[0][1]) > tmax or tmax is None):
            tmax = float(result[0][1])

    numPeriods = round((tmax - tmin) / interval) + 1
    if batch:
        numTS = len(tables)
    else:
        numTS = 1
    x = np.zeros((numPeriods, numTS))
    x[:,:] = None

    for table in tables:
        if verbose:
            print(table)
        if extra_sql is not None:
            query = "SELECT %s, %s FROM %s %s" %\
                    (time_field_name, value_field_name, table, extra_sql)
        else:
            query = "SELECT %s, %s FROM %s" %\
                    (time_field_name, value_field_name, table)
        db.query(query)
        results = db.use_result()
        running_row = None
        running_values = []
        for r in results.fetch_row(0):
            time = float(r[0])
            value = float(r[1])
            row = round((time - tmin) / interval)
            if running_row is None:
                running_row = row
                running_values.append(float(value))
            else:
                if row != running_row:
                    if batch is False:
                        col = 0
                    else:
                        col = ts_name_to_col[table]
                    x[running_row,col] = ts_aggregate_fn(running_values)
                    running_row = row
                    running_values = []
                running_values.append(float(value))
        if batch is False:
            np.savetxt(table, x, delimiter=',')
            x[:,:] = None
            
    if write_to_file is not None:
        if batch:
            np.savetxt(write_to_file, x, delimiter=',')
        m = re.search('.*(?=\.)', write_to_file)
        if m is None:
            filename = '%s_mtsconf.json' % (write_to_file)
        else:
            filename = '%s_mtsconf.json' % (m.group(0))
        f = open(filename, 'w')
        ts_name_to_col['tmin'] = tmin
        ts_name_to_col['tmax'] = tmax
        ts_name_to_col['interval'] = interval
        f.write(json.dumps(ts_name_to_col))
        f.close()

    return x

"""
Take a directory where each file represents a column of a mts and
merge the columns to reconstruct a mts matrix

Arguments
---------

dir: string
    Path to the directory containing the files
rows: int
    Number of rows in the mts matrix
cols: int
    Number of cols in the mts matrix
"""
def dir_to_mts_matrix(dir, rows, cols):
    import os
    files = os.listdir(dir)
    files.sort()
    mts = np.zeros((rows,cols))
    for i in range(len(files)):
        mts[:,i] = np.loadtxt(open("%s%s" % (dir, files[i]), "rb"), delimiter=",", skiprows=0)
    return (mts, files)

"""
Helper function for detect_nans
"""
def count_nans(array):
    return sum(np.isnan(array))

"""
Each row of the mts represents a time.  Often we want to figure out how many
time series have data for that time.  This function count number of nans in
each row and returns a 1D numpy array.

Arguments
---------

mts: 2D numpy array
    A multivariate time series where each column is an individual time series

"""
def detect_nans(mts):
    nans = np.apply_along_axis(count_nans, 0, mts)
    plot(nans)
    show()
    return nans
