<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { Delete, Edit, Link, Search } from '@element-plus/icons-vue'

type Relation = { relationId?:number; relationType?:string; direction?:string; id:number; type:string; name:string; meta?:Record<string,string|number|boolean> }
const props = defineProps<{ modelValue:boolean; sourceType:string; sourceId:number; relations:Relation[]; loadOptions:(type:string)=>Promise<any[]> }>()
const emit = defineEmits<{ 'update:modelValue':[value:boolean]; add:[payload:any]; edit:[relationId:number,payload:any]; remove:[relation:Relation] }>()

const centers=[{value:'products',label:'产品中心'},{value:'software',label:'软件中心'},{value:'algorithms',label:'算法中心'},{value:'model-capabilities',label:'模型能力中心'},{value:'scenes',label:'场景中心'},{value:'solutions',label:'方案中心'}]
const relationTypes=[{value:'SUPPORT',label:'支持/依赖'},{value:'COMMERCIALIZATION',label:'商业化映射'},{value:'RECOMMENDATION',label:'推荐'},{value:'COMPOSITION',label:'组成'},{value:'RELATED',label:'一般关联'}]
const metadataRules:Record<string,string[]>={
  'products:model-capabilities':['supportVersion','recommendedConcurrency','maxConcurrency','supportStatus','notes'],
  'products:software':['minimumVersion','supportStatus','purpose','notes'],
  'products:algorithms':['supportVersion','purpose','supportStatus','notes'],
  'products:scenes':['relationLevel','recommendationReason','purpose','notes'],
  'model-capabilities:scenes':['requirementLevel','purpose','condition','notes'],
  'scenes:solutions':['solutionLevel','recommended','recommendationReason','notes'],
}
const fallbackMetadata=['purpose','supportStatus','recommendationReason','notes']
const fieldLabels:Record<string,string>={supportVersion:'支持版本',minimumVersion:'最低版本',recommendedConcurrency:'推荐并发',maxConcurrency:'最大并发',supportStatus:'支持状态',purpose:'用途',relationLevel:'关系级别',requirementLevel:'需求级别',condition:'适用条件',solutionLevel:'方案级别',recommended:'是否推荐',recommendationReason:'推荐理由',notes:'备注'}

const targetType=ref('model-capabilities'),options=ref<any[]>([]),targetId=ref<number|null>(null),keyword=ref(''),loading=ref(false),editingRelation=ref<Relation|null>(null),relationType=ref('SUPPORT')
const metadata=reactive<Record<string,string|number|boolean>>({})
const filtered=computed(()=>options.value.filter((item)=>!keyword.value||item.name.toLowerCase().includes(keyword.value.toLowerCase())))
const pairKey=computed(()=>metadataRules[`${props.sourceType}:${targetType.value}`]?`${props.sourceType}:${targetType.value}`:`${targetType.value}:${props.sourceType}`)
const allowedMetadata=computed(()=>metadataRules[pairKey.value]||fallbackMetadata)
const selectableRelationTypes=computed(()=>relationTypes.filter((item)=>item.value!=='COMMERCIALIZATION'||(props.sourceType==='products'&&targetType.value==='software')))
const isEditing=computed(()=>Boolean(editingRelation.value?.relationId))

function defaultRelationType(){if(props.sourceType==='products'&&['software','algorithms','model-capabilities'].includes(targetType.value))return 'SUPPORT';if([props.sourceType,targetType.value].includes('scenes'))return 'RECOMMENDATION';if([props.sourceType,targetType.value].includes('solutions'))return 'COMPOSITION';return 'RELATED'}
function clearMetadata(values:Record<string,any>={}){Object.keys(metadata).forEach((key)=>delete metadata[key]);allowedMetadata.value.forEach((key)=>{metadata[key]=values[key]??''})}
async function refresh(){if(targetType.value===props.sourceType)targetType.value=centers.find((center)=>center.value!==props.sourceType)?.value||'products';loading.value=true;try{options.value=await props.loadOptions(targetType.value);targetId.value=options.value[0]?.id||null}finally{loading.value=false}}
function cleanMetadata(){return Object.fromEntries(allowedMetadata.value.flatMap((key)=>{const value=metadata[key];if(value===''||value===null||value===undefined)return[];if(['recommendedConcurrency','maxConcurrency'].includes(key))return[[key,Number(value)]];return[[key,value]]}))}
function submit(){const payload={relationType:relationType.value,metadata:cleanMetadata()};if(editingRelation.value?.relationId){emit('edit',editingRelation.value.relationId,payload);return}if(!targetId.value)return;emit('add',{sourceType:props.sourceType,sourceId:props.sourceId,targetType:targetType.value,targetId:targetId.value,...payload})}
async function beginEdit(relation:Relation){
  if(!relation.relationId)return
  editingRelation.value=relation
  targetType.value=relation.type
  loading.value=true
  try{
    options.value=await props.loadOptions(relation.type)
    targetId.value=relation.id
  }finally{
    loading.value=false
  }
  relationType.value=relation.relationType||'RELATED'
  clearMetadata(relation.meta||{})
}
function cancelEdit(){editingRelation.value=null;relationType.value=defaultRelationType();clearMetadata()}
function relationTypeLabel(value?:string){return relationTypes.find((item)=>item.value===value)?.label||'一般关联'}

watch(()=>props.modelValue,async(open)=>{if(!open)return;editingRelation.value=null;await refresh();relationType.value=defaultRelationType();clearMetadata()})
watch(targetType,async()=>{if(isEditing.value)return;await refresh();relationType.value=defaultRelationType();clearMetadata()})
</script>

<template>
 <el-drawer :model-value="modelValue" title="维护关联知识" size="540px" @update:model-value="emit('update:modelValue',$event)">
  <div class="drawer-body">
   <section><h3>已关联</h3><div v-if="relations.length" class="current-relations"><div v-for="relation in relations" :key="relation.relationId||relation.type+relation.id"><span><strong>{{ relation.name }}</strong><small>{{ centers.find(center=>center.value===relation.type)?.label }} · {{ relationTypeLabel(relation.relationType) }}</small></span><div class="relation-actions"><el-tooltip v-if="relation.relationId" content="编辑关系"><el-button :icon="Edit" circle plain aria-label="编辑关系" @click="beginEdit(relation)"/></el-tooltip><el-tooltip v-if="relation.relationId" content="移除关联"><el-button :icon="Delete" circle type="danger" plain aria-label="移除关联" @click="emit('remove',relation)"/></el-tooltip></div></div></div><el-empty v-else description="暂无关联知识" :image-size="52"/></section>
   <el-divider/>
   <section><div class="form-title"><h3>{{ isEditing?'编辑关系':'添加关联' }}</h3><el-button v-if="isEditing" link @click="cancelEdit">取消编辑</el-button></div><el-form label-position="top"><el-form-item label="目标中心"><el-select v-model="targetType" :disabled="isEditing" style="width:100%"><el-option v-for="center in centers.filter(item=>item.value!==sourceType)" :key="center.value" :label="center.label" :value="center.value"/></el-select></el-form-item><el-form-item v-if="!isEditing" label="搜索"><el-input v-model="keyword" :prefix-icon="Search" clearable/></el-form-item><el-form-item label="选择对象"><el-select v-model="targetId" :disabled="isEditing" filterable style="width:100%" v-loading="loading"><el-option v-for="item in filtered" :key="item.id" :label="item.name" :value="item.id"/></el-select></el-form-item><el-form-item label="关系类型"><el-select v-model="relationType" style="width:100%"><el-option v-for="item in selectableRelationTypes" :key="item.value" :label="item.label" :value="item.value"/></el-select></el-form-item><div class="meta-grid"><el-form-item v-for="field in allowedMetadata" :key="field" :label="fieldLabels[field]" :class="{'span-2':['recommendationReason','notes','condition'].includes(field)}"><el-select v-if="field==='supportStatus'" v-model="metadata[field]"><el-option label="支持" value="SUPPORTED"/><el-option label="受限支持" value="LIMITED"/><el-option label="不支持" value="UNSUPPORTED"/></el-select><el-select v-else-if="field==='relationLevel'||field==='requirementLevel'" v-model="metadata[field]"><el-option label="核心/必需" :value="field==='relationLevel'?'CORE':'REQUIRED'"/><el-option label="推荐" value="RECOMMENDED"/><el-option label="可选" value="OPTIONAL"/></el-select><el-switch v-else-if="field==='recommended'" v-model="metadata[field]"/><el-input-number v-else-if="field==='recommendedConcurrency'||field==='maxConcurrency'" v-model="metadata[field]" :min="0" style="width:100%"/><el-input v-else v-model="metadata[field]" :type="['recommendationReason','notes','condition'].includes(field)?'textarea':'text'" :rows="2"/></el-form-item></div></el-form></section>
  </div>
  <template #footer><el-button @click="emit('update:modelValue',false)">关闭</el-button><el-button type="primary" :icon="Link" :disabled="!targetId" @click="submit">{{ isEditing?'保存关系':'建立关联' }}</el-button></template>
 </el-drawer>
</template>

<style scoped>
.drawer-body{display:grid;gap:4px}.drawer-body h3{margin:0 0 12px;font-size:15px;color:#243650}.form-title{display:flex;align-items:center;justify-content:space-between}.current-relations{display:grid;gap:8px}.current-relations>div{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 12px;background:#f7f9fc;border:1px solid #e6ebf2;border-radius:7px}.current-relations span{display:grid;gap:3px;min-width:0}.current-relations strong,.current-relations small{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.current-relations strong{font-size:14px;color:#21334c}.current-relations small{color:#77869a}.relation-actions{display:flex;flex:0 0 auto;gap:6px}.meta-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 12px}.span-2{grid-column:1/-1}.meta-grid :deep(.el-select){width:100%}@media(max-width:600px){.meta-grid{grid-template-columns:1fr}.span-2{grid-column:auto}}
</style>
