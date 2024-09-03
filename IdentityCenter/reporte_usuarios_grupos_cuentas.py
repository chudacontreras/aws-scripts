import boto3
import csv

# Inicializar el cliente de Identity Store
identity_store_client = boto3.client('identitystore')

# Inicializar el cliente de SSO Admin
sso_admin_client = boto3.client('sso-admin')

# Inicializar el cliente de Organizations para obtener los nombres de las cuentas
organizations_client = boto3.client('organizations')


# Función para obtener los usuarios
def get_users(identity_store_id):
    users = []
    paginator = identity_store_client.get_paginator('list_users')
    for page in paginator.paginate(IdentityStoreId=identity_store_id):
        users.extend(page['Users'])
    return users


# Función para obtener los grupos a los que pertenece un usuario
def get_user_groups(identity_store_id, user_id):
    groups = []
    paginator = identity_store_client.get_paginator('list_group_memberships_for_member')
    for page in paginator.paginate(IdentityStoreId=identity_store_id, MemberId={'UserId': user_id}):
        groups.extend(page['GroupMemberships'])
    return groups


# Función para obtener todos los Permission Sets en la instancia de SSO
def get_all_permission_sets():
    permission_sets = []
    paginator = sso_admin_client.get_paginator('list_permission_sets')
    for page in paginator.paginate(InstanceArn=sso_instance_arn):
        permission_sets.extend(page['PermissionSets'])
    return permission_sets


# Función para obtener el nombre de un Permission Set
def get_permission_set_name(permission_set_arn):
    response = sso_admin_client.describe_permission_set(InstanceArn=sso_instance_arn,
                                                        PermissionSetArn=permission_set_arn)
    return response['PermissionSet']['Name']


# Función para obtener las cuentas a las que un Permission Set está asignado
def get_accounts_for_permission_set(permission_set_arn):
    accounts = []
    paginator = sso_admin_client.get_paginator('list_accounts_for_provisioned_permission_set')
    for page in paginator.paginate(InstanceArn=sso_instance_arn, PermissionSetArn=permission_set_arn):
        accounts.extend(page['AccountIds'])
    return accounts


# Función para obtener el nombre de una cuenta a partir de su ID
def get_account_name(account_id):
    try:
        response = organizations_client.describe_account(AccountId=account_id)
        return response['Account']['Name']
    except organizations_client.exceptions.AccountNotFoundException:
        return "Unknown"


# Función para verificar si un usuario está asignado a un Permission Set en una cuenta específica
def is_user_assigned_to_permission_set(account_id, user_id, permission_set_arn):
    paginator = sso_admin_client.get_paginator('list_account_assignments')
    for page in paginator.paginate(InstanceArn=sso_instance_arn, AccountId=account_id,
                                   PermissionSetArn=permission_set_arn):
        for assignment in page['AccountAssignments']:
            if assignment['PrincipalId'] == user_id:
                return True
    return False


# Configurar los parámetros iniciales
identity_store_id = 'd-90677080dc'  # Reemplaza con tu Identity Store ID
sso_instance_arn = 'arn:aws:sso:::instance/ssoins-72238a94f995b195'  # Reemplaza con tu ARN de la instancia de SSO

# Obtener todos los usuarios
users = get_users(identity_store_id)

# Obtener todos los Permission Sets disponibles
all_permission_sets = get_all_permission_sets()

# Procesar y guardar la información en un archivo CSV
with open('identity_center_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['UserName', 'UserId', 'Groups', 'PermissionSets', 'Accounts'])

    for user in users:
        user_id = user['UserId']
        user_name = user['UserName']

        # Obtener los grupos del usuario
        groups = get_user_groups(identity_store_id, user_id)
        group_ids = [group['GroupId'] for group in groups]

        # Obtener los Permission Sets y cuentas asociadas
        permission_set_arns = []
        permission_set_names = []
        account_ids = []
        account_names = []

        for permission_set_arn in all_permission_sets:
            if is_user_assigned_to_permission_set(account_id='285026024173', user_id=user_id,
                                                  permission_set_arn=permission_set_arn):
                permission_set_arns.append(permission_set_arn)
                permission_set_names.append(get_permission_set_name(permission_set_arn))
                accounts = get_accounts_for_permission_set(permission_set_arn)
                account_ids.extend(accounts)
                account_names.extend([get_account_name(account_id) for account_id in accounts])

        writer.writerow(
            [user_name, user_id, ', '.join(group_ids), ', '.join(permission_set_names), ', '.join(account_names)])

print("Datos extraídos y guardados en 'identity_center_data.csv'")
