import boto3
import csv

client_org = boto3.client('organizations')
client_iam = boto3.client('iam')

def get_account_groups_and_users(account_id):
    groups_and_users = {}

    # Asumir rol en la cuenta de destino (necesitarás permisos adecuados)
    sts_client = boto3.client('sts')
    role_arn = f'arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole'  # O el rol que uses
    response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName='GetGroupsAndUsers')

    # Crear cliente IAM para la cuenta asumida
    iam_client = boto3.client('iam',
                             aws_access_key_id=response['Credentials']['AccessKeyId'],
                             aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                             aws_session_token=response['Credentials']['SessionToken'])

    # Listar grupos y sus usuarios
    for group in iam_client.list_groups()['Groups']:
        group_name = group['GroupName']
        users = iam_client.get_group(GroupName=group_name)['Users']
        user_names = [user['UserName'] for user in users]
        groups_and_users[group_name] = user_names

    return groups_and_users

# Obtener la lista de cuentas de la organización
response = client_org.list_accounts()
accounts = response['Accounts']


# Obtener grupos y usuarios para cada cuenta
with open('reporte_cuentas_grupos_usuarios.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Cuenta", "Grupo", "Usuarios"])

    for account in accounts:
        account_id = account['Id']
        account_name = account['Name']

        groups_and_users = get_account_groups_and_users(account_id)
        for group_name, user_names in groups_and_users.items():
            writer.writerow([account_name, group_name, ", ".join(user_names)])