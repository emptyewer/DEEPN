import sqlite3


queries = {
    'SELECT': 'SELECT %s FROM %s WHERE %s',
    'SELECT_ALL': 'SELECT %s FROM %s',
    'INSERT': 'INSERT INTO %s VALUES(%s)',
    'UPDATE': 'UPDATE %s SET %s WHERE %s',
    'DELETE': 'DELETE FROM %s where %s',
    'DELETE_ALL': 'DELETE FROM %s',
    'CREATE_TABLE': 'CREATE TABLE IF NOT EXISTS %s(%s)',
    'DROP_TABLE': 'DROP TABLE %s',
    'TABLE_COLUMNS': 'PRAGMA table_info(%s)'}


class DatabaseObject(object):
    def __init__(self, data_file):
        self.db = sqlite3.connect(data_file, check_same_thread=False)
        self.data_file = data_file

    def free(self, cursor):
        cursor.close()

    def write(self, query, values=None):
        cursor = self.db.cursor()
        if values is not None:
            cursor.execute(query, list(values))
        else:
            cursor.execute(query)
        self.db.commit()
        return cursor

    def read(self, query, values=None):
        cursor = self.db.cursor()
        if values is not None:
            cursor.execute(query, list(values))
        else:
            cursor.execute(query)
        return cursor

    def select(self, tables, *args, **kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        subs = [kwargs[k] for k in kwargs]
        query = queries['SELECT'] % (vals, locs, conds)
        return self.read(query, subs)

    def select_all(self, tables, *args):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        query = queries['SELECT_ALL'] % (vals, locs)
        return self.read(query)

    def get_table_columns(self, table):
        query = queries['TABLE_COLUMNS'] % table[0]
        return self.read(query)

    def insert(self, table_name, *args):
        values = ','.join(['?' for l in args])
        query = queries['INSERT'] % (table_name, values)
        return self.write(query, args)

    def update(self, table_name, set_args, **kwargs):
        updates = ','.join(['%s=?' % k for k in set_args])
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        vals = [set_args[k] for k in set_args]
        subs = [kwargs[k] for k in kwargs]
        query = queries['UPDATE'] % (table_name, updates, conds)
        return self.write(query, vals + subs)

    def delete(self, table_name, **kwargs):
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        subs = [kwargs[k] for k in kwargs]
        query = queries['DELETE'] % (table_name, conds)
        print "Deleting from list \'%s\' where it matches \'%s\' from table \'%s\'" % (",".join(k for k in kwargs),
                                                                                       ",".join(kwargs[k] for k in kwargs),
                                                                                       table_name)
        return self.write(query, subs)

    def delete_all(self, table_name):
        query = queries['DELETE_ALL'] % table_name
        return self.write(query)

    def create_table(self, table_name, values):
        query = queries['CREATE_TABLE'] % (table_name, ','.join(values))
        self.free(self.write(query))

    def drop_table(self, table_name):
        query = queries['DROP_TABLE'] % table_name
        self.free(self.write(query))

    def disconnect(self):
        self.db.close()


class Table(DatabaseObject):

    def __init__(self, data_file, table_name, values):
        super(Table, self).__init__(data_file)
        self.create_table(table_name, values)
        self.table_name = table_name

    def select(self, *args, **kwargs):
        return super(Table, self).select([self.table_name], *args, **kwargs)

    def select_all(self, *args):
        return super(Table, self).select_all([self.table_name], *args)

    def get_table_columns(self, table):
        return super(Table, self).get_table_columns([self.table_name])

    def insert(self, *args):
        return super(Table, self).insert(self.table_name, *args)

    def update(self, set_args, **kwargs):
        return super(Table, self).update(self.table_name, set_args, **kwargs)

    def delete(self, **kwargs):
        return super(Table, self).delete(self.table_name, **kwargs)

    def delete_all(self):
        return super(Table, self).delete_all(self.table_name)

    def drop(self):
        return super(Table, self).drop_table(self.table_name)


class genome_db(Table):
    def __init__(self, data_file):
        super(genome_db, self).__init__(data_file, 'genome', ['genome TEXT', 'prey_library TEXT', 'orf_data TEXT',
                                                         'genecount_dictionary TEXT', 'orf_lookup_table TEXT',
                                                              'blast_db TEXT',
                                                         'junction_presequence TEXT'])
    def select(self, *args, **kwargs):
        cursor = super(genome_db, self).select(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results

    def select_all(self, *args, **kwargs):
        cursor = super(genome_db, self).select_all(*args, **kwargs)
        results = cursor.fetchall()
        cursor.close()
        return results

    def insert(self, *args):
        if not self.genome_exists(args[0]):
            self.free(super(genome_db, self).insert(*args))

    def update(self, set_args, **kwargs):
        self.free(super(genome_db, self).update(set_args, **kwargs))

    def delete(self, **kwargs):
        self.free(super(genome_db, self).delete(**kwargs))

    def delete_all(self):
        self.free(super(genome_db, self).delete_all())

    def drop(self):
        self.free(super(genome_db, self).drop())

    def genome_exists(self, name):
        results = self.select('genome', genome=name)
        return len(results) > 0


# class orf_lookup_db(Table):
#     def __init__(self, data_file, table_name):
#         super(orf_lookup_db, self).__init__(data_file, table_name, ['accession_number TEXT', 'gene_name TEXT',
#                                                                 'chromosome TEXT', 'present TEXT', 'gene_start TEXT',
#                                                                 'gene_end TEXT', 'orf_start TEXT', 'orf_end TEXT',
#                                                                 'intron TEXT', 'gene_sequence TEXT',
#                                                                 'protein_sequence TEXT'])
#     def select(self, *args, **kwargs):
#         cursor = super(orf_lookup_db, self).select(*args, **kwargs)
#         results = cursor.fetchall()
#         cursor.close()
#         return results
#
#     def select_all(self, *args, **kwargs):
#         cursor = super(orf_lookup_db, self).select_all(*args, **kwargs)
#         results = cursor.fetchall()
#         cursor.close()
#         return results
#
#     def update(self, set_args, **kwargs):
#         self.free(super(orf_lookup_db, self).update(set_args, **kwargs))
#
#     def delete(self, **kwargs):
#         self.free(super(orf_lookup_db, self).delete(**kwargs))
#
#     def delete_all(self):
#         self.free(super(orf_lookup_db, self).delete_all())
#
#     def drop(self):
#         self.free(super(orf_lookup_db, self).drop())
#
#     def get_table_columns(self, table):
#         cursor = super(orf_lookup_db, self).get_table_columns(table)
#         results = cursor.fetchall()
#         cursor.close()
#         return results


# if __name__ == '__main__':
#     g_db = genome_db('../Resources/DEEPN_db.sqlite3')
#     c_db = comment_db('../Resources/DEEPN_db.sqlite3')
#     o_db = orf_lookup_db('../Resources/DEEPN_db.sqlite3', 'mm10GeneList')
#     o_db.select_all('*')
#     for row in o_db.select_all('*'):
#         print row[0]
    # db = DatabaseObject('../Resources/DEEPN_db.sqlite3')
    # print db.select('table_names', 'user_tables')
    #g_db.insert(u'Mm101', u'Clontech(mate/plate)_pGADT7_Mouse_cDNA1', u'mm10mRNA1', u'mm10GeneDict.p1', u'mm10GeneList1', u'mm10mRNAnoSuffix.fa1', u'AATTCCACCCAAGCAGTGGTATCAACGCAGAGTGGCCATTACGGCCGGGG1')
    # g_db.delete(genome='Mm101')
    # print g_db.select_all('*')
    # print g_db.select('*', genome='Mm10')
    # g_db.select('genome', genome='Mm10')
    # print g_db.genome_exists('Mm101')
    # c_db.insert('GENEcountY2H', 'This program will read from .sam files.\nIt does a gene count giving an output '
    #                             'similar to a RNA-seq type experiment.\nThe .sam files need to be in a folder called '
    #                             'MappedSamFiles\nOutput from this program will be in two folders:\nThe Summary files '
    #                             'go into the GENEcountsFiles folder\nMore granular data for genes will be found in '
    #                             'the chromosomefiles folder\nBe patient....This program is slow but will keep you posted.')
    # c_db.delete(name='GENEcountY2H')
    # print c_db.select_all('*')