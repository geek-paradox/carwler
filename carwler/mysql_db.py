import mysql.connector as mysql


class MysqlDatabase:
    def __init__(self):
        self.db = mysql.connect(
            host='localhost',
            user='root',
            passwd='paytm@197'
        )

    def create_database(self):
        cursor = self.db.cursor()
        cursor.execute('CREATE DATABASE cars')


class MysqlTable:
    def __init__(self):
        self.db = mysql.connect(
            host='localhost',
            user='root',
            passwd='paytm@197',
            database='cars'
        )

    def list_tables(self):
        cursor = self.db.cursor()
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        for table in tables:
            print(table)

    def execute(self, cursor, statement, values):
        print('Statement:: ',statement)
        if not values:
            cursor.execute(statement)
        else:
            print('Values:: ',values)
            cursor.execute(statement, values)

    def delete_tables(self, tables):
        cursor = self.db.cursor()
        self.execute(cursor, 'DROP TABLES {tables}'.format(tables=', '.join(tables)), None)

    def create_tables(self):
        cursor = self.db.cursor()
        self.execute(cursor, 'CREATE TABLE brand ('
                       'id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,'
                       'name VARCHAR(255),'
                       'url VARCHAR(255))', None)
        self.execute(cursor, 'CREATE TABLE model ('
                       'id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,'
                       'name VARCHAR(255),'
                       'brand_id INT(11),'
                       'url VARCHAR(255),'
                       'body_type VARCHAR(20))', None)
        self.execute(cursor, 'CREATE TABLE variant ('
                        'id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,'
                        'model_id VARCHAR(255),'
                        'name VARCHAR(255),'
                        'url VARCHAR(255),'
                        'fuel_type VARCHAR(255),'
                        'transmission_type VARCHAR(255),'
                        'price VARCHAR(255),'
                        'specifications VARCHAR(16000),'
                        'features VARCHAR(16000))', None)

    def create_dynamic_table(self, table, columns):
        cursor = self.db.cursor()
        column_statement = ' VARCHAR(255), '.join(columns) + ' VARCHAR(255)'
        statement = 'CREATE TABLE {table} (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, {columns})'\
                    .format(table=table, columns=column_statement)
        print('Create dynamic table sql:: {statement}'.format(statement=statement))
        cursor.execute(statement)

    def insert_brands(self, rows: list):
        query = 'INSERT INTO brand (name, url) VALUES (%s, %s)'
        values = []
        for row in rows:
            values.append((row['name'], row['url']))
        cursor = self.db.cursor()
        self.execute(cursor, query, values)

    def insert_models(self, rows: list):
        query = 'INSERT INTO model (name, brand_id, url, body_type) VALUES (%s, %s, %s, %s)'
        values = []
        for row in rows:
            values.append((row['name'], row['brand_id'], row['url'], row['body_type']))
        cursor = self.db.cursor()
        self.execute(cursor, query, values)

    def insert_dynamic_table(self, table, dict_rows: [dict]):
        query = 'INSERT INTO {0} ({1}) VALUES ({2})'
        cursor = self.db.cursor()
        for row in dict_rows:
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['%s'] * len(row))
            sql = query.format(table, columns, placeholders)
            self.execute(cursor, sql, list(row.values()))

    def commit(self):
        self.db.commit()


if __name__ == '__main__':
    mysql_table = MysqlTable()
    mysql_table.create_tables()
