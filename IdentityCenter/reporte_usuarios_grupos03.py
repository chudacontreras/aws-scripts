import boto3
import csv

client = boto3.client('identitystore')

# Obtener el ID de tu Identity Store (puedes encontrarlo en la consola de AWS Identity Center)
identity_store_id = 'd-numeros'

# Obtener la lista de usuarios con paginación
users = []
paginator = client.get_paginator('list_users')
for page in paginator.paginate(IdentityStoreId=identity_store_id):
    users.extend(page['Users'])

# Obtener la lista de grupos con paginación
groups = []
paginator = client.get_paginator('list_groups')
for page in paginator.paginate(IdentityStoreId=identity_store_id):
    groups.extend(page['Groups'])

# Crear un diccionario para almacenar los nombres de los grupos
group_names = {group['GroupId']: group['DisplayName'] for group in groups}

# Crear un diccionario para almacenar los usuarios y sus grupos
user_groups = {}

# Iterar sobre cada grupo y obtener sus miembros
for group in groups:
    group_id = group['GroupId']

    response_memberships = client.list_group_memberships(
        IdentityStoreId=identity_store_id,
        GroupId=group_id,
        MaxResults=100  # Puedes ajustar este valor si un grupo tiene muchos miembros
    )

    for membership in response_memberships['GroupMemberships']:
        user_id = membership['MemberId']['UserId']
        user_name = next((user['UserName'] for user in users if user['UserId'] == user_id), 'Usuario desconocido')  

        if user_name not in user_groups:
            user_groups[user_name] = []
        user_groups[user_name].append(group_names.get(group_id, 'Grupo desconocido'))


# Guardar los resultados en un archivo CSV
with open('reporte_usuarios_grupos.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Usuario", "Grupos"])

    for user_name, group_names in user_groups.items():
        writer.writerow([user_name, ", ".join(group_names)])
