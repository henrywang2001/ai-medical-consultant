<template>
  <div class="knowledge-page">
    <!-- Header -->
    <header class="kb-header">
      <div class="kb-header-left">
        <button class="back-btn" @click="$router.push('/')">
          <el-icon :size="20"><ArrowLeft /></el-icon>
          <span>返回首页</span>
        </button>
      </div>
      <div class="kb-header-center">
        <svg width="28" height="28" viewBox="0 0 64 64" fill="none">
          <circle cx="32" cy="32" r="30" fill="#34C759" fill-opacity="0.08" stroke="#34C759" stroke-width="2"/>
          <rect x="24" y="20" width="16" height="24" rx="3" fill="#34C759" fill-opacity="0.12"/>
          <path d="M28 28H36M28 34H36" stroke="#34C759" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <h3>医学知识库</h3>
      </div>
      <div class="kb-header-right">
        <el-button class="add-knowledge-btn" @click="showDrawer = true">
          <el-icon><Plus /></el-icon> 添加知识
        </el-button>
      </div>
    </header>

    <!-- Main -->
    <main class="kb-main">
      <!-- Stats Cards -->
      <div class="kb-stats" v-if="stats">
        <div class="kb-stat-card">
          <div class="kb-stat-icon" style="background: linear-gradient(135deg, #E8F4FD, #D0EAFC); color: #4F8DFF;">
            <el-icon :size="24"><Document /></el-icon>
          </div>
          <div class="kb-stat-info">
            <span class="kb-stat-value">{{ stats.total_documents }}</span>
            <span class="kb-stat-label">知识库文档</span>
          </div>
        </div>
        <div class="kb-stat-card">
          <div class="kb-stat-icon" style="background: linear-gradient(135deg, #E8F8E8, #C8F0C8); color: #34C759;">
            <el-icon :size="24"><Connection /></el-icon>
          </div>
          <div class="kb-stat-info">
            <span class="kb-stat-value">{{ stats.vector_count }}</span>
            <span class="kb-stat-label">向量索引</span>
          </div>
        </div>
      </div>

      <!-- Search -->
      <div class="kb-search-section">
        <div class="search-box">
          <el-icon class="search-icon"><Search /></el-icon>
          <input
            v-model="searchQuery"
            placeholder="搜索医学知识（例如：感冒、高血压、糖尿病）"
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
            <el-icon><Close /></el-icon>
          </button>
        </div>
        <div class="search-hints" v-if="!searchResults.length && !searching">
          <span class="hint-label">热门搜索：</span>
          <span class="hint-tag" @click="searchQuery = '感冒'; handleSearch()">感冒</span>
          <span class="hint-tag" @click="searchQuery = '高血压'; handleSearch()">高血压</span>
          <span class="hint-tag" @click="searchQuery = '糖尿病'; handleSearch()">糖尿病</span>
          <span class="hint-tag" @click="searchQuery = '失眠'; handleSearch()">失眠</span>
        </div>
      </div>

      <!-- Search Results -->
      <div class="kb-results" v-if="searchResults.length > 0">
        <div class="results-header">
          <h4>搜索结果 <span class="results-count">({{ searchResults.length }} 条)</span></h4>
        </div>
        <div v-for="(item, i) in searchResults" :key="i" class="result-card" :style="{ animationDelay: i * 0.08 + 's' }">
          <div class="result-card-content">
            <div class="result-top">
              <h5 class="result-title">{{ item.title }}</h5>
              <span :class="['result-category', item.category]">
                {{ categoryLabel(item.category) }}
              </span>
            </div>
            <div class="result-body" v-html="renderMd(item.content)"></div>
            <div class="result-footer">
              <div class="result-score">
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: (item.score * 100) + '%' }"></div>
                </div>
                <span class="score-text">相关性 {{ (item.score * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Default: All Documents -->
      <div class="kb-results" v-if="!searchResults.length && !searching && allDocuments.length > 0">
        <div class="results-header">
          <h4>全部知识 <span class="results-count">({{ allDocuments.length }} 条)</span></h4>
        </div>
        <div v-for="(item, i) in allDocuments" :key="item.id" class="result-card" :style="{ animationDelay: i * 0.06 + 's' }">
          <div class="result-card-content">
            <div class="result-top">
              <h5 class="result-title">{{ item.title }}</h5>
              <span :class="['result-category', item.category]">
                {{ categoryLabel(item.category) }}
              </span>
            </div>
            <div class="result-body" v-html="renderMd(item.content)"></div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div class="empty-state" v-if="!searchResults.length && !searching && allDocuments.length === 0">
        <div class="empty-icon">
          <el-icon :size="48"><Document /></el-icon>
        </div>
        <h4>知识库暂无内容</h4>
        <p>点击右上角「添加知识」按钮，添加第一条医学知识吧</p>
      </div>

      <!-- Loading State -->
      <div v-if="searching" class="loading-state">
        <div class="skeleton-card" v-for="i in 3" :key="i">
          <div class="skeleton-shimmer" style="height: 20px; width: 60%; margin-bottom: 12px;"></div>
          <div class="skeleton-shimmer" style="height: 14px; width: 100%; margin-bottom: 8px;"></div>
          <div class="skeleton-shimmer" style="height: 14px; width: 80%;"></div>
        </div>
      </div>
    </main>

    <!-- Add Knowledge Drawer -->
    <el-drawer
      v-model="showDrawer"
      title="添加医学知识"
      size="480px"
      class="knowledge-drawer"
    >
      <el-form :model="addForm" label-position="top">
        <el-form-item label="标题">
          <el-input v-model="addForm.title" placeholder="例如：普通感冒、高血压..." size="large" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="addForm.category" placeholder="选择分类" size="large" style="width: 100%;">
            <el-option label="疾病知识" value="disease" />
            <el-option label="药品说明" value="drug" />
            <el-option label="检查指标" value="exam" />
            <el-option label="临床指南" value="guideline" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="addForm.content"
            type="textarea"
            :rows="10"
            placeholder="请输入医学知识内容..."
            size="large"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDrawer = false">取消</el-button>
        <el-button type="primary" :loading="adding" @click="handleAddKnowledge">
          添加到知识库
        </el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowLeft, Plus, Search, Close, Document, Connection } from '@element-plus/icons-vue'
import api from '../api/index.js'
import MarkdownIt from 'markdown-it'
import { ElMessage } from 'element-plus'

const md = new MarkdownIt({ breaks: true, html: true })

const stats = ref(null)
const allDocuments = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const searching = ref(false)
const adding = ref(false)
const showDrawer = ref(false)

const addForm = ref({ title: '', category: '', content: '' })

onMounted(async () => {
  try {
    const [statsRes, docsRes] = await Promise.all([
      api.get('/api/v1/knowledge/stats'),
      api.get('/api/v1/knowledge/documents'),
    ])
    stats.value = statsRes.data
    allDocuments.value = docsRes.data || []
  } catch { /* ignore */ }
})

function categoryLabel(value) {
  const map = { disease: '疾病知识', drug: '药品说明', exam: '检查指标', guideline: '临床指南' }
  return map[value] || value
}

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  searching.value = true
  try {
    const res = await api.post('/api/v1/knowledge/search', {
      query: searchQuery.value,
      top_k: 5,
    })
    searchResults.value = res.data
  } catch { /* ignore */ }
  finally { searching.value = false }
}

async function handleAddKnowledge() {
  if (!addForm.value.title || !addForm.value.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  adding.value = true
  try {
    await api.post('/api/v1/knowledge/documents', addForm.value)
    ElMessage.success('知识已添加')
    addForm.value = { title: '', category: '', content: '' }
    showDrawer.value = false
    const res = await api.get('/api/v1/knowledge/stats')
    stats.value = res.data
  } catch { /* ignore */ }
  finally { adding.value = false }
}

function renderMd(text) {
  return md.render(text || '')
}
</script>

<style scoped>
.knowledge-page {
  min-height: 100vh;
  background: #f5f7fa;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ========= Header ========= */
.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(20px);
  padding: 0 32px;
  height: 64px;
  border-bottom: 1px solid rgba(0,0,0,0.04);
  position: sticky;
  top: 0;
  z-index: 10;
}

.kb-header-left, .kb-header-right {
  flex: 1;
}
.kb-header-right {
  display: flex;
  justify-content: flex-end;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  font-size: 14px;
  color: #4F8DFF;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 10px;
  transition: all 0.2s;
}
.back-btn:hover { background: rgba(79,141,255,0.08); }

.kb-header-center {
  display: flex;
  align-items: center;
  gap: 12px;
}
.kb-header-center h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
}

.add-knowledge-btn {
  border-radius: 10px;
  background: linear-gradient(135deg, #34C759, #28A745);
  color: white;
  border: none;
  padding: 10px 20px;
  font-weight: 500;
  transition: all 0.3s;
}
.add-knowledge-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(52,199,89,0.3);
  color: white;
}

/* ========= Main ========= */
.kb-main {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px 60px;
}

/* ========= Stats ========= */
.kb-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.kb-stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  transition: all 0.3s;
  animation: fadeInUp 0.5s ease-out;
}
.kb-stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

.kb-stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kb-stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.kb-stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
}
.kb-stat-label {
  font-size: 13px;
  color: #8E8E93;
}

/* ========= Search ========= */
.kb-search-section {
  margin-bottom: 28px;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 16px;
  padding: 4px 6px 4px 18px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  border: 2px solid transparent;
  transition: all 0.3s;
}
.search-box:focus-within {
  border-color: #4F8DFF;
  box-shadow: 0 0 0 4px rgba(79,141,255,0.08);
}

.search-icon {
  color: #8E8E93;
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
  padding: 14px 0;
  outline: none;
  color: #1a1a2e;
  font-family: inherit;
}
.search-input::placeholder { color: #b0b0b8; }

.search-clear {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border: none;
  background: #f0f2f5;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8E8E93;
  transition: all 0.2s;
}
.search-clear:hover { background: #e8ecf1; }

.search-hints {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.hint-label {
  font-size: 13px;
  color: #8E8E93;
}
.hint-tag {
  padding: 4px 14px;
  background: white;
  border-radius: 20px;
  font-size: 12px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #eee;
}
.hint-tag:hover {
  border-color: #4F8DFF;
  color: #4F8DFF;
  background: rgba(79,141,255,0.04);
}

/* ========= Results ========= */
.kb-results {
  margin-bottom: 24px;
}

.results-header {
  margin-bottom: 16px;
}
.results-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}
.results-count {
  font-size: 14px;
  font-weight: 400;
  color: #8E8E93;
}

.result-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  transition: all 0.3s;
  animation: fadeInUp 0.5s ease-out;
  opacity: 0;
  animation-fill-mode: forwards;
}
.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.result-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
}

.result-category {
  flex-shrink: 0;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
}
.result-category.disease { background: #FFF3E0; color: #E65100; }
.result-category.drug { background: #E8F4FD; color: #1565C0; }
.result-category.exam { background: #E8F8E8; color: #2E7D32; }
.result-category.guideline { background: #F3E5F5; color: #7B1FA2; }

.result-body {
  font-size: 14px;
  line-height: 1.7;
  color: #555;
  max-height: 160px;
  overflow-y: auto;
  margin-bottom: 12px;
}
.result-body :deep(p) { margin: 0 0 8px; }
.result-body :deep(p:last-child) { margin-bottom: 0; }

.result-footer {
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}
.result-score {
  display: flex;
  align-items: center;
  gap: 12px;
}
.score-bar {
  flex: 1;
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
}
.score-fill {
  height: 100%;
  background: linear-gradient(135deg, #4F8DFF, #34C759);
  border-radius: 2px;
  transition: width 0.6s ease;
}
.score-text {
  font-size: 12px;
  color: #8E8E93;
  white-space: nowrap;
}

/* ========= Loading Skeleton ========= */
.loading-state {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.skeleton-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}

/* ========= Empty State ========= */
.empty-state {
  text-align: center;
  padding: 64px 24px;
}
.empty-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: #f0f2f5;
  color: #b0b0b8;
  margin-bottom: 20px;
}
.empty-state h4 {
  font-size: 17px;
  font-weight: 600;
  color: #555;
  margin: 0 0 8px;
}
.empty-state p {
  font-size: 14px;
  color: #8E8E93;
  margin: 0;
}

/* ========= Drawer ========= */
.knowledge-drawer :deep(.el-drawer__header) {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
  padding: 24px 24px 0;
}
.knowledge-drawer :deep(.el-drawer__body) {
  padding: 8px 24px 24px;
}
.knowledge-drawer :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  color: #555;
}
</style>
