<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ArrowLeft, Delete, Edit, Link, Plus, Remove, Select } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  record: Record<string, any>
  categories: Array<{ id: number; name: string }>
  canManage?: boolean
  showPrice?: boolean
  startEditing?: boolean
}>(), { canManage: false, showPrice: false, startEditing: false })
const emit = defineEmits<{ back: []; save: [value: Record<string, any>]; savePrice: [value: Record<string, any>]; delete: []; relate: [kind: string]; openRelation: [relation: any] }>()
const editing = ref(false)
const draft = reactive<Record<string, any>>({})
const dynamicFields = ref<Array<{ key: string; value: string }>>([])
const priceEditing=ref(false),priceDraft=reactive({reference_price:0,currency:'CNY',tax_included:true,tax_rate:13,valid_until:'',notes:''})
const productTypes = [{label:'硬件产品',value:'HARDWARE'},{label:'软件产品',value:'SOFTWARE_PRODUCT'},{label:'算法/模型商业产品',value:'AI_PRODUCT'},{label:'系统/解决方案产品',value:'SYSTEM_SOLUTION'},{label:'配套设备',value:'ACCESSORY'}]
const typeName = computed(() => productTypes.find((item) => item.value === props.record.productType)?.label || '硬件产品')
const allRelations = computed(() => {
  const legacy = (props.record.capabilities || []).map((item:any) => ({ ...item, type: 'model-capabilities' }))
  const modern = props.record.relations || []
  const seen = new Set(modern.map((item:any) => item.type + ':' + item.id))
  return [...modern, ...legacy.filter((item:any) => !seen.has(item.type + ':' + item.id))]
})
const recommendations: Record<string, string[]> = {HARDWARE:['外形尺寸','工作温度','防护等级'],SOFTWARE_PRODUCT:['部署方式','操作系统','数据库'],AI_PRODUCT:['模型框架','输入类型','推理算力'],SYSTEM_SOLUTION:['部署架构','适用规模','交付周期'],ACCESSORY:['接口类型','供电方式','安装方式']}

function resetDraft() {
  Object.assign(draft, { name: props.record.name, product_type: props.record.productType, model_code: props.record.modelCode, category_id: props.record.categoryId, summary: props.record.summary, status: props.record.status, main_image: props.record.mainImage || '' })
  dynamicFields.value = Object.entries(props.record.dynamicFields || {}).map(([key, value]) => ({ key, value: String(value) }))
}
function beginEdit(){resetDraft();editing.value=true}
function addField(key=''){dynamicFields.value.push({key,value:''})}
function save(){const fields=Object.fromEntries(dynamicFields.value.filter((item)=>item.key.trim()).map((item)=>[item.key.trim(),item.value]));emit('save',{...draft,dynamic_fields:fields});editing.value=false}
function beginPriceEdit(){Object.assign(priceDraft,{reference_price:props.record.price?.referencePrice||0,currency:props.record.price?.currency||'CNY',tax_included:props.record.price?.taxIncluded??true,tax_rate:props.record.price?.taxRate??13,valid_until:props.record.price?.validUntil?.slice(0,10)||'',notes:props.record.price?.notes||''});priceEditing.value=true}
function savePrice(){emit('savePrice',{...priceDraft,valid_until:priceDraft.valid_until||null});priceEditing.value=false}
watch(() => props.record.id, () => { resetDraft(); editing.value = props.startEditing }, { immediate: true })
watch(() => props.startEditing, (value) => { if(value)beginEdit() })
</script>

<template>
  <section class="product-detail-page">
    <div class="detail-nav"><el-button link :icon="ArrowLeft" @click="emit('back')">返回产品中心</el-button></div>
    <header class="product-hero">
      <div class="product-image"><img v-if="record.mainImage" :src="record.mainImage" :alt="record.name"><span v-else>{{ record.name.slice(0,1) }}</span></div>
      <div><div class="eyebrow">{{ typeName }} · {{ record.category }}</div><h1>{{ record.name }}</h1><p>{{ record.summary || '暂无一句话简介' }}</p><div class="hero-tags"><el-tag type="success" effect="plain">{{ record.status==='ON_SALE'?'在售':'停售' }}</el-tag><el-tag effect="plain">主型号 {{ record.modelCode }}</el-tag></div></div>
      <div v-if="canManage" class="hero-actions"><el-button v-if="!editing" :icon="Edit" @click="beginEdit">编辑产品</el-button><el-button type="danger" plain :icon="Delete" @click="emit('delete')">删除</el-button></div>
    </header>

    <div v-if="editing" class="edit-banner"><span>正在编辑产品知识</span><div><el-button @click="editing=false">取消</el-button><el-button type="primary" :icon="Select" @click="save">保存修改</el-button></div></div>

    <div class="product-layout">
      <main>
        <section class="product-section"><div class="section-head"><div><h2>产品概览</h2><p>基础身份、分类与销售状态。</p></div></div>
          <el-form v-if="editing" label-position="top" class="edit-grid"><el-form-item label="产品名称"><el-input v-model="draft.name" /></el-form-item><el-form-item label="产品类型"><el-select v-model="draft.product_type"><el-option v-for="item in productTypes" :key="item.value" :label="item.label" :value="item.value" /></el-select></el-form-item><el-form-item label="主型号"><el-input v-model="draft.model_code" /></el-form-item><el-form-item label="分类"><el-select v-model="draft.category_id"><el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" /></el-select></el-form-item><el-form-item label="销售状态"><el-select v-model="draft.status"><el-option label="在售" value="ON_SALE"/><el-option label="停售" value="OFF_SALE"/></el-select></el-form-item><el-form-item label="主图地址"><el-input v-model="draft.main_image" /></el-form-item><el-form-item label="一句话简介" class="span-2"><el-input v-model="draft.summary" type="textarea" :rows="3" /></el-form-item></el-form>
          <el-descriptions v-else :column="2" border><el-descriptions-item label="产品类型">{{ typeName }}</el-descriptions-item><el-descriptions-item label="分类">{{ record.category }}</el-descriptions-item><el-descriptions-item label="主型号">{{ record.modelCode }}</el-descriptions-item><el-descriptions-item label="销售状态">{{ record.status==='ON_SALE'?'在售':'停售' }}</el-descriptions-item><el-descriptions-item label="数据状态">已确认</el-descriptions-item><el-descriptions-item label="维护人">{{ record.owner || '产品管理部' }}</el-descriptions-item></el-descriptions>
        </section>

        <section class="product-section"><div class="section-head"><div><h2>产品参数</h2><p>字段根据产品类型推荐，产品经理可直接增删。</p></div><el-dropdown v-if="editing" trigger="click" @command="addField"><el-button :icon="Plus">添加推荐字段</el-button><template #dropdown><el-dropdown-menu><el-dropdown-item v-for="field in recommendations[draft.product_type]||[]" :key="field" :command="field">{{ field }}</el-dropdown-item><el-dropdown-item divided command="">自定义字段</el-dropdown-item></el-dropdown-menu></template></el-dropdown></div>
          <div v-if="editing" class="dynamic-editor"><div v-for="(field,index) in dynamicFields" :key="index"><el-input v-model="field.key" placeholder="字段名称"/><el-input v-model="field.value" placeholder="字段内容"/><el-button :icon="Remove" circle aria-label="删除字段" @click="dynamicFields.splice(index,1)"/></div><el-empty v-if="!dynamicFields.length" description="暂无参数字段" :image-size="56" /></div>
          <el-descriptions v-else-if="Object.keys(record.dynamicFields||{}).length" :column="2" border><el-descriptions-item v-for="(value,key) in record.dynamicFields" :key="key" :label="String(key)">{{ value }}</el-descriptions-item></el-descriptions><el-empty v-else description="暂无产品参数" :image-size="64" />
        </section>

        <section class="product-section"><div class="section-head"><div><h2>关联知识</h2><p>模型能力、软件、算法、场景与方案的真实关联。</p></div><el-button v-if="canManage" :icon="Link" @click="emit('relate','all')">选择关联</el-button></div><div v-if="allRelations.length" class="relation-grid"><button v-for="relation in allRelations" :key="relation.type+relation.id" @click="emit('openRelation',relation)"><strong>{{ relation.name }}</strong><small>{{ relation.category || relation.summary || '查看关联详情' }}</small></button></div><el-empty v-else description="暂无关联知识" :image-size="64" /></section>

        <section v-if="showPrice" class="product-section"><div class="section-head"><div><h2>价格信息</h2><p>仅具备价格查看权限的用户可见。</p></div><el-button v-if="canManage&&!priceEditing" :icon="Edit" @click="beginPriceEdit">维护价格</el-button></div><el-form v-if="priceEditing" label-position="top" class="edit-grid"><el-form-item label="参考价格"><el-input-number v-model="priceDraft.reference_price" :min="0" :precision="2" style="width:100%"/></el-form-item><el-form-item label="币种"><el-select v-model="priceDraft.currency"><el-option label="人民币" value="CNY"/></el-select></el-form-item><el-form-item label="含税"><el-switch v-model="priceDraft.tax_included"/></el-form-item><el-form-item label="税率 (%)"><el-input-number v-model="priceDraft.tax_rate" :min="0" :max="100"/></el-form-item><el-form-item label="有效期"><el-date-picker v-model="priceDraft.valid_until" type="date" value-format="YYYY-MM-DD"/></el-form-item><el-form-item label="备注"><el-input v-model="priceDraft.notes"/></el-form-item><div class="span-2 price-actions"><el-button @click="priceEditing=false">取消</el-button><el-button type="primary" @click="savePrice">保存价格</el-button></div></el-form><div v-else-if="record.price" class="price-value"><span>参考价格{{ record.price.taxIncluded?'（含税）':'（未税）' }}</span><strong>{{ record.price.currency }} {{ Number(record.price.referencePrice).toLocaleString() }}</strong></div><el-empty v-else description="暂无价格信息" :image-size="56" /></section>
      </main>
      <aside class="product-aside"><h3>维护信息</h3><dl><div><dt>创建来源</dt><dd>{{ record.source || '产品中心' }}</dd></div><div><dt>最近更新</dt><dd>{{ new Date(record.updatedAt).toLocaleDateString() }}</dd></div><div><dt>记录编号</dt><dd>#{{ record.id }}</dd></div></dl></aside>
    </div>
  </section>
</template>

<style scoped>
.product-detail-page{display:grid;gap:14px}.detail-nav{height:28px}.product-hero{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:22px;align-items:center;padding:24px;background:#fff;border:1px solid #e2e9f2;border-radius:8px}.product-image{display:grid;place-items:center;width:100px;height:100px;overflow:hidden;border-radius:8px;background:#eaf3ff;color:#146ef5;font-size:36px;font-weight:700}.product-image img{width:100%;height:100%;object-fit:cover}.eyebrow{font-size:12px;color:#146ef5;font-weight:700}.product-hero h1{margin:6px 0;font-size:26px;letter-spacing:0;color:#14233c}.product-hero p{margin:0;color:#66758d}.hero-tags{display:flex;gap:8px;margin-top:14px}.hero-actions{display:flex;gap:8px}.edit-banner{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:#eaf3ff;border:1px solid #bdd7ff;border-radius:8px;color:#1557aa;font-weight:600}.product-layout{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:16px}.product-layout main{display:grid;gap:16px}.product-section,.product-aside{padding:20px;background:#fff;border:1px solid #e2e9f2;border-radius:8px}.section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:16px}.section-head h2,.product-aside h3{margin:0;font-size:17px;letter-spacing:0;color:#192941}.section-head p{margin:5px 0 0;font-size:13px;color:#78869a}.edit-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 16px}.edit-grid .span-2{grid-column:1/-1}.edit-grid :deep(.el-select){width:100%}.dynamic-editor{display:grid;gap:10px}.dynamic-editor>div{display:grid;grid-template-columns:180px minmax(0,1fr) 34px;gap:8px}.relation-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.relation-grid button{display:grid;gap:4px;padding:13px;text-align:left;background:#f8fafc;border:1px solid #e3eaf2;border-radius:7px;cursor:pointer}.relation-grid strong{color:#20324b}.relation-grid small{color:#758398}.price-value{display:flex;align-items:baseline;justify-content:space-between;padding:18px;background:#f5f9ff;border-radius:7px}.price-value span{color:#6f7e92}.price-value strong{font-size:24px;color:#146ef5}.product-aside{align-self:start}.product-aside dl{margin:14px 0 0}.product-aside dl div{display:flex;justify-content:space-between;gap:12px;padding:11px 0;border-bottom:1px solid #edf1f5;font-size:13px}.product-aside dt{color:#78869a}.product-aside dd{margin:0;color:#273950;text-align:right}@media(max-width:1000px){.product-layout{grid-template-columns:1fr}.product-aside{order:-1}.relation-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:720px){.product-hero{grid-template-columns:auto 1fr}.hero-actions{grid-column:1/-1}.edit-grid{grid-template-columns:1fr}.edit-grid .span-2{grid-column:auto}.dynamic-editor>div{grid-template-columns:1fr 1fr 34px}.relation-grid{grid-template-columns:1fr}}
.price-actions{display:flex;justify-content:flex-end;gap:8px}
</style>
