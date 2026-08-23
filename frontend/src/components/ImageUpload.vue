<script setup lang="ts">
import { ref } from 'vue'
import { Picture, Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

defineProps<{ modelValue?: string; label?: string }>()
const emit = defineEmits<{ 'update:modelValue':[value:string]; uploaded:[asset:any] }>()
const input = ref<HTMLInputElement|null>(null)
const uploading = ref(false)

async function selectFile(event:Event){
  const file=(event.target as HTMLInputElement).files?.[0]
  if(!file)return
  const body=new FormData();body.append('file',file);uploading.value=true
  try{
    const response=await fetch('/api/media/images',{method:'POST',headers:{Authorization:'Bearer '+localStorage.hzToken},body})
    const data=await response.json()
    if(!response.ok)throw Error(data?.detail||'图片上传失败')
    emit('update:modelValue',data.url);emit('uploaded',data);ElMessage.success('图片上传成功')
  }catch(error:any){ElMessage.error(error.message||'图片上传失败')}
  finally{uploading.value=false;if(input.value)input.value.value=''}
}
</script>

<template>
  <div class="image-upload">
    <div class="preview"><img v-if="modelValue" :src="modelValue" :alt="label||'已上传图片'"><el-icon v-else><Picture/></el-icon></div>
    <div class="upload-actions"><span>{{ label || '图片' }}</span><el-button :icon="Upload" :loading="uploading" @click="input?.click()">上传图片</el-button></div>
    <input ref="input" type="file" accept="image/*" hidden @change="selectFile">
  </div>
</template>

<style scoped>
.image-upload{display:grid;grid-template-columns:104px 1fr;gap:12px;align-items:center;padding:10px;border:1px solid #dfe7f1;border-radius:7px;background:#f8fafc}.preview{display:grid;place-items:center;width:104px;height:74px;overflow:hidden;border-radius:5px;background:#eaf1f8;color:#7b8ca3}.preview img{width:100%;height:100%;object-fit:cover}.preview :deep(.el-icon){font-size:25px}.upload-actions{display:flex;align-items:center;justify-content:space-between;gap:10px}.upload-actions span{font-size:13px;color:#52637a}@media(max-width:600px){.image-upload{grid-template-columns:1fr}.preview{width:100%;height:130px}}
</style>
