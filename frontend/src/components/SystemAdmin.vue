<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Connection, Delete, Edit, Plus, Refresh, UserFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props=defineProps<{token:string}>()
const users=ref<any[]>([]),roles=ref<any[]>([]),permissions=ref<any[]>([]),directory=ref<any>({}),candidates=ref<any[]>([]),selected=ref<any[]>([])
const loading=ref(false),syncing=ref(false),testingDirectory=ref(false),savingDirectory=ref(false),confirming=ref(false),userDialog=ref(false),roleDialog=ref(false),editingUser=ref<any>(null),editingRole=ref<any>(null)
const userForm=reactive<any>({username:'',display_name:'',password:'',role_code:'',email:'',department:'',enabled:true})
const roleForm=reactive<any>({code:'',name:'',permissions:[]})
const directoryForm=reactive<any>({enabled:false,server_type:'MS_ACTIVE_DIRECTORY',protocol:'LDAP',host:'',port:389,timeout_seconds:30,bind_dn:'',bind_password:'',base_dn:'',login_domain:'',user_filter:'(&(objectClass=user)(sAMAccountName=*))',default_role:'sales'})
const candidateRoles=reactive<Record<number,string>>({})
const pendingRunId=computed(()=>directory.value.lastRun?.status==='PENDING_CONFIRMATION'?directory.value.lastRun.id:null)

async function api(url:string,options:any={}){const response=await fetch(url,{...options,headers:{'Content-Type':'application/json',Authorization:'Bearer '+props.token,...(options.headers||{})}});const data=response.status===204?null:await response.json();if(!response.ok)throw Error(data?.detail||'请求失败');return data}
function applyDirectory(value:any){Object.assign(directoryForm,{enabled:value.enabled,server_type:value.serverType,protocol:value.protocol,host:value.host,port:value.port,timeout_seconds:value.timeoutSeconds,bind_dn:value.bindDn,bind_password:'',base_dn:value.baseDn,login_domain:value.loginDomain,user_filter:value.userFilter,default_role:value.defaultRole})}
async function load(){loading.value=true;try{[users.value,roles.value,permissions.value,directory.value]=await Promise.all([api('/api/admin/users'),api('/api/admin/roles'),api('/api/admin/permissions'),api('/api/admin/directory/status')]);applyDirectory(directory.value);if(pendingRunId.value)await loadCandidates(pendingRunId.value)}finally{loading.value=false}}
async function loadCandidates(runId?:number){const result=await api('/api/admin/directory/candidates'+(runId?'?run_id='+runId:''));candidates.value=result.items||[];selected.value=[];for(const item of candidates.value)candidateRoles[item.id]=item.roleCode||directory.value.defaultRole||'sales'}
function addUser(){editingUser.value=null;Object.assign(userForm,{username:'',display_name:'',password:'',role_code:roles.value[0]?.code||'',email:'',department:'',enabled:true});userDialog.value=true}
function editUser(row:any){editingUser.value=row;Object.assign(userForm,{username:row.username,display_name:row.displayName,password:'',role_code:row.roleCode,email:row.email,department:row.department,enabled:row.enabled});userDialog.value=true}
async function saveUser(){const body={...userForm};if(editingUser.value){delete body.username;if(!body.password)delete body.password}await api(editingUser.value?'/api/admin/users/'+editingUser.value.id:'/api/admin/users',{method:editingUser.value?'PATCH':'POST',body:JSON.stringify(body)});userDialog.value=false;ElMessage.success('用户已保存');await load()}
async function removeUser(row:any){await ElMessageBox.confirm('确认删除用户 '+row.username+'？','删除用户',{type:'warning'});await api('/api/admin/users/'+row.id,{method:'DELETE'});ElMessage.success('用户已删除');await load()}
function addRole(){editingRole.value=null;Object.assign(roleForm,{code:'role_'+Date.now(),name:'',permissions:[]});roleDialog.value=true}
function editRole(row:any){editingRole.value=row;Object.assign(roleForm,{code:row.code,name:row.name,permissions:[...row.permissions]});roleDialog.value=true}
async function saveRole(){const body={name:roleForm.name,permissions:roleForm.permissions,...(!editingRole.value?{code:roleForm.code}:{})};await api(editingRole.value?'/api/admin/roles/'+editingRole.value.code:'/api/admin/roles',{method:editingRole.value?'PATCH':'POST',body:JSON.stringify(body)});roleDialog.value=false;ElMessage.success('角色与权限已保存');await load()}
async function removeRole(row:any){await ElMessageBox.confirm('确认删除角色 '+row.name+'？','删除角色',{type:'warning'});await api('/api/admin/roles/'+row.code,{method:'DELETE'});ElMessage.success('角色已删除');await load()}
function selectionChanged(rows:any[]){selected.value=rows}
async function testDirectory(){testingDirectory.value=true;try{const result=await api('/api/admin/directory/test',{method:'POST',body:JSON.stringify(directoryForm)});directory.value.lastTestStatus='SUCCESS';directory.value.lastTestMessage=result.message;ElMessage.success(result.message)}catch(error:any){directory.value.lastTestStatus='FAILED';directory.value.lastTestMessage=error.message;ElMessage.error(error.message)}finally{testingDirectory.value=false}}
async function saveDirectory(){savingDirectory.value=true;try{await api('/api/admin/directory/config',{method:'PUT',body:JSON.stringify(directoryForm)});ElMessage.success('AD 域配置已保存');const value=await api('/api/admin/directory/status');directory.value=value;applyDirectory(value)}catch(error:any){ElMessage.error(error.message)}finally{savingDirectory.value=false}}
async function syncAd(){syncing.value=true;try{const result=await api('/api/admin/directory/sync',{method:'POST'});candidates.value=result.items||[];for(const item of candidates.value)candidateRoles[item.id]=item.roleCode||directory.value.defaultRole||'sales';selected.value=[];ElMessage.success(`已读取 ${candidates.value.length} 个域用户，请勾选允许登录的人员`);await load()}catch(error:any){ElMessage.error(error.message)}finally{syncing.value=false}}
async function confirmAd(){if(!selected.value.length){ElMessage.warning('请先勾选允许登录系统的域用户');return}await ElMessageBox.confirm(`确认允许选中的 ${selected.value.length} 个域用户登录系统？未勾选用户不会保存。`,'确认域用户',{type:'warning'});confirming.value=true;try{const result=await api('/api/admin/directory/confirm',{method:'POST',body:JSON.stringify({run_id:pendingRunId.value,users:selected.value.map(item=>({candidate_id:item.id,role_code:candidateRoles[item.id]}))})});ElMessage.success(`已保存 ${result.selected} 个域用户`);candidates.value=[];selected.value=[];await load()}finally{confirming.value=false}}
const changeText=(value:string)=>value==='CREATE'?'新增用户':value==='UPDATE'?'资料更新':'无变化'
onMounted(load)
</script>

<template>
<section class="system-page" v-loading="loading">
  <div class="page-head"><div><h1>系统管理</h1><p>统一管理本地用户、AD 域用户、中文角色与敏感权限。</p></div></div>
  <el-tabs>
    <el-tab-pane label="用户管理">
      <div class="toolbar"><el-button type="primary" :icon="Plus" @click="addUser">新增用户</el-button></div>
      <el-table :data="users" border><el-table-column prop="username" label="账号"/><el-table-column prop="displayName" label="姓名"/><el-table-column prop="department" label="部门"/><el-table-column prop="email" label="邮箱"/><el-table-column prop="roleName" label="角色"/><el-table-column label="来源"><template #default="scope"><el-tag :type="scope.row.authSource==='AD'?'success':'info'">{{scope.row.authSource==='AD'?'AD 域':'本地'}}</el-tag></template></el-table-column><el-table-column label="状态"><template #default="scope">{{scope.row.enabled?'启用':'停用'}}</template></el-table-column><el-table-column width="110"><template #default="scope"><el-button link :icon="Edit" title="编辑" @click="editUser(scope.row)"/><el-button link type="danger" :icon="Delete" title="删除" @click="removeUser(scope.row)"/></template></el-table-column></el-table>
    </el-tab-pane>
    <el-tab-pane label="角色与权限">
      <div class="toolbar"><el-button type="primary" :icon="Plus" @click="addRole">新增角色</el-button></div>
      <el-table :data="roles" border><el-table-column prop="name" label="角色名称"/><el-table-column label="权限"><template #default="scope"><el-tag v-for="code in scope.row.permissions" :key="code" effect="plain">{{permissions.find(item=>item.code===code)?.name||'系统权限'}}</el-tag></template></el-table-column><el-table-column width="110"><template #default="scope"><el-button link :icon="Edit" title="编辑" @click="editRole(scope.row)"/><el-button link type="danger" :icon="Delete" title="删除" @click="removeRole(scope.row)"/></template></el-table-column></el-table>
    </el-tab-pane>
    <el-tab-pane label="AD 域用户">
      <article class="directory-card">
        <div class="enable-row"><div><el-icon><UserFilled/></el-icon><span><strong>启用 LDAP 同步</strong><small>配置保存并启用后，管理员才能手动读取域用户。</small></span></div><el-switch v-model="directoryForm.enabled"/></div>
        <div class="section-title">基本配置</div>
        <el-form label-position="left" label-width="128px" class="directory-form">
          <el-form-item label="服务器类型"><el-select v-model="directoryForm.server_type"><el-option label="MS Active Directory" value="MS_ACTIVE_DIRECTORY"/></el-select></el-form-item>
          <el-form-item label="服务器地址"><div class="address-row"><el-select v-model="directoryForm.protocol"><el-option label="LDAP" value="LDAP"/><el-option label="LDAPS" value="LDAPS"/></el-select><el-input v-model="directoryForm.host" placeholder="例如：10.1.1.102"/></div></el-form-item>
          <el-form-item label="认证端口"><el-input-number v-model="directoryForm.port" :min="1" :max="65535" controls-position="right"/></el-form-item>
          <el-form-item label="超时设置（秒）"><el-input-number v-model="directoryForm.timeout_seconds" :min="1" :max="300" controls-position="right"/></el-form-item>
          <el-form-item label="管理员账号"><el-input v-model="directoryForm.bind_dn" placeholder="例如：CN=LDAP Reader,OU=Service Accounts,DC=example,DC=com"/></el-form-item>
          <el-form-item label="管理密码"><el-input v-model="directoryForm.bind_password" type="password" show-password autocomplete="new-password" :placeholder="directory.passwordConfigured?'已配置；留空表示不修改':'请输入管理密码'"/></el-form-item>
          <el-form-item label="Base DN"><el-input v-model="directoryForm.base_dn" placeholder="例如：OU=公司名称,DC=example,DC=com"/></el-form-item>
          <el-form-item label="登录域"><el-input v-model="directoryForm.login_domain" placeholder="例如：example.com"/></el-form-item>
          <el-form-item label="用户过滤条件"><el-input v-model="directoryForm.user_filter"/></el-form-item>
          <el-form-item label="新用户默认角色"><el-select v-model="directoryForm.default_role"><el-option v-for="role in roles" :key="role.code" :label="role.name" :value="role.code"/></el-select></el-form-item>
        </el-form>
        <el-alert v-if="directory.lastTestStatus==='SUCCESS'" :title="directory.lastTestMessage" type="success" :closable="false" show-icon/>
        <el-alert v-else-if="directory.lastTestStatus==='FAILED'" :title="directory.lastTestMessage" type="error" :closable="false" show-icon/>
        <div class="directory-actions"><el-button :icon="Connection" :loading="testingDirectory" @click="testDirectory">连通性测试</el-button><el-button type="primary" :loading="savingDirectory" @click="saveDirectory">保存配置</el-button><el-button type="primary" plain :icon="Refresh" :loading="syncing" :disabled="!directory.configured" @click="syncAd">手动同步域用户</el-button></div>
        <el-alert v-if="directory.lastRun?.status==='FAILED'" :title="directory.lastRun.error" type="error" :closable="false" show-icon/>
      </article>
      <section v-if="candidates.length" class="candidate-panel">
        <div class="candidate-head"><div><h3>待确认域用户</h3><p>只有勾选并确认的用户才会保存到系统；后续资料变化仍需手动再次同步确认。</p></div><el-button type="primary" :loading="confirming" @click="confirmAd">确认选中用户（{{selected.length}}）</el-button></div>
        <el-table :data="candidates" border @selection-change="selectionChanged"><el-table-column type="selection" width="48"/><el-table-column prop="username" label="域账号"/><el-table-column prop="displayName" label="姓名"/><el-table-column prop="department" label="部门"/><el-table-column prop="email" label="邮箱"/><el-table-column label="变化"><template #default="scope"><el-tag :type="scope.row.changeType==='CREATE'?'success':'warning'">{{changeText(scope.row.changeType)}}</el-tag></template></el-table-column><el-table-column label="登录角色" min-width="150"><template #default="scope"><el-select v-model="candidateRoles[scope.row.id]"><el-option v-for="role in roles" :key="role.code" :label="role.name" :value="role.code"/></el-select></template></el-table-column></el-table>
      </section>
    </el-tab-pane>
  </el-tabs>
  <el-dialog v-model="userDialog" :title="editingUser?'编辑用户':'新增用户'" width="620px"><el-form label-position="top" class="grid"><el-form-item label="账号"><el-input v-model="userForm.username" :disabled="!!editingUser"/></el-form-item><el-form-item label="姓名"><el-input v-model="userForm.display_name"/></el-form-item><el-form-item :label="editingUser?'重置密码（留空不修改）':'初始密码'"><el-input v-model="userForm.password" type="password" show-password :disabled="editingUser?.authSource==='AD'"/></el-form-item><el-form-item label="角色"><el-select v-model="userForm.role_code"><el-option v-for="item in roles" :key="item.code" :label="item.name" :value="item.code"/></el-select></el-form-item><el-form-item label="部门"><el-input v-model="userForm.department"/></el-form-item><el-form-item label="邮箱"><el-input v-model="userForm.email"/></el-form-item><el-form-item label="启用"><el-switch v-model="userForm.enabled"/></el-form-item></el-form><template #footer><el-button @click="userDialog=false">取消</el-button><el-button type="primary" @click="saveUser">保存</el-button></template></el-dialog>
  <el-dialog v-model="roleDialog" :title="editingRole?'编辑角色':'新增角色'" width="700px"><el-form label-position="top"><el-form-item label="角色名称"><el-input v-model="roleForm.name" placeholder="请输入中文角色名称"/></el-form-item><el-form-item label="权限"><el-checkbox-group v-model="roleForm.permissions" class="permission-grid"><el-checkbox v-for="item in permissions" :key="item.code" :value="item.code"><span><b>{{item.name}}</b><small>{{item.description}}</small></span></el-checkbox></el-checkbox-group></el-form-item></el-form><template #footer><el-button @click="roleDialog=false">取消</el-button><el-button type="primary" @click="saveRole">保存</el-button></template></el-dialog>
</section>
</template>

<style scoped>
.system-page{display:grid;gap:14px}.page-head{display:flex;justify-content:space-between}.page-head h1{margin:0;font-size:26px}.page-head p{margin:6px 0;color:#69788c}.system-page :deep(.el-tabs){padding:16px 18px;background:#fff;border:1px solid #e2e9f2;border-radius:8px}.toolbar{display:flex;justify-content:flex-end;margin-bottom:12px}.system-page :deep(.el-tag){margin:2px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:0 14px}.grid :deep(.el-select){width:100%}.permission-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;width:100%}.permission-grid :deep(.el-checkbox){height:auto;margin:0;padding:10px;border:1px solid #e2e9f2}.permission-grid span{display:grid}.permission-grid small{color:#8290a2;white-space:normal}.directory-card,.candidate-panel{display:grid;gap:16px;padding:18px;border:1px solid #dfe7f0;border-radius:7px}.enable-row,.enable-row>div{display:flex;align-items:center;gap:12px}.enable-row{justify-content:space-between;padding:10px 0 16px;border-bottom:1px solid #e8edf3}.enable-row span{display:grid}.enable-row small{color:#758398}.section-title{padding-left:10px;border-left:3px solid #2f74e8;font-weight:700}.directory-form{max-width:820px}.directory-form :deep(.el-form-item){margin-bottom:14px}.directory-form :deep(.el-select),.directory-form :deep(.el-input-number){width:100%}.address-row{display:grid;grid-template-columns:120px 1fr;gap:8px;width:100%}.directory-actions{display:flex;justify-content:flex-end;gap:8px}.candidate-panel{margin-top:16px}.candidate-head{display:flex;align-items:center;justify-content:space-between;gap:20px}.candidate-head h3{margin:0;font-size:17px}.candidate-head p{margin:5px 0 0;color:#758398}.candidate-panel :deep(.el-select){width:100%}@media(max-width:720px){.grid,.permission-grid{grid-template-columns:1fr}.candidate-head,.directory-actions{align-items:flex-start;flex-direction:column}.address-row{grid-template-columns:1fr}.directory-actions .el-button{width:100%;margin:0}}
</style>
