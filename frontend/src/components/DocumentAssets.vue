<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { Delete, Download, Upload, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props=withDefaults(defineProps<{centerType:string;centerId:number;canManage?:boolean;canDownload?:boolean}>(),{canManage:false,canDownload:false})
const rows=ref<any[]>([]),loading=ref(false),uploading=ref(false),input=ref<HTMLInputElement|null>(null)
const headers=()=>({Authorization:'Bearer '+localStorage.hzToken})
async function load(){loading.value=true;try{const response=await fetch(`/api/documents?center_type=${encodeURIComponent(props.centerType)}&center_id=${props.centerId}`,{headers:headers()});const data=await response.json();if(!response.ok)throw Error(data?.detail||'资料加载失败');rows.value=data}catch(error:any){ElMessage.error(error.message)}finally{loading.value=false}}
async function upload(event:Event){const file=(event.target as HTMLInputElement).files?.[0];if(!file)return;const body=new FormData();body.append('file',file);body.append('center_type',props.centerType);body.append('center_id',String(props.centerId));uploading.value=true;try{const response=await fetch('/api/documents',{method:'POST',headers:headers(),body});const data=await response.json();if(!response.ok)throw Error(data?.detail||'上传失败');await load();ElMessage.success('资料上传成功')}catch(error:any){ElMessage.error(error.message)}finally{uploading.value=false;if(input.value)input.value.value=''}}
async function openAsset(item:any,mode:'preview'|'download'){const response=await fetch(`/api/documents/${item.id}/${mode}`,{headers:headers()});if(!response.ok){const data=await response.json().catch(()=>null);throw Error(data?.detail||'文件读取失败')}const blob=await response.blob();const url=URL.createObjectURL(blob);if(mode==='preview'){window.open(url,'_blank','noopener,noreferrer');setTimeout(()=>URL.revokeObjectURL(url),60000)}else{const link=document.createElement('a');link.href=url;link.download=item.name;link.click();URL.revokeObjectURL(url)}}
async function remove(item:any){await ElMessageBox.confirm(`确认删除“${item.name}”？`,'删除资料',{type:'warning'});const response=await fetch('/api/documents/'+item.id,{method:'DELETE',headers:headers()});if(!response.ok){const data=await response.json().catch(()=>null);throw Error(data?.detail||'删除失败')}await load();ElMessage.success('资料已删除')}
async function run(action:()=>Promise<void>){try{await action()}catch(error:any){ElMessage.error(error.message||'操作失败')}}
watch(()=>[props.centerType,props.centerId],load);onMounted(load)
</script>

<template>
  <div class="assets" v-loading="loading">
    <div class="asset-toolbar"><div><h3>相关资料</h3><p>支持在线预览；下载由独立后台权限控制。</p></div><el-button v-if="canManage" type="primary" :icon="Upload" :loading="uploading" @click="input?.click()">上传文件</el-button><input ref="input" hidden type="file" @change="upload"></div>
    <div v-if="rows.length" class="asset-list"><article v-for="item in rows" :key="item.id"><div class="file-mark">{{ item.name.split('.').pop()?.slice(0,4).toUpperCase() }}</div><span><strong>{{ item.name }}</strong><small>{{ item.mimeType }} · {{ new Date(item.updatedAt).toLocaleDateString() }}</small></span><div><el-tooltip content="在线预览"><el-button circle plain :icon="View" aria-label="在线预览" @click="run(()=>openAsset(item,'preview'))"/></el-tooltip><el-tooltip v-if="canDownload&&item.canDownload" content="下载"><el-button circle plain :icon="Download" aria-label="下载" @click="run(()=>openAsset(item,'download'))"/></el-tooltip><el-tooltip v-if="canManage" content="删除"><el-button circle plain type="danger" :icon="Delete" aria-label="删除资料" @click="run(()=>remove(item))"/></el-tooltip></div></article></div>
    <el-empty v-else description="暂无相关资料" :image-size="64"/>
  </div>
</template>

<style scoped>
.assets{min-height:140px}.asset-toolbar{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:14px}.asset-toolbar h3{margin:0;font-size:16px}.asset-toolbar p{margin:5px 0 0;color:#77869a;font-size:12px}.asset-list{display:grid;gap:8px}.asset-list article{display:grid;grid-template-columns:44px minmax(0,1fr) auto;gap:11px;align-items:center;padding:11px;border:1px solid #e4eaf2;border-radius:6px;background:#f8fafc}.file-mark{display:grid;place-items:center;height:38px;border-radius:5px;background:#e8f2ff;color:#146ef5;font-size:10px;font-weight:800}.asset-list span{display:grid;min-width:0}.asset-list strong{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.asset-list small{margin-top:3px;color:#7b899c}.asset-list article>div:last-child{display:flex;gap:6px}@media(max-width:600px){.asset-toolbar{align-items:stretch;flex-direction:column}.asset-list article{grid-template-columns:38px minmax(0,1fr)}.asset-list article>div:last-child{grid-column:2}}
</style>
