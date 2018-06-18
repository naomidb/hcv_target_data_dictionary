import sqlite3

def get_labels(c):
    c.execute('SELECT variable_name FROM dictionary')
    rows = c.fetchall()
    choices = {}
    count = 1
    for row in rows:
        choices[count] = row[0]
        count += 1

    return choices

def get_explanation(c, label):
    c.execute('SELECT description FROM details WHERE field=?', (label,))
    rows = c.fetchall()
    print(label + ': ' + rows[0][0])

def print_411(c, label, field_choices):
    c.execute('SELECT * FROM dictionary WHERE variable_name=?', (label,))
    rows = c.fetchall()
    count = 0
    for field in field_choices.values():
        try:
            print((' '*8) + field + ': ' + rows[0][count])
        except TypeError as e:
            print((' '*8) + field + ': ')
        count += 1

def insert_new(c, group):
    fields = ", ".join(group.keys())
    erotemes = ''
    for field in group.keys():
        erotemes += '?, '
    erotemes = erotemes[:-2]
    query= '''INSERT INTO dictionary ({}) VALUES({})'''.format(fields, erotemes)
    c.execute(query, tuple(group.values()))

def update_old(c, group, label):
    fields = ''
    for field in group.keys():
        fields += (field + ' = ? , ')
    fields = fields[:-2]
    query= '''UPDATE dictionary SET {} WHERE variable_name = ?'''.format(fields)
    values = tuple(group.values()) + (label,)
    c.execute(query, values)

def delete_entry(c, label):
    c.execute('DELETE FROM dictionary WHERE variable_name = ?', (label,))

def main():
    db = 'data_dictionary.db'
    conn = sqlite3.connect(db)
    c = conn.cursor()

    redcap_choices = get_labels(c)
    field_choices = {'1': 'variable_name', '2': 'description', '3': 'datatype', '4': 'length_of_field', '5': 'allowable_codes', '6': 'comment', '7': 'forms'}

    task = ''
    print("Select what you would like to do from the menu below:")
    menu = (' '*5) + "1: Print list of existing fields in dictionary\n\
     2: View information on an existing field in dictionary\n\
     3: Insert a new field into dictionary\n\
     4: Edit an existing field in dictionary\n\
     5: Get list of available fields\n\
     6: Delete a field in dictionary\n\
     7: Print menu again\n\
     8: Exit"
    print(menu)
    while task.lower() != 'exit':
        task = input("What would you like to do: ")
        if task=='1':
            for key, value in redcap_choices.items():
                print((' '*8) + str(key) + ': ' + value)

        elif task=='2':
            label = input("Enter the field name you would like to look up: ")
            print_411(c, label, field_choices)

        elif task=='3':
            label = input("What is the field name you would like to add: ")
            if label in redcap_choices.values():
                confirm = input("This field name already exists. Would you like to view this entry? (y/n) ")
                if confirm.lower() == 'y' or confirm.lower() == 'yes':
                    print_411(c, label, field_choices)
            else:
                print("Write the information you wish to include below. You can skip fields by hitting the return key.")
                group = {}
                for field in field_choices.values():
                    if field=='variable_name':
                        entry = label
                    else:
                        entry = input((' '*8) + field + ': ')
                    group[field] = entry
                insert_new(c, group)
                #conn.commit()
                redcap_choices = get_labels(c)

        elif task=='4':
            label = input("What is the field name you would like to edit: ")
            if label not in redcap_choices.values():
                print("This field name is not in the dictionary yet. You can add it by selecting 3 from the menu.")
            else:
                print_411(c, label, field_choices)
                print("Write the information you wish to change below. You can skip fields by hitting the return key.")
                group = {}
                for field in field_choices.values():
                    entry = input((' '*8) + field + ': ')
                    group[field] = entry
                update_old(c, group, label)
                conn.commit()
                redcap_choices = get_labels(c)

        elif task=='5':
            print("The available fields are: ")
            for key, value in field_choices.items():
                print((' '*8) + key + ': ' + value)

            study = ''
            print("If you need an explanation of any of the fields, write the associated number. When you are ready to go on, write 'done'.")
            while study.lower() != 'done':
                study = input("Get explanation for: ")
                if study.lower() != 'done':
                    get_explanation(c, field_choices[study])

        elif task=='6':
            label = input("Enter the field name you wish to delete: ")
            if label in redcap_choices.values():
                print_411(c, label, field_choices)
                confirm = input("Are you sure you want to delete this entry? (y/n) ")
                if confirm.lower() == 'y' or confirm.lower() == 'yes':
                    delete_entry(c, label)
                    conn.commit()
                    redcap_choices = get_labels(c)
            else:
                print("This field name is not in the dictionary.")

        elif task=='7':
            print(menu)

        elif task=='8':
            exit()

if __name__ == '__main__':
    main()

        