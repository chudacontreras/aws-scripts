import boto3

def delete_default_vpc(region_name):
    """Elimina la VPC por defecto y sus dependencias en la región especificada."""

    ec2 = boto3.client('ec2', region_name=region_name)
    ec2_resource = boto3.resource('ec2', region_name=region_name)

    try:
        # Obtener el ID de la VPC por defecto
        response = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
        default_vpc_id = response['Vpcs'][0]['VpcId']
        vpc = ec2_resource.Vpc(default_vpc_id)

        print(f"Eliminando dependencias de la VPC: {default_vpc_id} en {region_name}")


        # Eliminar internet gateways (si los hay)
        for gw in vpc.internet_gateways.all():
            vpc.detach_internet_gateway(InternetGatewayId=gw.id)
            gw.delete()

        # Eliminar subredes
        for subnet in vpc.subnets.all():
            subnet.delete()

        # Eliminar tablas de rutas (excepto la principal)
        for rt in vpc.route_tables.all():
            if not rt.associations_attribute:  # Verificar si no es la tabla principal
                rt.delete()

        # Eliminar listas de control de acceso (excepto las predeterminadas)
        for acl in vpc.network_acls.all():
            if not acl.is_default:
                acl.delete()

        # Eliminar grupos de seguridad (excepto los predeterminados)
        for sg in vpc.security_groups.all():
            if sg.group_name != 'default':
                sg.delete()

        print(f"Eliminando VPC por defecto: {default_vpc_id} en {region_name}")
        ec2.delete_vpc(VpcId=default_vpc_id)
        print("VPC eliminada exitosamente.")

    except IndexError:
        print(f"No se encontró VPC por defecto en {region_name}")
    except Exception as e:
        print(f"Error al eliminar la VPC en {region_name}: {e}")


# Obtener todas las regiones disponibles (sin especificar región en el cliente)
ec2_global = boto3.client('ec2')
regions = [region['RegionName'] for region in ec2_global.describe_regions()['Regions']]

# Iterar sobre cada región y eliminar la VPC por defecto
for region in regions:
    delete_default_vpc(region)
