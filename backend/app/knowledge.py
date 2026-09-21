import json
from datetime import datetime
from typing import Any, get_args, get_origin

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .database import session
from .models import *

router = APIRouter(prefix='/api', tags=['Six knowledge centers R3'])
security = HTTPBearer(auto_error=False)

PRODUCT_TYPES = {'HARDWARE', 'SOFTWARE_PRODUCT', 'SYSTEM_PRODUCT', 'ACCESSORY'}
RELATION_TYPES = {'RELATED', 'SUPPORT', 'COMMERCIALIZATION', 'RECOMMENDATION', 'COMPOSITION'}
CENTER_MODELS = {
    'products': Product,
    'software': Software,
    'algorithms': Algorithm,
    'model-capabilities': Capability,
    'scenes': Scene,
    'solutions': Solution,
}


def json_value(raw: str | None, fallback):
    try:
        value = json.loads(raw or '')
        return value if isinstance(value, type(fallback)) else fallback
    except (TypeError, ValueError):
        return fallback


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def schema_data(model, raw: dict):
    """Project a response DTO back onto an input schema, dropping read-only IDs."""
    result = {}
    for name, field in model.model_fields.items():
        alias = field.alias or name
        key = alias if alias in raw else name
        if key not in raw:
            continue
        value = raw[key]
        annotation = field.annotation
        if isinstance(value, list) and get_origin(annotation) is list:
            child = get_args(annotation)[0]
            if isinstance(child, type) and issubclass(child, BaseModel):
                value = [schema_data(child, item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, dict) and isinstance(annotation, type) and issubclass(annotation, BaseModel):
            value = schema_data(annotation, value)
        result[name] = value
    return result


def permissions(user: User) -> set[str]:
    normalized = {link.permission.code for link in user.role.permission_links}
    return normalized or {code for code in user.role.permissions.split(',') if code}


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security), db: Session = Depends(session)):
    if not credentials:
        raise HTTPException(401, '请先登录')
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=['HS256'])
    except jwt.PyJWTError as exc:
        raise HTTPException(401, '登录已失效') from exc
    user = db.scalar(select(User).where(User.id == payload['uid'], User.enabled == True))
    if not user:
        raise HTTPException(401, '用户不可用')
    return user


def require_permission(code: str):
    def dependency(user: User = Depends(current_user)):
        if code not in permissions(user):
            raise HTTPException(403, '缺少权限：' + code)
        return user
    return dependency


def audit(db: Session, user: User, action: str, resource_type: str, resource_id: int, detail=None):
    db.add(AuditLog(user_id=user.id, action=action, resource_type=resource_type, resource_id=str(resource_id), detail_json=json_text(detail or {})))


class Payload(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='forbid')


class ProductParameterPayload(Payload):
    # The detail editor round-trips persisted rows.  The database id is not
    # used when replacing the ordered parameter collection, but accepting it
    # makes edit/delete saves idempotent instead of rejecting the whole PATCH.
    id: int | None = None
    name: str = Field(min_length=1, max_length=120)
    value: str = ''
    unit: str = ''
    group: str = '基础参数'
    highlight: bool = False
    dataType: str = Field(default='TEXT', alias='data_type')
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class MediaPayload(Payload):
    image: str = Field(min_length=1, max_length=500)
    title: str = ''
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class FeaturePayload(Payload):
    title: str = Field(min_length=1, max_length=160)
    description: str = ''
    icon: str = ''
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)

class ProductVariantOfferPayload(Payload):
    priceType: str = Field(default='SALES', alias='price_type')
    channel: str = 'DIRECT'
    warrantyMonths: int | None = Field(default=None, alias='warranty_months', ge=0)
    amount: float = Field(ge=0)
    currency: str = 'CNY'
    taxIncluded: bool = Field(default=True, alias='tax_included')
    taxRate: float = Field(default=13, alias='tax_rate', ge=0, le=100)
    validUntil: datetime | None = Field(default=None, alias='valid_until')
    isDefault: bool = Field(default=False, alias='is_default')
    status: str = 'ACTIVE'
    notes: str = ''

class ProductVariantPayload(Payload):
    modelCode: str = Field(alias='model_code', min_length=1, max_length=100)
    materialCode: str = Field(default='', alias='material_code')
    unit: str = '台'
    isPrimary: bool = Field(default=False, alias='is_primary')
    isAgentProduct: bool = Field(default=False, alias='is_agent_product')
    agentPrice: float | None = Field(default=None, alias='agent_price', ge=0)
    salePrice: float | None = Field(default=None, alias='sale_price', ge=0)
    warrantyMonths: int = Field(default=24, alias='warranty_months', ge=0)
    extendedWarrantyRule: str = Field(default='', alias='extended_warranty_rule')
    applicableScenes: list[str] = Field(default=[], alias='applicable_scenes')
    salesNotes: str = Field(default='', alias='sales_notes')
    commercialStatus: str = Field(default='ACTIVE', alias='commercial_status')
    specifications: dict[str, str] = {}
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)
    offers: list[ProductVariantOfferPayload] = []


class ProductCreate(Payload):
    name: str = Field(min_length=2, max_length=160)
    productType: str = Field(default='HARDWARE', alias='product_type')
    primaryModel: str = Field(alias='model_code', min_length=1, max_length=80)
    categoryId: int = Field(alias='category_id')
    summary: str = ''
    salesStatus: str = Field(default='ON_SALE', alias='status')
    mainImage: str = Field(default='', alias='main_image')

    @field_validator('productType')
    @classmethod
    def valid_product_type(cls, value):
        if value not in PRODUCT_TYPES:
            raise ValueError('产品类型无效')
        return value


class ProductUpdate(Payload):
    name: str | None = None
    productCode: str | None = Field(default=None, alias='product_code')
    productSeries: str | None = Field(default=None, alias='product_series')
    productType: str | None = Field(default=None, alias='product_type')
    primaryModel: str | None = Field(default=None, alias='model_code')
    currentVersion: str | None = Field(default=None, alias='current_version')
    categoryId: int | None = Field(default=None, alias='category_id')
    summary: str | None = None
    description: str | None = None
    salesStatus: str | None = Field(default=None, alias='status')
    dataStatus: str | None = Field(default=None, alias='data_status')
    mainImage: str | None = Field(default=None, alias='main_image')
    gallery: list[MediaPayload] | None = None
    tags: list[str] | None = None
    features: list[FeaturePayload] | None = None
    boundaries: list[str] | None = None
    parameters: list[ProductParameterPayload] | None = None
    tenderParameters: list[ProductParameterPayload] | None = Field(default=None, alias='tender_parameters')
    variants: list[ProductVariantPayload] | None = None

    @field_validator('productType')
    @classmethod
    def valid_product_type(cls, value):
        if value is not None and value not in PRODUCT_TYPES:
            raise ValueError('产品类型无效')
        return value


class ProductOrderItem(Payload):
    id: int
    displayOrder: int = Field(alias='display_order', ge=0)


class ProductOrderPayload(Payload):
    items: list[ProductOrderItem] = Field(min_length=1)


class SoftwareFeaturePayload(Payload):
    name: str = Field(min_length=1)
    description: str = ''
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class SoftwareModulePayload(Payload):
    name: str = Field(min_length=1)
    description: str = ''
    icon: str = ''
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)
    features: list[SoftwareFeaturePayload] = []


class SoftwareVersionPayload(Payload):
    version: str = Field(min_length=1)
    releasedAt: datetime | None = Field(default=None, alias='released_at')
    summary: str = ''


class SoftwarePayload(Payload):
    name: str = Field(min_length=2)
    code: str = ''
    version: str = 'v1.0'
    softwareType: str = Field(default='PLATFORM', alias='software_type')
    vendor: str = '海智科技'
    deploymentMode: str = Field(default='PRIVATE', alias='deployment_mode')
    supportedOs: list[str] = Field(default=[], alias='supported_os')
    databases: list[str] = []
    protocols: list[str] = []
    summary: str = ''
    description: str = ''
    logo: str = ''
    status: str = 'SUPPORTED'
    boundaries: list[str] = []
    modules: list[SoftwareModulePayload] = []
    versions: list[SoftwareVersionPayload] = []
    screenshots: list[MediaPayload] = []


class SoftwarePatch(Payload):
    name: str | None = None
    code: str | None = None
    version: str | None = None
    softwareType: str | None = Field(default=None, alias='software_type')
    vendor: str | None = None
    deploymentMode: str | None = Field(default=None, alias='deployment_mode')
    supportedOs: list[str] | None = Field(default=None, alias='supported_os')
    databases: list[str] | None = None
    protocols: list[str] | None = None
    summary: str | None = None
    description: str | None = None
    logo: str | None = None
    status: str | None = None
    boundaries: list[str] | None = None
    modules: list[SoftwareModulePayload] | None = None
    versions: list[SoftwareVersionPayload] | None = None
    screenshots: list[MediaPayload] | None = None


class AlgorithmParameterPayload(Payload):
    name: str = Field(min_length=1)
    value: str = ''
    unit: str = ''
    group: str = '核心参数'
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class AlgorithmMetricPayload(Payload):
    name: str = Field(min_length=1)
    value: str = ''
    unit: str = ''
    group: str = '性能指标'
    condition: str = ''
    source: str = ''
    highlight: bool = False
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class AlgorithmPayload(Payload):
    name: str = Field(min_length=2)
    code: str = ''
    version: str = 'v1.0'
    category: str = '分析算法'
    status: str = 'SUPPORTED'
    summary: str = ''
    principle: str = ''
    inputSummary: str = Field(default='', alias='input_summary')
    outputSummary: str = Field(default='', alias='output_summary')
    parameters: list[AlgorithmParameterPayload] = []
    metrics: list[AlgorithmMetricPayload] = []
    boundaries: list[str] = []


class AlgorithmPatch(Payload):
    name: str | None = None
    code: str | None = None
    version: str | None = None
    category: str | None = None
    status: str | None = None
    summary: str | None = None
    principle: str | None = None
    inputSummary: str | None = Field(default=None, alias='input_summary')
    outputSummary: str | None = Field(default=None, alias='output_summary')
    parameters: list[AlgorithmParameterPayload] | None = None
    metrics: list[AlgorithmMetricPayload] | None = None
    boundaries: list[str] | None = None


class ModelMetricPayload(AlgorithmMetricPayload):
    dataset: str = ''
    sampleCount: str = Field(default='', alias='sample_count')
    inputResolution: str = Field(default='', alias='input_resolution')
    hardware: str = ''
    runtime: str = ''
    testedAt: datetime | None = Field(default=None, alias='tested_at')


class InputDefinitionPayload(Payload):
    name: str = Field(min_length=1)
    dataType: str = Field(alias='data_type')
    required: bool = False
    description: str = ''
    example: str = ''
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class OutputDefinitionPayload(Payload):
    name: str = Field(min_length=1)
    dataType: str = Field(alias='data_type')
    description: str = ''
    example: str = ''
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class ModelPayload(Payload):
    name: str = Field(min_length=2)
    code: str = ''
    version: str = 'v1.0'
    category: str = '视觉模型'
    modelType: str = Field(default='DETECTION', alias='model_type')
    taskType: str = Field(default='', alias='task_type')
    functionType: str = Field(default='识别', alias='function_type')
    status: str = 'SUPPORTED'
    summary: str = ''
    metrics: list[ModelMetricPayload] = []
    inputDefinitions: list[InputDefinitionPayload] = Field(default=[], alias='input_definitions')
    outputDefinitions: list[OutputDefinitionPayload] = Field(default=[], alias='output_definitions')
    deploymentRequirements: dict[str, str] = Field(default={}, alias='deployment_requirements')
    useConditions: list[str] = Field(default=[], alias='use_conditions')
    boundaries: list[str] = []


class ModelPatch(Payload):
    name: str | None = None
    code: str | None = None
    version: str | None = None
    category: str | None = None
    modelType: str | None = Field(default=None, alias='model_type')
    taskType: str | None = Field(default=None, alias='task_type')
    functionType: str | None = Field(default=None, alias='function_type')
    status: str | None = None
    summary: str | None = None
    metrics: list[ModelMetricPayload] | None = None
    inputDefinitions: list[InputDefinitionPayload] | None = Field(default=None, alias='input_definitions')
    outputDefinitions: list[OutputDefinitionPayload] | None = Field(default=None, alias='output_definitions')
    deploymentRequirements: dict[str, str] | None = Field(default=None, alias='deployment_requirements')
    useConditions: list[str] | None = Field(default=None, alias='use_conditions')
    boundaries: list[str] | None = None


class SceneItemPayload(Payload):
    title: str = Field(min_length=1)
    description: str = ''
    icon: str = ''
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class ProcessStepPayload(Payload):
    nodeTitle: str = Field(alias='node_title', min_length=1)
    nodeDescription: str = Field(default='', alias='node_description')
    icon: str = ''
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class ScenePayload(Payload):
    name: str = Field(min_length=2)
    category: str = '水域安全'
    summary: str = ''
    coverImage: str = Field(default='', alias='cover_image')
    status: str = 'PUBLISHED'
    tags: list[str] = []
    conditions: list[str] = []
    painPoints: list[SceneItemPayload] = Field(default=[], alias='pain_points')
    goals: list[SceneItemPayload] = []
    process: list[ProcessStepPayload] = []
    coreCapabilitySummary: str = Field(default='', alias='core_capability_summary')


class ScenePatch(Payload):
    name: str | None = None
    category: str | None = None
    summary: str | None = None
    coverImage: str | None = Field(default=None, alias='cover_image')
    status: str | None = None
    tags: list[str] | None = None
    conditions: list[str] | None = None
    painPoints: list[SceneItemPayload] | None = Field(default=None, alias='pain_points')
    goals: list[SceneItemPayload] | None = None
    process: list[ProcessStepPayload] | None = None
    coreCapabilitySummary: str | None = Field(default=None, alias='core_capability_summary')


class ArchitecturePayload(Payload):
    layer: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = ''
    relationType: str = Field(default='', alias='relation_type')
    relationId: int | None = Field(default=None, alias='relation_id')
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)


class CoveragePayload(Payload):
    capabilityName: str = Field(alias='capability_name', min_length=1)
    status: str = 'COVERED'
    implementation: str = ''
    relationObjects: list[dict[str, Any]] = Field(default=[], alias='relation_objects')
    notes: str = ''
    sortOrder: int = Field(default=0, alias='sort_order', ge=0)

    @field_validator('status')
    @classmethod
    def valid_status(cls, value):
        if value not in {'COVERED', 'OPTIONAL', 'NOT_COVERED'}:
            raise ValueError('能力覆盖状态无效')
        return value


class SolutionPayload(Payload):
    name: str = Field(min_length=2)
    code: str = ''
    category: str = '水域安全'
    sceneId: int = Field(alias='scene_id')
    tier: str = 'STANDARD'
    status: str = 'ACTIVE'
    summary: str = ''
    coverImage: str = Field(default='', alias='cover_image')
    targetDescription: str = Field(default='', alias='target_description')
    coverageScope: str = Field(default='', alias='coverage_scope')
    implementationNotes: str = Field(default='', alias='implementation_notes')
    architecture: list[ArchitecturePayload] = []
    capabilityCoverage: list[CoveragePayload] = Field(default=[], alias='capability_coverage')


class SolutionPatch(Payload):
    name: str | None = None
    code: str | None = None
    category: str | None = None
    sceneId: int | None = Field(default=None, alias='scene_id')
    tier: str | None = None
    status: str | None = None
    summary: str | None = None
    coverImage: str | None = Field(default=None, alias='cover_image')
    targetDescription: str | None = Field(default=None, alias='target_description')
    coverageScope: str | None = Field(default=None, alias='coverage_scope')
    implementationNotes: str | None = Field(default=None, alias='implementation_notes')
    architecture: list[ArchitecturePayload] | None = None
    capabilityCoverage: list[CoveragePayload] | None = Field(default=None, alias='capability_coverage')


class RelationPayload(Payload):
    sourceType: str = Field(alias='source_type')
    sourceId: int = Field(alias='source_id')
    targetType: str = Field(alias='target_type')
    targetId: int = Field(alias='target_id')
    relationType: str = Field(default='RELATED', alias='relation_type')
    metadata: dict[str, str | int | bool] = {}


class RelationUpdate(Payload):
    relationType: str | None = Field(default=None, alias='relation_type')
    metadata: dict[str, str | int | bool]


class PricePayload(Payload):
    referencePrice: float = Field(alias='reference_price', ge=0)
    currency: str = 'CNY'
    taxIncluded: bool = Field(default=True, alias='tax_included')
    taxRate: float = Field(default=13, alias='tax_rate', ge=0, le=100)
    validFrom: datetime | None = Field(default=None, alias='valid_from')
    validUntil: datetime | None = Field(default=None, alias='valid_until')
    notes: str = ''

class CommercialProfilePayload(Payload):
    materialCode: str = Field(default='', alias='material_code')
    unit: str = '套'
    isAgentProduct: bool = Field(default=False, alias='is_agent_product')
    agentPrice: float | None = Field(default=None, alias='agent_price', ge=0)
    salePrice: float | None = Field(default=None, alias='sale_price', ge=0)
    warrantyMonths: int = Field(default=12, alias='warranty_months', ge=0)
    extendedWarrantyRule: str = Field(default='', alias='extended_warranty_rule')
    applicableScenes: list[str] = Field(default=[], alias='applicable_scenes')
    salesNotes: str = Field(default='', alias='sales_notes')
    commercialStatus: str = Field(default='ACTIVE', alias='commercial_status')
    licenseUnit: str = Field(default='', alias='license_unit')
    includedQuantity: int | None = Field(default=None, alias='included_quantity', ge=0)
    overageUnitPrice: float | None = Field(default=None, alias='overage_unit_price', ge=0)
    deliveryMethod: str = Field(default='', alias='delivery_method')


class BomItemPayload(Payload):
    productId: int = Field(alias='product_id')
    quantity: int = Field(default=1, ge=1, le=10000)
    unit: str = '台'
    purpose: str = ''
    requirementLevel: str = Field(default='REQUIRED', alias='requirement_level')
    recommendationReason: str = Field(default='', alias='recommendation_reason')


class BomPayload(Payload):
    items: list[BomItemPayload]


def parameter_dto(item: ProductParameter):
    return {'id': item.id, 'name': item.name, 'value': item.value, 'unit': item.unit, 'group': item.group_name, 'highlight': item.highlight, 'dataType': item.data_type, 'sortOrder': item.sort_order}


def media_dto(item):
    return {'id': item.id, 'image': item.image, 'title': item.title, 'sortOrder': item.sort_order}


def price_dto(item: ProductPrice | None):
    if not item:
        return None
    return {'referencePrice': float(item.reference_price), 'currency': item.currency, 'taxIncluded': item.tax_included, 'taxRate': float(item.tax_rate), 'validFrom': item.valid_from.isoformat() if item.valid_from else None, 'validUntil': item.valid_until.isoformat() if item.valid_until else None, 'notes': item.notes}


def offer_dto(item: ProductVariantOffer):
    return {'id': item.id, 'priceType': item.price_type, 'channel': item.channel, 'warrantyMonths': item.warranty_months, 'amount': float(item.amount), 'currency': item.currency, 'taxIncluded': item.tax_included, 'taxRate': float(item.tax_rate), 'validUntil': item.valid_until.isoformat() if item.valid_until else None, 'isDefault': item.is_default, 'status': item.status, 'notes': item.notes}

def commercial_dto(item: KnowledgeCommercialProfile | None, user: User):
    if not item:return None
    result={'materialCode':item.material_code,'unit':item.unit,'isAgentProduct':item.is_agent_product,'warrantyMonths':item.warranty_months,'extendedWarrantyRule':item.extended_warranty_rule,'applicableScenes':json_value(item.applicable_scenes_json,[]),'salesNotes':item.sales_notes,'commercialStatus':item.commercial_status,'licenseUnit':item.license_unit,'includedQuantity':item.included_quantity,'deliveryMethod':item.delivery_method}
    if 'PRICE_VIEW' in permissions(user):result|={'agentPrice':float(item.agent_price) if item.agent_price is not None else None,'salePrice':float(item.sale_price) if item.sale_price is not None else None,'overageUnitPrice':float(item.overage_unit_price) if item.overage_unit_price is not None else None}
    return result


def product_dto(product: Product, db: Session, user: User, detail=False):
    result = {
        'id': product.id, 'name': product.name, 'productCode': product.product_code,
        'productSeries': product.product_series, 'primaryModel': product.model_code,
        'modelCode': product.model_code, 'currentVersion': product.current_version,
        'productType': product.product_type, 'categoryId': product.category_id,
        'category': product.category.name, 'summary': product.summary,
        'salesStatus': product.status, 'status': product.status, 'dataStatus': product.data_status,
        'mainImage': product.main_image, 'parameters': [parameter_dto(x) for x in product.parameters],
        'displayOrder': product.display_order, 'updatedAt': product.updated_at.isoformat(),
    }
    if 'PRICE_VIEW' in permissions(user):
        result['price'] = price_dto(db.scalar(select(ProductPrice).where(ProductPrice.product_id == product.id)))
        default_offer = db.scalar(select(ProductVariantOffer).join(ProductVariant).where(ProductVariant.product_id == product.id, ProductVariantOffer.is_default.is_(True), ProductVariantOffer.status == 'ACTIVE').order_by(ProductVariant.is_primary.desc(), ProductVariant.sort_order, ProductVariantOffer.id))
        result['defaultOffer'] = offer_dto(default_offer) if default_offer else None
    if detail:
        legacy_capabilities = db.scalars(
            select(Capability)
            .join(ProductCapability, Capability.id == ProductCapability.capability_id)
            .where(ProductCapability.product_id == product.id)
            .order_by(Capability.id)
        ).all()
        result |= {
            'description': product.description, 'tags': json_value(product.tags_json, []),
            'boundaries': json_value(product.boundaries_json, []),
            'gallery': [media_dto(x) for x in product.gallery],
            'features': [{'id': x.id, 'title': x.title, 'description': x.description, 'icon': x.icon, 'sortOrder': x.sort_order} for x in product.features],
            'owner': product.owner, 'source': product.source,
            'tenderParameters': json_value(product.tender_parameters_json, []),
            'relations': relation_rows('products', product.id, db),
            'capabilities': [
                {
                    'id': item.id,
                    'type': 'model-capabilities',
                    'name': item.name,
                    'category': item.category,
                    'meta': item.category,
                    'summary': item.description,
                }
                for item in legacy_capabilities
            ],
            'variants': [{'id': x.id, 'modelCode': x.model_code, 'materialCode': x.material_code, 'unit': x.unit, 'isPrimary': x.is_primary, 'isAgentProduct': x.is_agent_product, 'warrantyMonths': x.warranty_months, 'extendedWarrantyRule': x.extended_warranty_rule, 'applicableScenes': json_value(x.applicable_scenes_json, []), 'salesNotes': x.sales_notes, 'commercialStatus': x.commercial_status, 'specifications': json_value(x.specifications_json, {}), 'sortOrder': x.sort_order, **({'agentPrice': float(x.agent_price) if x.agent_price is not None else None, 'salePrice': float(x.sale_price) if x.sale_price is not None else None, 'offers': [offer_dto(offer) for offer in x.offers]} if 'PRICE_VIEW' in permissions(user) else {})} for x in sorted(product.variants, key=lambda item: item.sort_order) if x.commercial_status != 'ARCHIVED'],
        }
    return result


def relation_rows(kind: str, record_id: int, db: Session):
    records = db.scalars(select(KnowledgeRelation).where(
        ((KnowledgeRelation.source_type == kind) & (KnowledgeRelation.source_id == record_id)) |
        ((KnowledgeRelation.target_type == kind) & (KnowledgeRelation.target_id == record_id))
    ).order_by(KnowledgeRelation.updated_at.desc())).all()
    result = []
    for relation in records:
        outgoing = relation.source_type == kind and relation.source_id == record_id
        other_type = relation.target_type if outgoing else relation.source_type
        other_id = relation.target_id if outgoing else relation.source_id
        model = CENTER_MODELS.get(other_type)
        other = db.get(model, other_id) if model else None
        if other:
            if other_type == 'products' and other.data_status == 'ARCHIVED':
                continue
            if other_type != 'products' and getattr(other, 'status', None) in {'ARCHIVED', 'DEPRECATED'}:
                continue
            result.append({'relationId': relation.id, 'relationType': relation.relation_type, 'direction': 'OUTGOING' if outgoing else 'INCOMING', 'id': other.id, 'type': other_type, 'name': other.name, 'summary': getattr(other, 'summary', getattr(other, 'description', '')), 'meta': json_value(relation.metadata_json, {})})
    return result


def software_dto(record: Software, db: Session, detail=False):
    result = {'id': record.id, 'name': record.name, 'code': record.code, 'version': record.version, 'softwareType': record.software_type, 'vendor': record.vendor, 'deploymentMode': record.deployment_mode, 'supportedOs': json_value(record.supported_os_json, []), 'summary': record.description, 'logo': record.logo, 'status': record.status, 'updatedAt': record.updated_at.isoformat(), 'moduleCount': len(record.modules), 'featureCount': sum(len(x.features) for x in record.modules), 'primaryScreenshot': record.screenshots[0].image if record.screenshots else record.logo}
    if detail:
        result |= {'description': record.detail_description, 'databases': json_value(record.database_json, []), 'protocols': json_value(record.protocols_json, []), 'boundaries': json_value(record.boundaries_json, []), 'screenshots': [media_dto(x) for x in record.screenshots], 'versions': [{'id': x.id, 'version': x.version, 'releasedAt': x.released_at.isoformat() if x.released_at else None, 'summary': x.summary} for x in record.versions], 'modules': [{'id': x.id, 'name': x.name, 'description': x.description, 'icon': x.icon, 'sortOrder': x.sort_order, 'features': [{'id': f.id, 'name': f.name, 'description': f.description, 'sortOrder': f.sort_order} for f in x.features]} for x in record.modules], 'relations': relation_rows('software', record.id, db)}
    return result


def algorithm_dto(record: Algorithm, db: Session, detail=False):
    result = {'id': record.id, 'name': record.name, 'code': record.code, 'version': record.version, 'category': record.category, 'summary': record.description, 'status': record.status, 'inputSummary': record.input_summary, 'outputSummary': record.output_summary, 'metrics': [{'id': x.id, 'name': x.name, 'value': x.value, 'unit': x.unit, 'highlight': x.highlight} for x in record.metrics if x.highlight][:3], 'updatedAt': record.updated_at.isoformat()}
    if detail:
        result |= {'principle': record.principle, 'inputSummary': record.input_summary, 'outputSummary': record.output_summary, 'parameters': [{'id': x.id, 'name': x.name, 'value': x.value, 'unit': x.unit, 'group': x.group_name, 'sortOrder': x.sort_order} for x in record.parameters], 'metrics': [{'id': x.id, 'name': x.name, 'value': x.value, 'unit': x.unit, 'group': x.group_name, 'condition': x.condition, 'source': x.source, 'highlight': x.highlight, 'sortOrder': x.sort_order} for x in record.metrics], 'boundaries': json_value(record.boundaries_json, []), 'relations': relation_rows('algorithms', record.id, db)}
    return result


def model_dto(record: Capability, db: Session, detail=False):
    result = {'id': record.id, 'name': record.name, 'code': record.code, 'version': record.version, 'category': record.category, 'modelType': record.model_type, 'taskType': record.task_type, 'functionType': record.function_type, 'summary': record.description, 'status': record.status, 'metrics': [{'id': x.id, 'name': x.name, 'value': x.value, 'unit': x.unit, 'highlight': x.highlight} for x in record.metrics if x.highlight][:3], 'updatedAt': record.updated_at.isoformat()}
    if detail:
        result |= {'metrics': [{'id': x.id, 'name': x.name, 'value': x.value, 'unit': x.unit, 'group': x.group_name, 'condition': x.condition, 'source': x.source, 'dataset': x.dataset, 'sampleCount': x.sample_count, 'inputResolution': x.input_resolution, 'hardware': x.hardware, 'runtime': x.runtime, 'testedAt': x.tested_at.isoformat() if x.tested_at else None, 'highlight': x.highlight, 'sortOrder': x.sort_order} for x in record.metrics], 'inputDefinitions': [{'id': x.id, 'name': x.name, 'dataType': x.data_type, 'required': x.required, 'description': x.description, 'example': x.example, 'sortOrder': x.sort_order} for x in record.inputs], 'outputDefinitions': [{'id': x.id, 'name': x.name, 'dataType': x.data_type, 'description': x.description, 'example': x.example, 'sortOrder': x.sort_order} for x in record.outputs], 'deploymentRequirements': json_value(record.deployment_requirements_json, {}), 'useConditions': json_value(record.use_conditions_json, []), 'boundaries': json_value(record.boundaries_json, []), 'relations': relation_rows('model-capabilities', record.id, db)}
    return result


def scene_dto(record: Scene, db: Session, detail=False):
    relations = relation_rows('scenes', record.id, db)
    relation_counts = {kind: sum(1 for item in relations if item['type'] == kind) for kind in ('products', 'model-capabilities', 'solutions')}
    result = {'id': record.id, 'name': record.name, 'category': record.category, 'summary': record.summary, 'coverImage': record.cover_image, 'status': record.status, 'tags': json_value(record.tags_json, []), 'relationCounts': relation_counts, 'updatedAt': record.updated_at.isoformat()}
    if detail:
        result |= {'conditions': json_value(record.conditions_json, []), 'painPoints': [{'id': x.id, 'title': x.title, 'description': x.description, 'icon': x.icon, 'sortOrder': x.sort_order} for x in record.pains], 'goals': [{'id': x.id, 'title': x.title, 'description': x.description, 'icon': x.icon, 'sortOrder': x.sort_order} for x in record.goals], 'process': [{'id': x.id, 'nodeTitle': x.node_title, 'nodeDescription': x.node_description, 'icon': x.icon, 'sortOrder': x.sort_order} for x in record.process_steps], 'coreCapabilitySummary': record.core_capability_summary, 'relations': relation_rows('scenes', record.id, db)}
    return result


def bom_dto(solution_id: int, db: Session, user: User):
    can_price = 'PRICE_VIEW' in permissions(user)
    items, total = [], 0.0
    for item in db.scalars(select(SolutionBomItem).where(SolutionBomItem.solution_id == solution_id).order_by(SolutionBomItem.id)):
        row = {'id': item.id, 'productId': item.product_id, 'product': item.product.name, 'primaryModel': item.product.model_code, 'modelCode': item.product.model_code, 'quantity': item.quantity, 'unit': item.unit, 'purpose': item.purpose, 'requirementLevel': item.requirement_level, 'recommendationReason': item.recommendation_reason}
        if can_price:
            price = db.scalar(select(ProductPrice).where(ProductPrice.product_id == item.product_id))
            unit_price = float(price.reference_price) if price else None
            subtotal = unit_price * item.quantity if unit_price is not None else None
            row |= {'unitPrice': unit_price, 'subtotal': subtotal, 'currency': price.currency if price else 'CNY'}
            total += subtotal or 0
        items.append(row)
    result = {'items': items}
    if can_price:
        result |= {'productReferenceTotal': total, 'total': total, 'currency': 'CNY'}
    return result


def solution_dto(record: Solution, db: Session, user: User, detail=False):
    result = {'id': record.id, 'name': record.name, 'code': record.code, 'category': record.category, 'sceneId': record.scene_id, 'scene': record.scene.name, 'tier': record.tier, 'status': record.status, 'summary': record.summary, 'coverImage': record.cover_image, 'coverageScope': record.coverage_scope, 'coverageCount': len(record.capability_coverage), 'architectureCount': len(record.architecture), 'bomCount': db.scalar(select(func.count(SolutionBomItem.id)).where(SolutionBomItem.solution_id == record.id)) or 0, 'updatedAt': record.updated_at.isoformat()}
    if detail:
        result |= {'targetDescription': record.target_description, 'coverageScope': record.coverage_scope, 'implementationNotes': record.implementation_notes, 'architecture': [{'id': x.id, 'layer': x.layer, 'name': x.name, 'description': x.description, 'relationType': x.relation_type, 'relationId': x.relation_id, 'sortOrder': x.sort_order} for x in record.architecture], 'capabilityCoverage': [{'id': x.id, 'capabilityName': x.capability_name, 'status': x.status, 'implementation': x.implementation, 'relationObjects': json_value(x.relation_objects_json, []), 'notes': x.notes, 'sortOrder': x.sort_order} for x in record.capability_coverage], 'relations': relation_rows('solutions', record.id, db), 'bom': bom_dto(record.id, db, user)}
    return result


def replace_product_children(record: Product, data: dict, db: Session):
    # `model_dump()` recursively materializes nested Pydantic payloads as
    # dictionaries.  Normalize them back to payload objects before reading
    # attributes; otherwise every parameter/variant edit reaches this method
    # and fails with AttributeError (the UI then appears to save but reloads
    # the old data).
    def normalize(cls, values):
        return [item if isinstance(item, cls) else cls.model_validate(item) for item in values]
    if 'parameters' in data:
        items = normalize(ProductParameterPayload, data.pop('parameters'))
        db.query(ProductParameter).filter(ProductParameter.product_id == record.id).delete(synchronize_session=False)
        record.parameters = []
        record.parameters = [ProductParameter(name=x.name.strip(), value=x.value, unit=x.unit, group_name=x.group.strip() or '基础参数', highlight=x.highlight, data_type=x.dataType, sort_order=x.sortOrder) for x in items]
        record.dynamic_fields_json = json_text({x.name: x.value for x in record.parameters})
    if 'gallery' in data:
        db.query(ProductMedia).filter(ProductMedia.product_id == record.id).delete(synchronize_session=False)
        record.gallery = []
        record.gallery = [ProductMedia(image=x.image, title=x.title, sort_order=x.sortOrder) for x in normalize(MediaPayload, data.pop('gallery'))]
    if 'features' in data:
        db.query(ProductFeature).filter(ProductFeature.product_id == record.id).delete(synchronize_session=False)
        record.features = []
        record.features = [ProductFeature(title=x.title, description=x.description, icon=x.icon, sort_order=x.sortOrder) for x in normalize(FeaturePayload, data.pop('features'))]
    if 'tenderParameters' in data:
        record.tender_parameters_json = json_text([x.model_dump(by_alias=False) for x in normalize(ProductParameterPayload, data.pop('tenderParameters'))])
    if 'variants' in data:
        db.query(ProductVariant).filter(ProductVariant.product_id == record.id).delete(synchronize_session=False)
        record.variants = []
        record.variants = [ProductVariant(model_code=x.modelCode.strip(), material_code=x.materialCode, unit=x.unit, is_primary=x.isPrimary, is_agent_product=x.isAgentProduct, agent_price=x.agentPrice, sale_price=x.salePrice, warranty_months=x.warrantyMonths, extended_warranty_rule=x.extendedWarrantyRule, applicable_scenes_json=json_text(x.applicableScenes), sales_notes=x.salesNotes, commercial_status=x.commercialStatus, specifications_json=json_text(x.specifications), sort_order=x.sortOrder, offers=[ProductVariantOffer(price_type=offer.priceType,channel=offer.channel,warranty_months=offer.warrantyMonths,amount=offer.amount,currency=offer.currency,tax_included=offer.taxIncluded,tax_rate=offer.taxRate,valid_until=offer.validUntil,is_default=offer.isDefault,status=offer.status,notes=offer.notes) for offer in x.offers]) for x in normalize(ProductVariantPayload, data.pop('variants'))]


@router.get('/products')
def list_products(q: str = '', product_type: str = '', status: str = '', category_id: int | None = None, db: Session = Depends(session), user: User = Depends(require_permission('KNOWLEDGE_VIEW'))):
    statement = select(Product).order_by(Product.display_order, Product.id)
    if q:
        statement = statement.where(Product.name.ilike('%' + q + '%') | Product.model_code.ilike('%' + q + '%') | Product.product_code.ilike('%' + q + '%'))
    if product_type:
        statement = statement.where(Product.product_type == product_type)
    if status:
        statement = statement.where(Product.status == status)
    else:
        statement = statement.where(Product.data_status != 'ARCHIVED')
    if category_id:
        statement = statement.where(Product.category_id == category_id)
    return [product_dto(x, db, user) for x in db.scalars(statement)]


@router.patch('/products/order')
def update_product_order(payload: ProductOrderPayload, db: Session = Depends(session), user: User = Depends(require_permission('KNOWLEDGE_MANAGE'))):
    ids = [item.id for item in payload.items]
    if len(ids) != len(set(ids)):
        raise HTTPException(422, '产品排序中存在重复产品')
    records = {item.id: item for item in db.scalars(select(Product).where(Product.id.in_(ids)))}
    if len(records) != len(ids):
        raise HTTPException(404, '产品排序中包含不存在的产品')
    for item in payload.items:
        records[item.id].display_order = item.displayOrder
    audit(db, user, 'UPDATE', 'product_order', 'all', {'productIds': ids}); db.commit()
    return {'items': [{'id': item.id, 'displayOrder': item.displayOrder} for item in payload.items]}


@router.post('/products', status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(session), user: User = Depends(require_permission('KNOWLEDGE_MANAGE'))):
    if not db.get(ProductCategory, payload.categoryId):
        raise HTTPException(422, '产品分类不存在')
    code = payload.primaryModel
    suffix = 1
    while db.scalar(select(Product).where(Product.product_code == code)):
        suffix += 1
        code = f'{payload.primaryModel}-{suffix}'
    record = Product(name=payload.name, product_code=code, product_series='', model_code=payload.primaryModel, current_version='v1.0', product_type=payload.productType, category_id=payload.categoryId, summary=payload.summary, status=payload.salesStatus, main_image=payload.mainImage, owner=user.display_name, source='产品经理创建')
    db.add(record)
    try:
        db.flush(); audit(db, user, 'CREATE', 'products', record.id, payload.model_dump(by_alias=False)); db.commit(); db.refresh(record)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409, '产品名称、编码或主型号已存在') from exc
    return product_dto(record, db, user, True)


@router.get('/products/{record_id}')
def get_product(record_id: int, db: Session = Depends(session), user: User = Depends(require_permission('KNOWLEDGE_VIEW'))):
    record = db.get(Product, record_id)
    if not record:
        raise HTTPException(404, '产品不存在')
    return product_dto(record, db, user, True)


@router.patch('/products/{record_id}')
def update_product(record_id: int, payload: ProductUpdate, db: Session = Depends(session), user: User = Depends(require_permission('KNOWLEDGE_MANAGE'))):
    record = db.get(Product, record_id)
    if not record:
        raise HTTPException(404, '产品不存在')
    data = payload.model_dump(exclude_none=True, by_alias=False)
    if payload.variants is not None:
        default_count = sum(1 for variant in payload.variants for offer in variant.offers if offer.isDefault and offer.status == 'ACTIVE')
        if default_count > 1:
            raise HTTPException(422, '一个产品只能设置一条默认展示价格')
        has_sensitive_price = any(variant.offers or variant.agentPrice is not None or variant.salePrice is not None for variant in payload.variants)
        if has_sensitive_price and 'PRICE_VIEW' not in permissions(user):
            raise HTTPException(403, '缺少权限：PRICE_VIEW')
    replace_product_children(record, data, db)
    mapping = {'productCode': 'product_code', 'productSeries': 'product_series', 'productType': 'product_type', 'primaryModel': 'model_code', 'currentVersion': 'current_version', 'categoryId': 'category_id', 'salesStatus': 'status', 'dataStatus': 'data_status', 'mainImage': 'main_image'}
    for key in ['tags', 'boundaries']:
        if key in data:
            setattr(record, key + '_json', json_text(data.pop(key)))
    for key, value in data.items():
        setattr(record, mapping.get(key, key), value)
    record.owner = user.display_name
    try:
        audit(db, user, 'UPDATE', 'products', record.id, payload.model_dump(exclude_none=True)); db.commit(); db.refresh(record)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409, '产品名称、编码或主型号冲突') from exc
    return product_dto(record, db, user, True)


@router.delete('/products/{record_id}', status_code=204)
def delete_product(record_id: int, db: Session = Depends(session), user: User = Depends(require_permission('KNOWLEDGE_MANAGE'))):
    record = db.get(Product, record_id)
    if not record:
        raise HTTPException(404, '产品不存在')
    db.query(ProductCapability).filter(ProductCapability.product_id == record_id).delete()
    db.query(KnowledgeRelation).filter(((KnowledgeRelation.source_type == 'products') & (KnowledgeRelation.source_id == record_id)) | ((KnowledgeRelation.target_type == 'products') & (KnowledgeRelation.target_id == record_id))).delete(synchronize_session=False)
    db.query(ProductPrice).filter(ProductPrice.product_id == record_id).delete()
    db.query(SolutionBomItem).filter(SolutionBomItem.product_id == record_id).delete()
    db.query(DocumentAsset).filter(DocumentAsset.product_id == record_id).update({'product_id': None})
    audit(db, user, 'DELETE', 'products', record.id, {'name': record.name}); db.delete(record); db.commit()


@router.get('/products/{record_id}/prices')
def get_product_price(record_id: int, db: Session = Depends(session), user: User = Depends(require_permission('PRICE_VIEW'))):
    if not db.get(Product, record_id):
        raise HTTPException(404, '产品不存在')
    return price_dto(db.scalar(select(ProductPrice).where(ProductPrice.product_id == record_id)))


@router.patch('/products/{record_id}/prices')
def update_product_price(record_id: int, payload: PricePayload, db: Session = Depends(session), user: User = Depends(require_permission('KNOWLEDGE_MANAGE'))):
    if 'PRICE_VIEW' not in permissions(user):
        raise HTTPException(403, '缺少权限：PRICE_VIEW')
    if not db.get(Product, record_id):
        raise HTTPException(404, '产品不存在')
    record = db.scalar(select(ProductPrice).where(ProductPrice.product_id == record_id))
    values = payload.model_dump(by_alias=False)
    mapping = {'referencePrice': 'reference_price', 'taxIncluded': 'tax_included', 'taxRate': 'tax_rate', 'validFrom': 'valid_from', 'validUntil': 'valid_until'}
    if not record:
        record = ProductPrice(product_id=record_id, cost_price=0, reference_price=payload.referencePrice)
        db.add(record)
    for key, value in values.items():
        setattr(record, mapping.get(key, key), value)
    audit(db, user, 'UPDATE', 'product_price', record_id, {'priceFields': sorted(values)}); db.commit(); db.refresh(record)
    return price_dto(record)

@router.get('/{kind}/{record_id}/commercial')
def get_commercial_profile(kind:str,record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))):
    if kind not in {'software','algorithms'} or not db.get(CENTER_MODELS[kind],record_id):raise HTTPException(404,'知识条目不存在')
    return commercial_dto(db.scalar(select(KnowledgeCommercialProfile).where(KnowledgeCommercialProfile.center_type==kind,KnowledgeCommercialProfile.center_id==record_id)),user)

@router.patch('/{kind}/{record_id}/commercial')
def update_commercial_profile(kind:str,record_id:int,payload:CommercialProfilePayload,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))):
    if 'PRICE_VIEW' not in permissions(user):raise HTTPException(403,'缺少权限：PRICE_VIEW')
    if kind not in {'software','algorithms'} or not db.get(CENTER_MODELS[kind],record_id):raise HTTPException(404,'知识条目不存在')
    record=db.scalar(select(KnowledgeCommercialProfile).where(KnowledgeCommercialProfile.center_type==kind,KnowledgeCommercialProfile.center_id==record_id))
    if not record:record=KnowledgeCommercialProfile(center_type=kind,center_id=record_id);db.add(record)
    values=payload.model_dump(by_alias=False)
    mapping={'materialCode':'material_code','isAgentProduct':'is_agent_product','agentPrice':'agent_price','salePrice':'sale_price','warrantyMonths':'warranty_months','extendedWarrantyRule':'extended_warranty_rule','applicableScenes':'applicable_scenes_json','salesNotes':'sales_notes','commercialStatus':'commercial_status','licenseUnit':'license_unit','includedQuantity':'included_quantity','overageUnitPrice':'overage_unit_price','deliveryMethod':'delivery_method'}
    for key,value in values.items():setattr(record,mapping.get(key,key),json_text(value) if key=='applicableScenes' else value)
    db.flush();audit(db,user,'UPDATE','commercial_profile',record.id,{'centerType':kind,'centerId':record_id});db.commit();return commercial_dto(record,user)


def replace_software(record: Software, payload: SoftwarePayload):
    record.name=payload.name; record.code=payload.code; record.version=payload.version; record.software_type=payload.softwareType; record.vendor=payload.vendor; record.deployment_mode=payload.deploymentMode; record.supported_os_json=json_text(payload.supportedOs); record.database_json=json_text(payload.databases); record.protocols_json=json_text(payload.protocols); record.description=payload.summary; record.detail_description=payload.description; record.logo=payload.logo; record.status=payload.status; record.boundaries_json=json_text(payload.boundaries)
    record.modules=[SoftwareModule(name=x.name,description=x.description,icon=x.icon,sort_order=x.sortOrder,features=[SoftwareFeature(name=f.name,description=f.description,sort_order=f.sortOrder) for f in x.features]) for x in payload.modules]
    record.versions=[SoftwareVersion(version=x.version,released_at=x.releasedAt,summary=x.summary) for x in payload.versions]
    record.screenshots=[SoftwareMedia(image=x.image,title=x.title,sort_order=x.sortOrder) for x in payload.screenshots]


def replace_algorithm(record: Algorithm, payload: AlgorithmPayload):
    record.name=payload.name; record.code=payload.code; record.version=payload.version; record.category=payload.category; record.status=payload.status; record.description=payload.summary; record.principle=payload.principle; record.input_summary=payload.inputSummary; record.output_summary=payload.outputSummary; record.boundaries_json=json_text(payload.boundaries)
    record.parameters=[AlgorithmParameter(name=x.name,value=x.value,unit=x.unit,group_name=x.group,sort_order=x.sortOrder) for x in payload.parameters]
    record.metrics=[AlgorithmMetric(name=x.name,value=x.value,unit=x.unit,group_name=x.group,condition=x.condition,source=x.source,highlight=x.highlight,sort_order=x.sortOrder) for x in payload.metrics]
    record.metrics_json=json_text({x.name:x.value for x in payload.metrics})


def replace_model(record: Capability, payload: ModelPayload):
    record.name=payload.name; record.code=payload.code; record.version=payload.version; record.category=payload.category; record.model_type=payload.modelType; record.task_type=payload.taskType; record.function_type=payload.functionType; record.status=payload.status; record.description=payload.summary; record.deployment_requirements_json=json_text(payload.deploymentRequirements); record.use_conditions_json=json_text(payload.useConditions); record.boundaries_json=json_text(payload.boundaries)
    record.metrics=[ModelMetric(name=x.name,value=x.value,unit=x.unit,group_name=x.group,condition=x.condition,source=x.source,dataset=x.dataset,sample_count=x.sampleCount,input_resolution=x.inputResolution,hardware=x.hardware,runtime=x.runtime,tested_at=x.testedAt,highlight=x.highlight,sort_order=x.sortOrder) for x in payload.metrics]
    record.inputs=[ModelInputDefinition(name=x.name,data_type=x.dataType,required=x.required,description=x.description,example=x.example,sort_order=x.sortOrder) for x in payload.inputDefinitions]
    record.outputs=[ModelOutputDefinition(name=x.name,data_type=x.dataType,description=x.description,example=x.example,sort_order=x.sortOrder) for x in payload.outputDefinitions]
    record.metrics_json=json_text({x.name:x.value for x in payload.metrics}); record.input_requirements_json=json_text({x.name:x.description for x in payload.inputDefinitions})


def replace_scene(record: Scene, payload: ScenePayload):
    record.name=payload.name; record.category=payload.category; record.summary=payload.summary; record.cover_image=payload.coverImage; record.status=payload.status; record.tags_json=json_text(payload.tags); record.conditions_json=json_text(payload.conditions); record.core_capability_summary=payload.coreCapabilitySummary
    record.pains=[ScenePain(title=x.title,description=x.description,icon=x.icon,sort_order=x.sortOrder) for x in payload.painPoints]
    record.goals=[SceneGoal(title=x.title,description=x.description,icon=x.icon,sort_order=x.sortOrder) for x in payload.goals]
    record.process_steps=[SceneProcessStep(node_title=x.nodeTitle,node_description=x.nodeDescription,icon=x.icon,sort_order=x.sortOrder) for x in payload.process]
    record.pain_points='；'.join(x.title for x in payload.painPoints); record.goals_json=json_text([x.title for x in payload.goals]); record.process_json=json_text([x.nodeTitle for x in payload.process])


def replace_solution(record: Solution, payload: SolutionPayload):
    record.name=payload.name; record.code=payload.code; record.category=payload.category; record.scene_id=payload.sceneId; record.tier=payload.tier; record.status=payload.status; record.summary=payload.summary; record.cover_image=payload.coverImage; record.target_description=payload.targetDescription; record.coverage_scope=payload.coverageScope; record.implementation_notes=payload.implementationNotes
    record.architecture=[SolutionArchitectureNode(layer=x.layer,name=x.name,description=x.description,relation_type=x.relationType,relation_id=x.relationId,sort_order=x.sortOrder) for x in payload.architecture]
    record.capability_coverage=[SolutionCapabilityCoverage(capability_name=x.capabilityName,status=x.status,implementation=x.implementation,relation_objects_json=json_text(x.relationObjects),notes=x.notes,sort_order=x.sortOrder) for x in payload.capabilityCoverage]
    record.architecture_summary='；'.join(f'{x.layer}:{x.name}' for x in payload.architecture)


CENTER_CONFIG = {
    'software': (Software, SoftwarePayload, SoftwarePatch, replace_software, software_dto),
    'algorithms': (Algorithm, AlgorithmPayload, AlgorithmPatch, replace_algorithm, algorithm_dto),
    'model-capabilities': (Capability, ModelPayload, ModelPatch, replace_model, model_dto),
    'scenes': (Scene, ScenePayload, ScenePatch, replace_scene, scene_dto),
    'solutions': (Solution, SolutionPayload, SolutionPatch, replace_solution, solution_dto),
}


def list_center(kind, q, status, db, user):
    model, _, _, _, serializer = CENTER_CONFIG[kind]
    statement = select(model).order_by(model.updated_at.desc())
    if q:
        statement = statement.where(model.name.ilike('%' + q + '%'))
    if status:
        statement = statement.where(model.status == status)
    else:
        statement = statement.where(model.status.notin_(['ARCHIVED', 'DEPRECATED']))
    return [serializer(x, db, user) if kind == 'solutions' else serializer(x, db) for x in db.scalars(statement)]


def get_center(kind, record_id, db, user):
    model, _, _, _, serializer = CENTER_CONFIG[kind]; record = db.get(model, record_id)
    if not record: raise HTTPException(404, '知识条目不存在')
    result=serializer(record, db, user, True) if kind == 'solutions' else serializer(record, db, True)
    if kind in {'software','algorithms'}:result['commercial']=commercial_dto(db.scalar(select(KnowledgeCommercialProfile).where(KnowledgeCommercialProfile.center_type==kind,KnowledgeCommercialProfile.center_id==record_id)),user)
    return result


def create_center(kind, payload, db, user):
    model, _, _, replacer, serializer = CENTER_CONFIG[kind]
    if kind == 'solutions' and not db.get(Scene, payload.sceneId): raise HTTPException(422, '所属场景不存在')
    record=model(); replacer(record,payload); db.add(record)
    try:
        db.flush(); audit(db,user,'CREATE',kind,record.id,payload.model_dump()); db.commit(); db.refresh(record)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,'名称或编码已存在') from exc
    return serializer(record,db,user,True) if kind=='solutions' else serializer(record,db,True)


def update_center(kind, record_id, payload, db, user):
    model, full_model, _, replacer, serializer=CENTER_CONFIG[kind]; record=db.get(model,record_id)
    if not record: raise HTTPException(404,'知识条目不存在')
    current=serializer(record,db,user,True) if kind=='solutions' else serializer(record,db,True)
    merged={}
    for name,field in full_model.model_fields.items():
        alias=field.alias or name
        if name in payload.model_fields_set:
            merged[name]=getattr(payload,name)
        elif alias in current:
            merged[name]=current[alias]
        elif name in current:
            merged[name]=current[name]
    complete=full_model.model_validate(schema_data(full_model,merged))
    if kind=='solutions' and not db.get(Scene,complete.sceneId): raise HTTPException(422,'所属场景不存在')
    replacer(record,complete)
    try:
        audit(db,user,'UPDATE',kind,record.id,payload.model_dump(exclude_unset=True)); db.commit(); db.refresh(record)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,'名称或编码已存在') from exc
    return serializer(record,db,user,True) if kind=='solutions' else serializer(record,db,True)


def delete_center(kind, record_id, db, user):
    model=CENTER_CONFIG[kind][0]; record=db.get(model,record_id)
    if not record: raise HTTPException(404,'知识条目不存在')
    db.query(KnowledgeRelation).filter(((KnowledgeRelation.source_type==kind)&(KnowledgeRelation.source_id==record_id))|((KnowledgeRelation.target_type==kind)&(KnowledgeRelation.target_id==record_id))).delete(synchronize_session=False)
    if kind=='model-capabilities': db.query(ProductCapability).filter(ProductCapability.capability_id==record_id).delete()
    audit(db,user,'DELETE',kind,record.id,{'name':record.name}); db.delete(record)
    try: db.commit()
    except IntegrityError as exc: db.rollback(); raise HTTPException(409,'记录仍被业务数据引用') from exc


@router.get('/software')
def list_software(q:str='',status:str='',db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return list_center('software',q,status,db,user)
@router.get('/software/{record_id}')
def get_software(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return get_center('software',record_id,db,user)
@router.post('/software',status_code=201)
def create_software(payload:SoftwarePayload,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return create_center('software',payload,db,user)
@router.patch('/software/{record_id}')
def update_software(record_id:int,payload:SoftwarePatch,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return update_center('software',record_id,payload,db,user)
@router.delete('/software/{record_id}',status_code=204)
def delete_software(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): delete_center('software',record_id,db,user)

@router.get('/algorithms')
def list_algorithms(q:str='',status:str='',db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return list_center('algorithms',q,status,db,user)
@router.get('/algorithms/{record_id}')
def get_algorithm(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return get_center('algorithms',record_id,db,user)
@router.post('/algorithms',status_code=201)
def create_algorithm(payload:AlgorithmPayload,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return create_center('algorithms',payload,db,user)
@router.patch('/algorithms/{record_id}')
def update_algorithm(record_id:int,payload:AlgorithmPatch,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return update_center('algorithms',record_id,payload,db,user)
@router.delete('/algorithms/{record_id}',status_code=204)
def delete_algorithm(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): delete_center('algorithms',record_id,db,user)

@router.get('/model-capabilities')
def list_models(q:str='',status:str='',db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return list_center('model-capabilities',q,status,db,user)
@router.get('/model-capabilities/{record_id}')
def get_model(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return get_center('model-capabilities',record_id,db,user)
@router.post('/model-capabilities',status_code=201)
def create_model(payload:ModelPayload,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return create_center('model-capabilities',payload,db,user)
@router.patch('/model-capabilities/{record_id}')
def update_model(record_id:int,payload:ModelPatch,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return update_center('model-capabilities',record_id,payload,db,user)
@router.delete('/model-capabilities/{record_id}',status_code=204)
def delete_model(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): delete_center('model-capabilities',record_id,db,user)

@router.get('/scenes')
def list_scenes(q:str='',status:str='',db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return list_center('scenes',q,status,db,user)
@router.get('/scenes/{record_id}')
def get_scene(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return get_center('scenes',record_id,db,user)
@router.post('/scenes',status_code=201)
def create_scene(payload:ScenePayload,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return create_center('scenes',payload,db,user)
@router.patch('/scenes/{record_id}')
def update_scene(record_id:int,payload:ScenePatch,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return update_center('scenes',record_id,payload,db,user)
@router.delete('/scenes/{record_id}',status_code=204)
def delete_scene(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): delete_center('scenes',record_id,db,user)

@router.get('/solutions')
def list_solutions(q:str='',status:str='',db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return list_center('solutions',q,status,db,user)
@router.get('/solutions/{record_id}')
def get_solution(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))): return get_center('solutions',record_id,db,user)
@router.post('/solutions',status_code=201)
def create_solution(payload:SolutionPayload,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return create_center('solutions',payload,db,user)
@router.patch('/solutions/{record_id}')
def update_solution(record_id:int,payload:SolutionPatch,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): return update_center('solutions',record_id,payload,db,user)
@router.delete('/solutions/{record_id}',status_code=204)
def delete_solution(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))): delete_center('solutions',record_id,db,user)


@router.get('/solutions/{record_id}/bom')
def get_solution_bom(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_VIEW'))):
    if not db.get(Solution,record_id): raise HTTPException(404,'方案不存在')
    return bom_dto(record_id,db,user)


@router.patch('/solutions/{record_id}/bom')
def update_solution_bom(record_id:int,payload:BomPayload,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))):
    if not db.get(Solution,record_id): raise HTTPException(404,'方案不存在')
    if any(not db.get(Product,x.productId) for x in payload.items): raise HTTPException(422,'BOM引用了不存在的产品')
    db.query(SolutionBomItem).filter(SolutionBomItem.solution_id==record_id).delete()
    db.add_all([SolutionBomItem(solution_id=record_id,product_id=x.productId,quantity=x.quantity,unit=x.unit,purpose=x.purpose,requirement_level=x.requirementLevel,recommendation_reason=x.recommendationReason) for x in payload.items])
    audit(db,user,'UPDATE','solution_bom',record_id,{'count':len(payload.items)}); db.commit()
    return bom_dto(record_id,db,user)


RELATION_METADATA = {
    ('products','model-capabilities'): {'version','supportVersion','recommendedConcurrency','maxConcurrency','supportStatus','notes'},
    ('products','software'): {'minimumVersion','supportStatus','purpose','notes'},
    ('products','algorithms'): {'supportVersion','purpose','supportStatus','notes'},
    ('products','scenes'): {'relationLevel','recommendationReason','purpose','notes'},
    ('model-capabilities','scenes'): {'requirementLevel','purpose','condition','notes'},
    ('scenes','solutions'): {'solutionLevel','recommended','recommendationReason','notes'},
}


def canonical_type(value:str): return 'model-capabilities' if value=='capabilities' else value


def validate_relation(data:RelationPayload|RelationUpdate, existing:KnowledgeRelation|None=None):
    relation_type=data.relationType or (existing.relation_type if existing else 'RELATED')
    if relation_type not in RELATION_TYPES: raise HTTPException(422,'关系类型无效')
    source=canonical_type(data.sourceType) if isinstance(data,RelationPayload) else existing.source_type
    target=canonical_type(data.targetType) if isinstance(data,RelationPayload) else existing.target_type
    allowed=RELATION_METADATA.get((source,target),RELATION_METADATA.get((target,source),{'purpose','supportStatus','recommendationReason','notes'}))
    unknown=set(data.metadata)-allowed
    if unknown: raise HTTPException(422,'不支持的关系属性：'+','.join(sorted(unknown)))
    return source,target,relation_type


@router.post('/relations',status_code=201)
def create_relation(payload:RelationPayload,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))):
    source,target,relation_type=validate_relation(payload)
    if source not in CENTER_MODELS or target not in CENTER_MODELS: raise HTTPException(422,'关系对象类型无效')
    if source==target and payload.sourceId==payload.targetId: raise HTTPException(422,'不能关联对象自身')
    source_object=db.get(CENTER_MODELS[source],payload.sourceId); target_object=db.get(CENTER_MODELS[target],payload.targetId)
    if not source_object or not target_object: raise HTTPException(422,'关系对象不存在')
    if relation_type=='COMMERCIALIZATION':
        if source!='products' or target!='software' or source_object.product_type!='SOFTWARE_PRODUCT': raise HTTPException(422,'商业化映射仅允许 SOFTWARE_PRODUCT 指向 Software')
        duplicate=db.scalar(select(KnowledgeRelation).where(KnowledgeRelation.relation_type=='COMMERCIALIZATION',((KnowledgeRelation.source_type=='products')&(KnowledgeRelation.source_id==payload.sourceId))|((KnowledgeRelation.target_type=='software')&(KnowledgeRelation.target_id==payload.targetId))))
        if duplicate: raise HTTPException(409,'产品或软件已存在主要商业化映射')
    existing=db.scalar(select(KnowledgeRelation).where(KnowledgeRelation.source_type==source,KnowledgeRelation.source_id==payload.sourceId,KnowledgeRelation.target_type==target,KnowledgeRelation.target_id==payload.targetId,KnowledgeRelation.relation_type==relation_type))
    if existing: raise HTTPException(409,'关系已存在')
    record=KnowledgeRelation(source_type=source,source_id=payload.sourceId,target_type=target,target_id=payload.targetId,relation_type=relation_type,metadata_json=json_text(payload.metadata)); db.add(record)
    try:
        db.flush(); audit(db,user,'CREATE','knowledge_relation',record.id,payload.model_dump()); db.commit(); db.refresh(record)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,'关系约束冲突') from exc
    return {'id':record.id,'relationType':record.relation_type,'metadata':payload.metadata}


@router.patch('/relations/{record_id}')
def update_relation(record_id:int,payload:RelationUpdate,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))):
    record=db.get(KnowledgeRelation,record_id)
    if not record: raise HTTPException(404,'关系不存在')
    _,_,relation_type=validate_relation(payload,record); record.relation_type=relation_type; record.metadata_json=json_text(payload.metadata)
    try:
        audit(db,user,'UPDATE','knowledge_relation',record_id,payload.model_dump()); db.commit(); db.refresh(record)
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409,'关系约束冲突') from exc
    return {'id':record.id,'relationType':record.relation_type,'metadata':json_value(record.metadata_json,{})}


@router.delete('/relations/{record_id}',status_code=204)
def delete_relation(record_id:int,db:Session=Depends(session),user:User=Depends(require_permission('KNOWLEDGE_MANAGE'))):
    record=db.get(KnowledgeRelation,record_id)
    if not record: raise HTTPException(404,'关系不存在')
    audit(db,user,'DELETE','knowledge_relation',record_id,{}); db.delete(record); db.commit()
