<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Delete, Link, Search } from '@element-plus/icons-vue'

const props = defineProps<{ modelValue:boolean; sourceType:string; sourceId:number; relations:any[]; loadOptions:(type:string)=>Promise<any[]> }>()
const emit = defineEmits<{ 'update:modelValue':[value:boolean]; add:[payload:any]; remove:[relation:any] }>()
const targetType=ref('model-capabilities'),options=ref<any[]>([]),targetId=ref<number|null>(null),keyword=ref(''),loading=ref(false)
const metadata=ref({supportVersion:'',recommendedConcurrency:'',maxConcurrency:'',supportStatus:'SUPPORTED',purpose:'',relationLevel:'RECOMMENDED',recommendationReason:'',notes:''})
const centers=[{value:'products',label:'产品中心'},{value:'software',label:'软件中心'},{value:'algorithms',label:'算法中心'},{value:'model-capabilities',label:'模型能力中心'},{value:'scenes',label:'场景中心'},{value:'solutions',label:'方案中心'}]
const filtered=computed(()=>options.value.filter((item)=>!keyword.value||item.name.toLowerCase().includes(keyword.value.toLowerCase())))
async function refresh(){if(targetType.value===props.sourceType)targetType.value=centers.find((center)=>center.value!==props.sourceType)?.value||'products';loading.value=true;try{options.value=await props.loadOptions(targetType.value);targetId.value=options.value[0]?.id||null}finally{loading.value=false}}
function submit(){if(!targetId.value)return;emit('add',{source_type:props.sourceType,source_id:props.sourceId,target_type:targetType.value,target_id:targetId.value,metadata:Object.fromEntries(Object.entries(metadata.value).filter(([,value])=>value!==''))})}
watch(()=>props.modelValue,(open)=>{if(open)refresh()})
watch(targetType,refresh)
</script>

<template>
 <el-drawer :model-value="modelValue" title="选择关联知识" size="520px" @update:model-value="emit('update:modelValue',$event)">
  <div class="drawer-body">
   <section><h3>已关联</h3><div v-if="relations.length" class="current-relations"><div v-for="relation in relations" :key="relation.relationId||relation.type+relation.id"><span><strong>{{ relation.name }}</strong><small>{{ centers.find(c=>c.value===relation.type)?.label }}</small></span><el-tooltip v-if="relation.relationId" content="移除关联"><el-button :icon="Delete" circle type="danger" plain aria-label="移除关联" @click="emit('remove',relation)"/></el-tooltip></div></div><el-empty v-else description="暂无关联知识" :image-size="52"/></section>
   <el-divider />
   <section><h3>添加关联</h3><el-form label-position="top"><el-form-item label="目标中心"><el-select v-model="targetType" style="width:100%"><el-option v-for="center in centers.filter(c=>c.value!==sourceType)" :key="center.value" :label="center.label" :value="center.value"/></el-select></el-form-item><el-form-item label="搜索"><el-input v-model="keyword" :prefix-icon="Search" clearable /></el-form-item><el-form-item label="选择对象"><el-select v-model="targetId" filterable style="width:100%" v-loading="loading"><el-option v-for="item in filtered" :key="item.id" :label="item.name" :value="item.id"/></el-select></el-form-item><div class="meta-grid"><el-form-item label="支持版本"><el-input v-model="metadata.supportVersion"/></el-form-item><el-form-item label="支持状态"><el-select v-model="metadata.supportStatus"><el-option label="支持" value="SUPPORTED"/><el-option label="受限支持" value="LIMITED"/><el-option label="不支持" value="UNSUPPORTED"/></el-select></el-form-item><el-form-item label="推荐并发"><el-input v-model="metadata.recommendedConcurrency"/></el-form-item><el-form-item label="最大并发"><el-input v-model="metadata.maxConcurrency"/></el-form-item><el-form-item label="关系级别"><el-select v-model="metadata.relationLevel"><el-option label="核心" value="CORE"/><el-option label="推荐" value="RECOMMENDED"/><el-option label="可选" value="OPTIONAL"/></el-select></el-form-item><el-form-item label="用途"><el-input v-model="metadata.purpose"/></el-form-item><el-form-item label="推荐理由" class="span-2"><el-input v-model="metadata.recommendationReason" type="textarea" :rows="2"/></el-form-item><el-form-item label="备注" class="span-2"><el-input v-model="metadata.notes" type="textarea" :rows="2"/></el-form-item></div></el-form></section>
  </div>
  <template #footer><el-button @click="emit('update:modelValue',false)">取消</el-button><el-button type="primary" :icon="Link" :disabled="!targetId" @click="submit">建立关联</el-button></template>
 </el-drawer>
</template>

<style scoped>
.drawer-body{display:grid;gap:4px}.drawer-body h3{margin:0 0 12px;font-size:15px;color:#243650}.current-relations{display:grid;gap:8px}.current-relations>div{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 12px;background:#f7f9fc;border:1px solid #e6ebf2;border-radius:7px}.current-relations span{display:grid;gap:3px}.current-relations strong{font-size:14px;color:#21334c}.current-relations small{color:#77869a}.meta-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 12px}.span-2{grid-column:1/-1}.meta-grid :deep(.el-select){width:100%}@media(max-width:600px){.meta-grid{grid-template-columns:1fr}.span-2{grid-column:auto}}
</style>
