from peewee import SqliteDatabase, Model, AutoField, CharField

conn = SqliteDatabase('Chinook_Sqlite.sqlite')
cursor = conn.cursor()


class BaseModel(Model):
    class Meta:
        database = conn


class User(BaseModel):
    user_id = AutoField(column_name='UserIdDB')
    user_tg_id = CharField(column_name="userTgId")

    class Meta:
        table_name = 'User'



