from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str
    redis_url: str
    jwt_secret: str
    ai_base_url: str = 'http://10.1.2.4:6999'
    ai_model: str = '/model/models/Qwen3.6-27B'
    ai_timeout_seconds: int = 30
    ai_gateway_api_key: str = ''
    storage_endpoint: str = ''
    storage_access_key: str = ''
    storage_secret_key: str = ''
    storage_bucket: str = 'haizhi-documents'
    storage_secure: bool = False
    ad_server_url: str = ''
    ad_base_dn: str = ''
    ad_bind_dn: str = ''
    ad_bind_password: str = ''
    ad_user_filter: str = '(&(objectClass=user)(sAMAccountName=*))'
    ad_username_attribute: str = 'sAMAccountName'
    ad_display_name_attribute: str = 'displayName'
    ad_email_attribute: str = 'mail'
    ad_department_attribute: str = 'department'
    ad_external_id_attribute: str = 'objectGUID'
    ad_default_role: str = 'viewer'
    ad_login_domain: str = ''
    ad_disable_missing_users: bool = False

settings = Settings()
