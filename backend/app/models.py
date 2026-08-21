from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now(): return datetime.now(timezone.utc)
class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)
class Role(Base, Timestamped):
    __tablename__='roles'; id:Mapped[int]=mapped_column(primary_key=True); code:Mapped[str]=mapped_column(String(64),unique=True); name:Mapped[str]=mapped_column(String(80)); permissions:Mapped[str]=mapped_column(Text,default=''); permission_links=relationship('RolePermission',cascade='all, delete-orphan',lazy='selectin')
class Permission(Base, Timestamped):
    __tablename__='permissions'; id:Mapped[int]=mapped_column(primary_key=True); code:Mapped[str]=mapped_column(String(80),unique=True); name:Mapped[str]=mapped_column(String(120)); description:Mapped[str]=mapped_column(Text,default='')
class RolePermission(Base):
    __tablename__='role_permissions'; role_id:Mapped[int]=mapped_column(ForeignKey('roles.id',ondelete='CASCADE'),primary_key=True); permission_id:Mapped[int]=mapped_column(ForeignKey('permissions.id',ondelete='CASCADE'),primary_key=True); permission=relationship(Permission,lazy='joined')
class User(Base, Timestamped):
    __tablename__='users'; id:Mapped[int]=mapped_column(primary_key=True); username:Mapped[str]=mapped_column(String(64),unique=True); display_name:Mapped[str]=mapped_column(String(80)); password_hash:Mapped[str]=mapped_column(String(255)); role_id:Mapped[int]=mapped_column(ForeignKey('roles.id')); enabled:Mapped[bool]=mapped_column(Boolean,default=True); role=relationship(Role)
class ProductCategory(Base, Timestamped):
    __tablename__='product_categories'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(80),unique=True); description:Mapped[str]=mapped_column(Text,default='')
class Product(Base, Timestamped):
    __tablename__='products'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(160),unique=True); model_code:Mapped[str]=mapped_column(String(80),unique=True); product_type:Mapped[str]=mapped_column(String(48),default='HARDWARE'); category_id:Mapped[int]=mapped_column(ForeignKey('product_categories.id')); summary:Mapped[str]=mapped_column(Text,default=''); status:Mapped[str]=mapped_column(String(32),default='ON_SALE'); main_image:Mapped[str]=mapped_column(String(500),default=''); dynamic_fields_json:Mapped[str]=mapped_column(Text,default='{}'); data_status:Mapped[str]=mapped_column(String(32),default='CONFIRMED'); source:Mapped[str]=mapped_column(String(80),default='正式演示数据'); owner:Mapped[str]=mapped_column(String(80),default='产品中心'); last_verified_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now); category=relationship(ProductCategory)
class Capability(Base, Timestamped):
    __tablename__='capabilities'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(100),unique=True); code:Mapped[str]=mapped_column(String(80),default=''); version:Mapped[str]=mapped_column(String(32),default='v1.0'); category:Mapped[str]=mapped_column(String(80)); function_type:Mapped[str]=mapped_column(String(80),default='识别'); metrics_json:Mapped[str]=mapped_column(Text,default='{}'); input_requirements_json:Mapped[str]=mapped_column(Text,default='{}'); deployment_requirements_json:Mapped[str]=mapped_column(Text,default='{}'); boundaries_json:Mapped[str]=mapped_column(Text,default='[]'); description:Mapped[str]=mapped_column(Text); status:Mapped[str]=mapped_column(String(32),default='SUPPORTED')
class Algorithm(Base, Timestamped):
    __tablename__='algorithms'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(120),unique=True); code:Mapped[str]=mapped_column(String(80),default=''); version:Mapped[str]=mapped_column(String(32)); category:Mapped[str]=mapped_column(String(80)); input_summary:Mapped[str]=mapped_column(Text,default=''); output_summary:Mapped[str]=mapped_column(Text,default=''); metrics_json:Mapped[str]=mapped_column(Text,default='{}'); boundaries_json:Mapped[str]=mapped_column(Text,default='[]'); description:Mapped[str]=mapped_column(Text); status:Mapped[str]=mapped_column(String(32),default='SUPPORTED')
class Software(Base, Timestamped):
    __tablename__='software'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(120),unique=True); code:Mapped[str]=mapped_column(String(80),default=''); software_type:Mapped[str]=mapped_column(String(48),default='PLATFORM'); vendor:Mapped[str]=mapped_column(String(120),default='海智科技'); version:Mapped[str]=mapped_column(String(32)); deployment_mode:Mapped[str]=mapped_column(String(48),default='PRIVATE'); supported_os_json:Mapped[str]=mapped_column(Text,default='[]'); description:Mapped[str]=mapped_column(Text); status:Mapped[str]=mapped_column(String(32),default='SUPPORTED')
class Scene(Base, Timestamped):
    __tablename__='scenes'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(120),unique=True); category:Mapped[str]=mapped_column(String(80),default='水域安全'); summary:Mapped[str]=mapped_column(Text); cover_image:Mapped[str]=mapped_column(String(500),default=''); pain_points:Mapped[str]=mapped_column(Text,default=''); goals_json:Mapped[str]=mapped_column(Text,default='[]'); process_json:Mapped[str]=mapped_column(Text,default='[]'); core_capability_summary:Mapped[str]=mapped_column(Text,default=''); status:Mapped[str]=mapped_column(String(32),default='ON_SALE')
class Solution(Base, Timestamped):
    __tablename__='solutions'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(120),unique=True); scene_id:Mapped[int]=mapped_column(ForeignKey('scenes.id')); tier:Mapped[str]=mapped_column(String(32)); summary:Mapped[str]=mapped_column(Text); scene=relationship(Scene)
class ProductCapability(Base):
    __tablename__='product_capabilities'; product_id:Mapped[int]=mapped_column(ForeignKey('products.id'),primary_key=True); capability_id:Mapped[int]=mapped_column(ForeignKey('capabilities.id'),primary_key=True)
class BomRule(Base, Timestamped):
    __tablename__='bom_rules'; id:Mapped[int]=mapped_column(primary_key=True); code:Mapped[str]=mapped_column(String(80),unique=True); name:Mapped[str]=mapped_column(String(160)); condition_json:Mapped[str]=mapped_column(Text); recommendation_json:Mapped[str]=mapped_column(Text); enabled:Mapped[bool]=mapped_column(Boolean,default=True)
class Project(Base, Timestamped):
    __tablename__='projects'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(160)); customer:Mapped[str]=mapped_column(String(160)); region:Mapped[str]=mapped_column(String(100)); scene_id:Mapped[int]=mapped_column(ForeignKey('scenes.id')); requirements_json:Mapped[str]=mapped_column(Text,default='{}'); bom_json:Mapped[str]=mapped_column(Text,default='[]'); bom_version:Mapped[int]=mapped_column(Integer,default=1); scene=relationship(Scene)
class ProductPrice(Base, Timestamped):
    __tablename__='product_prices'; id:Mapped[int]=mapped_column(primary_key=True); product_id:Mapped[int]=mapped_column(ForeignKey('products.id')); reference_price:Mapped[float]=mapped_column(Numeric(12,2)); cost_price:Mapped[float]=mapped_column(Numeric(12,2)); currency:Mapped[str]=mapped_column(String(8),default='CNY'); product=relationship(Product)
class PriceAccessLog(Base, Timestamped):
    __tablename__='price_access_logs'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id')); action:Mapped[str]=mapped_column(String(32)); resource:Mapped[str]=mapped_column(String(120))
class Tender(Base, Timestamped):
    __tablename__='tenders'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(180),unique=True); customer:Mapped[str]=mapped_column(String(160)); deadline:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True); status:Mapped[str]=mapped_column(String(32),default='PREPARING'); summary:Mapped[str]=mapped_column(Text,default='')
class DocumentAsset(Base, Timestamped):
    __tablename__='documents'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(255)); path:Mapped[str]=mapped_column(String(500)); mime_type:Mapped[str]=mapped_column(String(100)); product_id:Mapped[int|None]=mapped_column(ForeignKey('products.id'),nullable=True); scene_id:Mapped[int|None]=mapped_column(ForeignKey('scenes.id'),nullable=True); tender_id:Mapped[int|None]=mapped_column(ForeignKey('tenders.id',ondelete='SET NULL'),nullable=True)
class AiInteractionLog(Base, Timestamped):
    __tablename__='ai_interaction_logs'; id:Mapped[int]=mapped_column(primary_key=True); request_id:Mapped[str]=mapped_column(String(64),unique=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id')); provider:Mapped[str]=mapped_column(String(32)); model_id:Mapped[str]=mapped_column(String(160)); latency_ms:Mapped[int]=mapped_column(Integer); success:Mapped[bool]=mapped_column(Boolean); failure_reason:Mapped[str]=mapped_column(Text,default='')
class AuditLog(Base, Timestamped):
    __tablename__='audit_logs'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id')); action:Mapped[str]=mapped_column(String(32)); resource_type:Mapped[str]=mapped_column(String(64)); resource_id:Mapped[str]=mapped_column(String(64)); detail_json:Mapped[str]=mapped_column(Text,default='{}')
class DocumentChunk(Base, Timestamped):
    __tablename__='document_chunks'; id:Mapped[int]=mapped_column(primary_key=True); document_id:Mapped[int|None]=mapped_column(ForeignKey('documents.id',ondelete='CASCADE'),nullable=True); content:Mapped[str]=mapped_column(Text); embedding_json:Mapped[str]=mapped_column(Text); metadata_json:Mapped[str]=mapped_column(Text,default='{}')
class TrainingCourse(Base, Timestamped):
    __tablename__='training_courses'; id:Mapped[int]=mapped_column(primary_key=True); external_course_id:Mapped[str]=mapped_column(String(80),unique=True); name:Mapped[str]=mapped_column(String(180)); summary:Mapped[str]=mapped_column(Text,default=''); launch_url:Mapped[str]=mapped_column(String(500)); status:Mapped[str]=mapped_column(String(32),default='ACTIVE')
