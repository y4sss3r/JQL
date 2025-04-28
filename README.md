# JQL
Json Query Language is a basic emulator of Mysql, using json and python

## Features
- Simulate basic SQL queries (SELECT, INSERT, DELETE, INNER JOIN) using JSON.
- Lightweight and easy to use.
- No need for a MySQL server setup.

## Usage
import Database
json_file_path="database.json"
db=Database(json_file_path) # Database object

# add table
db.create_tabella("nome_tabella")

# select table 
db.select_tabella("nome_tabella") #this return an object Tabella

# add collumn
table=db.select_tabella("nome_tabella")
table.add_campo("nome_campo_1")
db.select_tabella("nome_tabella").add_campo("nome_campo_2") # or this for simplicity

# insert values into table
data={
  "nome_campo_1":"value_1",
  "nome_campo_2":"value_2"
}

db.select_tabella("nome_tabella").insert_into_table(data)


## all methods

Database:
  |__ select_tabella(nome_tabella:str) --> Tabella
  |__ create_tabella(nome_tabella:str) --> self
  |__ remove_tabella(nome_tabella_str) --> self
  |__ inner_join(nome_tabella_1:str, nome_tabella_2:str, campo_chiave_1:str, campo_chiave_2:str, *campi) --> dict
  |__ print_database() --> none

Tabella:
  |__ add_campo(nome_campo:str) --> self
  |__ remove_campo(nome_campo:str) --> self
  |__ select_campo(nome_campo:str) --> Campo
  |__ insert_into_table(dict_data:dict) --> self
  |__ remove_elements_where_campo_equals_to_value(nome_campo:str, value) --> self
  |__ remove_elements_at_index(index:int) --> self
  |__ select_elements_where_campo_equals_to_value(nome_campo:str, value) --> dict
  |__ edit_CampoTarget_to_NewValue_where_NomeCampo_equals_to_Value(campo_target:str, new_value, nome_campo:str, value) --> self

Campo:
  |__ edit_element_at_index(index:int, new_value) --> bool
  |__ add_element(element) --> self
  |__ get_last_element() --> Any
  |__ get_index_element(element) --> list
  |__ remove_element_by_index(index:int) --> self
  |__ get_element_by_index(index) --> Any

