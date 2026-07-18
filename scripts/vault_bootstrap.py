import os
import hvac
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "root")

def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return private_pem.decode('utf-8'), public_pem.decode('utf-8')

def main():
    client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
    if not client.is_authenticated():
        raise RuntimeError("No se pudo autenticar con Vault. Revisa VAULT_ADDR y VAULT_TOKEN.")

    print("Conectado a Vault.")

    # 1. Habilita KV v2 en 'secret/'
    secrets_engines = client.sys.list_mounted_secrets_engines()
    if 'secret/' not in secrets_engines.get('data', {}):
        client.sys.enable_secrets_engine('kv', path='secret', options={'version': '2'})
        print("Secrets engine KV v2 habilitado en 'secret/'.")
    else:
        print("Secrets engine 'secret/' ya estaba habilitado.")

    # 2. Habilita auth method approle
    auth_methods = client.sys.list_auth_methods()
    if 'approle/' not in auth_methods.get('data', {}):
        client.sys.enable_auth_method('approle')
        print("Auth method 'approle' habilitado.")
    else:
        print("Auth method 'approle' ya estaba habilitado.")

    # 3. Políticas HCL
    policy_auth = """
    path "secret/data/jwt/private" { capabilities = ["read"] }
    path "secret/data/jwt/public" { capabilities = ["read"] }
    """
    policy_gateway = """
    path "secret/data/jwt/public" { capabilities = ["read"] }
    """
    client.sys.create_or_update_policy(name='jwt-auth', policy=policy_auth)
    client.sys.create_or_update_policy(name='jwt-gateway', policy=policy_gateway)
    print("Políticas 'jwt-auth' y 'jwt-gateway' creadas/actualizadas.")

    # 4. Crea AppRoles
    client.auth.approle.create_or_update_approle('auth', token_policies=['jwt-auth'])
    client.auth.approle.create_or_update_approle('gateway', token_policies=['jwt-gateway'])
    print("AppRoles 'auth' y 'gateway' creados/actualizados.")

    # 5 & 6. Genera e inserta par de llaves si no existen
    try:
        client.secrets.kv.v2.read_secret_version(path='jwt/private')
        print("Las llaves JWT ya existen en Vault. No se sobrescribirán.")
    except hvac.exceptions.InvalidPath:
        print("Generando nuevo par de llaves RSA 2048...")
        private_pem, public_pem = generate_rsa_key_pair()
        
        client.secrets.kv.v2.create_or_update_secret(
            path='jwt/private',
            secret={'private_key': private_pem}
        )
        client.secrets.kv.v2.create_or_update_secret(
            path='jwt/public',
            secret={'public_key': public_pem}
        )
        print("Llaves escritas exitosamente en secret/jwt/private y secret/jwt/public.")

    # 7. Imprime credenciales para .env
    auth_role_id = client.auth.approle.read_role_id('auth')['data']['role_id']
    auth_secret_id = client.auth.approle.generate_secret_id('auth')['data']['secret_id']
    
    gateway_role_id = client.auth.approle.read_role_id('gateway')['data']['role_id']
    gateway_secret_id = client.auth.approle.generate_secret_id('gateway')['data']['secret_id']

    print("\n--- CREDENCIALES PARA .env ---")
    print("\n# Servicio auth:")
    print(f"VAULT_ROLE_ID_AUTH={auth_role_id}")
    print(f"VAULT_SECRET_ID_AUTH={auth_secret_id}")
    
    print("\n# Servicio gateway:")
    print(f"VAULT_ROLE_ID_GATEWAY={gateway_role_id}")
    print(f"VAULT_SECRET_ID_GATEWAY={gateway_secret_id}")
    print("--------------------------------\n")

if __name__ == '__main__':
    main()
