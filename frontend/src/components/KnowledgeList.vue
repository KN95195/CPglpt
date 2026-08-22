<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Grid, List, Plus, Refresh, Search } from '@element-plus/icons-vue'

export type KnowledgeRow = {
  id: number
  name: string
  summary?: string
  status?: string
  modelCode?: string
  category?: string
  version?: string
  scene?: string
  tier?: string
  updatedAt?: string
}

const props = withDefaults(defineProps<{
  title: string
  centerKey: string
  description: string
  rows: KnowledgeRow[]
  loading?: boolean
  error?: string
  canManage?: boolean
  searchPlaceholder?: string
}>(), {
  loading: false,
  error: '',
  canManage: false,
  searchPlaceholder: '搜索名称、分类或简介',
})

const emit = defineEmits<{
  create: []
  open: [row: KnowledgeRow]
  edit: [row: KnowledgeRow]
  delete: [row: KnowledgeRow]
  retry: []
}>()

const keyword = ref('')
const status = ref('全部状态')
const viewMode = ref<'card' | 'list'>('card')
const visibleRows = computed(() => {
  const needle = keyword.value.trim().toLocaleLowerCase()
  return props.rows.filter((row) => {
    const matchesKeyword = !needle || [row.name, row.summary, row.modelCode, row.category, row.version, row.scene, row.tier]
      .filter(Boolean).join(' ').toLocaleLowerCase().includes(needle)
    const matchesStatus = status.value === '全部状态' || statusLabel(row.status) === status.value
    return matchesKeyword && matchesStatus
  })
})

const supportedCount = computed(() => props.rows.filter((row) => !row.status || ['SUPPORTED', 'ON_SALE', 'ACTIVE', 'PUBLISHED'].includes(row.status)).length)
const centerNoun = computed(() => ({software:'软件资产',algorithms:'算法资产','model-capabilities':'模型能力',scenes:'业务场景',solutions:'标准方案'} as Record<string,string>)[props.centerKey] || '知识对象')
const symbol = computed(() => ({software:'SW',algorithms:'ALG','model-capabilities':'AI',scenes:'SC',solutions:'SOL'} as Record<string,string>)[props.centerKey] || 'HZ')
watch(() => props.title, () => { keyword.value = ''; status.value = '全部状态' })

function statusLabel(value?: string) {
  return ({ SUPPORTED: '正式支持', ON_SALE: '在售', OFF_SALE: '停售', ACTIVE: '启用', PUBLISHED: '已发布', DRAFT: '草稿', BETA: 'Beta', DISABLED: '停用', PLANNING: '规划中' } as Record<string, string>)[value || ''] || '状态待确认'
}

function sceneImage(value?: string) {
  return value && !/\/(?:product-(?:terminal|radar)|scene-waterway)\.png(?:\?|$)/i.test(value)
    ? value
    : '/assets/bridge-ship-waterway.jpg'
}
</script>

<template>
  <section class="knowledge-page" v-loading="loading">
    <header class="knowledge-head">
      <div>
        <div class="eyebrow">知识中心</div>
        <h1>{{ title }}</h1>
        <p>{{ description }}</p>
      </div>
      <el-button v-if="canManage" type="primary" :icon="Plus" @click="emit('create')">新增{{ title.replace('中心', '') }}</el-button>
    </header>

    <div class="summary-strip" aria-label="数据概况">
      <div><strong>{{ rows.length }}</strong><span>全部{{ centerNoun }}</span></div>
      <div><strong>{{ supportedCount }}</strong><span>正式可用</span></div>
      <div><strong>{{ Math.max(rows.length - supportedCount, 0) }}</strong><span>Beta / 草稿</span></div>
    </div>

    <div class="knowledge-toolbar">
      <el-input v-model="keyword" :prefix-icon="Search" :placeholder="searchPlaceholder" clearable />
      <el-select v-model="status" aria-label="状态筛选">
        <el-option label="全部状态" value="全部状态" />
        <el-option label="正式支持" value="正式支持" />
        <el-option label="在售" value="在售" />
        <el-option label="停售" value="停售" />
      </el-select>
      <div class="view-switch" aria-label="视图切换">
        <el-tooltip content="卡片视图"><el-button :type="viewMode === 'card' ? 'primary' : 'default'" :icon="Grid" aria-label="卡片视图" @click="viewMode = 'card'" /></el-tooltip>
        <el-tooltip content="列表视图"><el-button :type="viewMode === 'list' ? 'primary' : 'default'" :icon="List" aria-label="列表视图" @click="viewMode = 'list'" /></el-tooltip>
      </div>
    </div>

    <el-alert v-if="error" class="state-panel" type="error" :title="error" :closable="false" show-icon>
      <template #default><el-button :icon="Refresh" @click="emit('retry')">重新加载</el-button></template>
    </el-alert>

    <template v-else-if="!loading && visibleRows.length">
      <div v-if="viewMode === 'card'" class="knowledge-grid">
        <article v-for="row in visibleRows" :key="row.id" class="knowledge-card" :class="'center-'+centerKey" tabindex="0" @click="emit('open', row)" @keydown.enter="emit('open', row)">
          <div v-if="centerKey==='software'" class="card-visual"><img :src="(row as any).primaryScreenshot||(row as any).logo||'/assets/solution-overview.png'" :alt="row.name"><span>{{ symbol }}</span></div>
          <div v-else-if="centerKey==='scenes'" class="card-visual"><img :src="sceneImage((row as any).coverImage)" :alt="row.name"><span>{{ row.category }}</span></div>
          <div class="card-top"><span class="record-mark">{{ symbol }}</span><el-tag size="small" effect="plain">{{ statusLabel(row.status) }}</el-tag></div>
          <h2>{{ row.name }}</h2>
          <p>{{ row.summary || '暂无简介' }}</p>
          <div class="metadata"><span v-if="(row as any).code">{{ (row as any).code }}</span><span v-if="row.version">版本 {{ row.version }}</span><span v-if="row.category">{{ row.category }}</span><span v-if="row.scene">{{ row.scene }}</span><span v-if="row.tier">{{ ({STANDARD:'标准型',ENHANCED:'增强型',FLAGSHIP:'旗舰型'} as any)[row.tier]||row.tier }}</span></div>
          <div v-if="centerKey==='software'" class="business-metrics"><span><b>{{ (row as any).moduleCount||0 }}</b>功能模块</span><span><b>{{ (row as any).featureCount||0 }}</b>子功能</span><span><b>{{ ({PRIVATE:'私有化',CLOUD:'云端',HYBRID:'混合'} as any)[(row as any).deploymentMode]||(row as any).deploymentMode }}</b>部署方式</span></div>
          <div v-else-if="centerKey==='algorithms'" class="flow-summary"><span>{{ (row as any).inputSummary||'输入待完善' }}</span><b>→</b><span>{{ (row as any).outputSummary||'输出待完善' }}</span></div>
          <div v-else-if="centerKey==='model-capabilities'" class="business-metrics"><span v-for="metric in ((row as any).metrics||[]).slice(0,3)" :key="metric.id"><b>{{ metric.value }}{{ metric.unit }}</b>{{ metric.name }}</span><span v-if="!(row as any).metrics?.length"><b>待验证</b>核心性能</span></div>
          <div v-else-if="centerKey==='scenes'" class="business-metrics"><span><b>{{ (row as any).relationCounts?.['model-capabilities']||0 }}</b>核心能力</span><span><b>{{ (row as any).relationCounts?.products||0 }}</b>推荐产品</span><span><b>{{ (row as any).relationCounts?.solutions||0 }}</b>标准方案</span></div>
          <div v-else-if="centerKey==='solutions'" class="business-metrics"><span><b>{{ (row as any).architectureCount||0 }}</b>架构对象</span><span><b>{{ (row as any).coverageCount||0 }}</b>能力覆盖</span><span><b>{{ (row as any).bomCount||0 }}</b>BOM品类</span></div>
          <footer><span>查看详情</span><div v-if="canManage"><el-button link @click.stop="emit('edit', row)">编辑</el-button><el-button link type="danger" @click.stop="emit('delete', row)">删除</el-button></div></footer>
        </article>
      </div>
      <el-table v-else :data="visibleRows" class="knowledge-table" row-key="id" @row-click="emit('open', $event)">
        <el-table-column prop="name" label="名称" min-width="210" />
        <el-table-column prop="modelCode" label="型号/版本" min-width="130"><template #default="scope">{{ scope.row.modelCode || scope.row.version || '-' }}</template></el-table-column>
        <el-table-column prop="category" label="分类/场景" min-width="140"><template #default="scope">{{ scope.row.category || scope.row.scene || '-' }}</template></el-table-column>
        <el-table-column prop="summary" label="简介" min-width="280" show-overflow-tooltip />
        <el-table-column label="状态" width="110"><template #default="scope"><el-tag size="small" effect="plain">{{ statusLabel(scope.row.status) }}</el-tag></template></el-table-column>
        <el-table-column v-if="canManage" label="操作" width="120" fixed="right"><template #default="scope"><el-button link @click.stop="emit('edit', scope.row)">编辑</el-button><el-button link type="danger" @click.stop="emit('delete', scope.row)">删除</el-button></template></el-table-column>
      </el-table>
    </template>

    <el-empty v-else-if="!loading" class="state-panel" description="暂无匹配的知识条目" />
  </section>
</template>

<style scoped>
.knowledge-page{display:grid;gap:18px}.knowledge-head{display:flex;align-items:flex-start;justify-content:space-between;gap:24px}.knowledge-head h1{margin:4px 0 6px;font-size:26px;line-height:1.25;color:#14233c}.knowledge-head p{margin:0;color:#66758d}.eyebrow{font-size:12px;color:#146ef5;font-weight:700}.summary-strip{display:grid;grid-template-columns:repeat(3,minmax(0,160px));gap:32px;padding:14px 20px;background:#fff;border:1px solid #e5ebf3;border-radius:8px}.summary-strip div{display:flex;align-items:baseline;gap:8px}.summary-strip strong{font-size:22px;color:#14233c}.summary-strip span{font-size:13px;color:#7a879b}.knowledge-toolbar{display:grid;grid-template-columns:minmax(260px,520px) 150px 1fr;gap:10px;align-items:center}.view-switch{justify-self:end;display:flex}.view-switch :deep(.el-button){width:36px;padding:0}.knowledge-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.knowledge-card{min-width:0;min-height:218px;padding:18px;background:#fff;border:1px solid #e4eaf2;border-radius:8px;cursor:pointer;transition:border-color .16s,box-shadow .16s,transform .16s}.knowledge-card:hover,.knowledge-card:focus{outline:0;border-color:#8bb9ff;box-shadow:0 8px 24px rgba(31,83,148,.1);transform:translateY(-1px)}.card-top,.knowledge-card footer{display:flex;align-items:center;justify-content:space-between;gap:12px}.record-mark{display:grid;place-items:center;width:38px;height:38px;border-radius:7px;background:#eaf3ff;color:#146ef5;font-weight:700}.knowledge-card h2{margin:16px 0 7px;font-size:17px;letter-spacing:0;color:#17263e}.knowledge-card p{height:42px;margin:0;color:#67758a;font-size:14px;line-height:1.5;overflow:hidden}.metadata{display:flex;gap:7px;min-height:28px;margin-top:13px;overflow:hidden}.metadata span{white-space:nowrap;padding:3px 7px;background:#f2f6fa;border-radius:4px;font-size:12px;color:#52647c}.knowledge-card footer{margin-top:12px;padding-top:11px;border-top:1px solid #edf1f6;font-size:13px;color:#146ef5}.state-panel{min-height:180px}.knowledge-table{width:100%;border:1px solid #e4eaf2;border-radius:8px;overflow:hidden}@media(max-width:1200px){.knowledge-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:760px){.knowledge-head{align-items:stretch;flex-direction:column}.knowledge-toolbar{grid-template-columns:1fr 130px}.view-switch{grid-column:1/-1;justify-self:start}.summary-strip{grid-template-columns:repeat(3,1fr);gap:8px}.summary-strip div{display:grid}.knowledge-grid{grid-template-columns:1fr}}
.knowledge-card{position:relative;min-height:300px}.card-visual{position:relative;height:120px;margin:-18px -18px 14px;overflow:hidden;border-radius:8px 8px 0 0;background:#eef5fc}.card-visual img{width:100%;height:100%;object-fit:cover}.card-visual>span{position:absolute;left:10px;bottom:9px;padding:3px 7px;background:rgba(18,43,68,.82);color:#fff;font-size:11px}.center-software .card-top,.center-scenes .card-top{position:absolute;top:10px;right:10px}.center-software .record-mark,.center-scenes .record-mark{display:none}.record-mark{width:auto;min-width:40px;height:34px;padding:0 7px;border-radius:5px;font-size:11px}.center-algorithms .record-mark{background:#f0edff;color:#6654d9}.center-model-capabilities .record-mark{background:#e8f8f7;color:#099892}.center-solutions .record-mark{background:#fff3df;color:#ad6d0d}.business-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;min-height:54px;margin-top:10px}.business-metrics span{display:grid;padding:7px;background:#f6f9fc;color:#78869a;font-size:10px}.business-metrics b{color:#263a56;font-size:13px;overflow:hidden;text-overflow:ellipsis}.flow-summary{display:grid;grid-template-columns:1fr 22px 1fr;align-items:center;gap:4px;min-height:54px;margin-top:10px;padding:8px;background:#183f5e;color:#dbe9f3;font-size:11px}.flow-summary b{text-align:center;color:#56ded7}
</style>
