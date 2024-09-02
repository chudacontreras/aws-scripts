import boto3

client = boto3.client('identitystore')

# Obtener el ID de tu Identity Store (puedes encontrarlo en la consola de AWS Identity Center)
identity_store_id = 'TU_IDENTITY_STORE_ID'

# Obtener la lista de usuarios
response_users = client.list_users(
    IdentityStoreId=identity_store_id,
    MaxResults=100  # Puedes ajustar este valor según la cantidad de usuarios
)

users = response_users['Users']

# Obtener la lista de grupos
response_groups = client.list_groups(
    IdentityStoreId=identity_store_id,
    MaxResults=100  # Puedes ajustar este valor según la cantidad de grupos
)

groups = response_groups['Groups']

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


# Imprimir los resultados en formato CSV
print("Usuario,Grupos")
for user_name, group_names in user_groups.items():
    print(f"{user_name},\"{', '.join(group_names)}\"")
