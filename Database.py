import json, os
from tabulate import tabulate

class Database_Exception(Exception):
    def __init__(self, message):
        super().__init__(message)

class json_man:
    def __init__(self, path):
        self.file_path=path
        try:
            with open(self.file_path, "r") as file:
                pass
        except:
            with open(self.file_path, "w") as file:
                file.write("{}")
            
    def get_data(self):
        with open(self.file_path, "r") as file:
            self.data:dict=json.load(file)
        return self.data
        
    def update_data(self, data):
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)
        return
    
class Database(json_man):
    def __init__(self, path):
        self.path=path
        super().__init__(self.path)
        self.tabelle:list[Tabella]=[]
        for tabella in self.get_data():
            self.tabelle.append(Tabella(tabella, self))

    def resfresh(self):
        new_data={}
        for tabella in self.tabelle:
            new_data[tabella.nome]={}
            for campo in tabella.campi:
                new_data[tabella.nome][campo.nome]=campo.elements
                
        self.update_data(new_data)
            
    def get_tabelle_names(self):
        return [tabella.name for tabella in self.tabelle]
    
    def select_tabella(self, nome_tabella:str):
        for tabella in self.tabelle:
            if tabella.nome==nome_tabella:
                return tabella
            
        raise Database_Exception(f"tabella {nome_tabella} non è presente nel database")
            
    def create_tabella(self, nome_tabella):
        if nome_tabella not in [tabella.nome for tabella in self.tabelle]:
            self.tabelle.append(Tabella(nome_tabella, self, True))
            self.resfresh()
            return self
        else:
            raise Database_Exception(f"tabella {nome_tabella} è gia presente nel database")


    def remove_tabella(self, nome_tabella):
        for tabella in self.tabelle:
            if nome_tabella == tabella.nome:
                self.tabelle.remove(tabella)
                self.resfresh()
                return self

        raise Database_Exception(f"tabella {nome_tabella} non è presente nel database")
        
    def inner_join(self, nome_tabella_1:str, nome_tabella_2:str, campo_chiave_1:str, campo_chiave_2:str, *campi):
        """_summary_
        Args:
            nome_tabella_1
            nome_tabella_2
            campo_chiave_1: ID di tabella 1
            campo_chiave_2: ID di tabella 2

        se non viene specificato l'args campi, ritorna un dict formato da tutti i campi di tabella 1 e tutti i campi di tabella 2
        i valori di questi campi sono l'intersezione ove il valore di campoChiave1=campoChiave2

        se invece vengono specificati l'args, allora ritorna un dict formato solo dai campi specificati nell'args 
        i valori di questi campi sono l'intersezione ove il valore di campoChiave1=campoChiave2
        
        Returns:
            _type_: _dict_
        """
        out={}
        table_names=[tabella.nome for tabella in self.tabelle]
        if nome_tabella_1 in table_names and nome_tabella_2 in table_names:
            tab_1=self.select_tabella(nome_tabella_1)
            tab_2=self.select_tabella(nome_tabella_2)
            
            campi_names_1=[campo.nome for campo in tab_1.campi]
            campi_names_2=[campo.nome for campo in tab_2.campi]
            if campo_chiave_1 in campi_names_1:
                obj_campo_chiave_1=tab_1.select_campo(campo_chiave_1)
            
                if campo_chiave_2 in campi_names_2:
                    obj_campo_chiave_2=tab_2.select_campo(campo_chiave_2)
                    
                    if not campi:
                        for campo in tab_1.campi:
                            out[campo.nome]=[]
                        for campo in tab_2.campi:
                            out[campo.nome]=[]
                    else:
                        for campo in campi:
                            out[campo]=[]
                    
                    for value in obj_campo_chiave_1.elements:
                        if value in obj_campo_chiave_2.elements:
                            
                            index_value_in_obj_campo_1=obj_campo_chiave_1.get_index_element(value)[0]
                            index_value_in_obj_campo_2=obj_campo_chiave_2.get_index_element(value)[0]
                            
                            if not campi:
                                for campo in tab_1.campi:
                                    out[campo.nome].append(campo.get_element_by_index(index_value_in_obj_campo_1))                    
                                for campo in tab_2.campi:
                                    out[campo.nome].append(campo.get_element_by_index(index_value_in_obj_campo_2))

                            else:
                                for campo in campi:
                                    if campo in campi_names_1:
                                        obj_campo=tab_1.select_campo(campo)
                                        out[obj_campo.nome].append(obj_campo.get_element_by_index(index_value_in_obj_campo_1))
                                        
                                    elif campo in campi_names_2:
                                        obj_campo=tab_2.select_campo(campo)
                                        out[obj_campo.nome].append(obj_campo.get_element_by_index(index_value_in_obj_campo_2))
                    return out               
                else:
                    raise Database_Exception(f"campo {campo_chiave_2} non è nella tabella {tab_2.nome}")
            else:
                raise Database_Exception(f"campo {campo_chiave_1} non è nella tabella {tab_1.nome}")
        else:
            raise Database_Exception(f"tabelle {nome_tabella_1} o tabella {nome_tabella_2} non sono presenti nel database")

    
    def print_dict_data(self, dict_data:dict, nome_tabella:str):
        print(f"== {nome_tabella.upper()} ==")
    
        colonne = list(dict_data.keys())
        righe = list(zip(*dict_data.values()))
    
        print(tabulate(righe, headers=colonne, tablefmt="grid"))
        
    
    def get_folder_size(self, folder_path):
        """
        return value in MB
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size / (1024*1024)

    def print_database(self):
        for tabella in self.tabelle:
            nome=tabella.nome
            data={}
            for campo in tabella.campi:
                data[campo.nome]=campo.get_elements()
            self.print_dict_data(data, nome)
    


class Tabella():
    def __init__(self, nome, Database:Database, new=False):
        self.super_database=Database
        self.nome=nome
        self.campi:list[Campo]=[]
        if not new:
            for campo in self.super_database.get_data()[self.nome]:
                self.campi.append(Campo(campo, self))

    def get_campi_names(self):
        return [campo.nome for campo in self.campi]
        
    def add_campo(self, nome_campo):
        if nome_campo not in [campo.nome for campo in self.campi]:
            self.campi.append(Campo(nome_campo, self, True))
            self.super_database.resfresh()
            return self
        else:
            raise Database_Exception(f"campo {nome_campo} è gia presente nella tabella {self.nome}")

    def remove_campo(self, nome_campo):
        campi_names=[campo.nome for campo in self.campi]
        if nome_campo not in campi_names:
            raise Database_Exception(f"campo {nome_campo} non è presente nella tabella {self.nome}")
        
        for campo in self.campi:
            if nome_campo==campo.nome:
                self.campi.remove(campo)
        
        self.super_database.resfresh()
        
    
    def select_campo(self, nome_campo):
        for campo in self.campi:
            if campo.nome==nome_campo:
                return campo
        raise Database_Exception(f"campo {nome_campo} non è presente nella tabella {self.nome}")
        
    def insert_into_table(self, dict_values:dict): # AGGIORNARE DA QUIIIIIIIIIIIIIIIIII
        campi_names=[campo.nome for campo in self.campi]
        
        for campo in dict_values:
            if campo in campi_names:
                campi_names.remove(campo)
                self.select_campo(campo).add_element(dict_values[campo])
                
        if len(campi_names)>0:
            raise Database_Exception(f"manca il valore dei campi: {campi_names}")
        
        return self
    
    def remove_elements_where_campo_equals_to_value(self, nome_campo, value):
        campi_names=[campo.nome for campo in self.campi]
        if nome_campo in campi_names:
            index=self.select_campo(nome_campo).get_index_element(value)[0]
            for campo in self.campi:
                campo.remove_element_by_index(index)
            return self
        else:
            raise Database_Exception(f"campo {nome_campo} non è presente nella tabella {self.nome}")
    
    def remove_elements_at_index(self, index):
        for campo in self.campi:
            campo.remove_element_by_index(index)
        return self

    def select_elements_where_campo_equals_to_value(self, nome_campo, value, reversed=False):
        """
        seleziona tutti i campi dove nome_campo=value
        """
        campi_names=[campo.nome for campo in self.campi]
        if nome_campo in campi_names:
            campo=self.select_campo(nome_campo)
            indexes=campo.get_index_element(value)
            out={}
            for campo in self.campi:
                out[campo.nome]=[]
                for index in indexes:
                    out[campo.nome].append(campo.get_element_by_index(index))
            return out
        else:
            raise Database_Exception(f"campo {nome_campo} non è presente nella tabella {self.nome}")
    
    def edit_CampoTarget_to_NewValue_where_NomeCampo_equals_to_Value(self, campo_target, new_value, nome_campo, value):
        """
        modifica il valore del campo_target in new_value dove nome_campo=value
        """
        campi_names=[campo.nome for campo in self.campi]
        if campo_target in campi_names and nome_campo in campi_names:
            print("entrambi i campi si trovano nel db")
            index=self.select_campo(nome_campo).get_index_element(value)[0]
            print(f"il valore {value} si trova alla posizione {index} all'interno di {nome_campo}")
            if not self.select_campo(campo_target).edit_element_at_index(index, new_value):
                raise Database_Exception(f"ce stato un problema nel modificare i dati del campo {campo_target}")
            return self
        else:
            raise Database_Exception(f"campo {campo_target} o campo {nome_campo} non è presente nella tabella {self.nome}")
        
class Campo():
    def __init__(self, nome, Tabella:Tabella, new=False):
        self.super_tabella=Tabella
        self.nome=nome
        self.elements:list=[]
        if not new:
            for element in self.super_tabella.super_database.get_data()[self.super_tabella.nome][self.nome]:
                self.elements.append(element)
        
    def get_elements(self):        
        return self.elements
    
    def edit_element_at_index(self, index, new_value):
        try:
            self.elements[index]=new_value
            self.super_tabella.super_database.resfresh()
            return True
        except:
            return False
    
    def add_element(self, element):
        self.elements.append(element)
        self.super_tabella.super_database.resfresh()
        return self
    
    def get_last_element(self):
        return self.elements[-1]
    
    def get_index_element(self, element):
        out=[]
        for x in range(0, len(self.elements)):
            if element==self.elements[x]:
                out.append(x)
        return out
            
    def remove_element_by_index(self, index):
        self.elements.remove(self.elements[index])
        self.super_tabella.super_database.resfresh()
        return self
    
    def get_element_by_index(self, index):
        return self.elements[index]
    