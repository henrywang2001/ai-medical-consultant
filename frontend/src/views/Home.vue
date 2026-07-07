<template>
  <div class="home-page">
    <!-- Premium Header -->
    <header class="app-header">
      <div class="header-left">
        <div class="brand-logo-mini">
          <svg width="32" height="32" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="30" fill="#4F8DFF" fill-opacity="0.1" stroke="#4F8DFF" stroke-width="2"/>
            <path d="M32 16V48M16 32H48" stroke="#4F8DFF" stroke-width="4" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="brand-name">AI 智能问诊</span>
      </div>
      <div class="header-right">
        <el-badge :value="3" :hidden="false" class="notification-badge">
          <el-button circle :icon="Bell" class="header-icon-btn" />
        </el-badge>
        <el-dropdown trigger="click">
          <div class="user-avatar">
            <span class="avatar-text">{{ userStore.username?.charAt(0).toUpperCase() || 'U' }}</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">
                <el-icon><SwitchButton /></el-icon> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- Main Content -->
    <main class="app-main">
      <!-- Welcome Section -->
      <section class="welcome-section">
        <div class="welcome-text">
          <h1>您好，{{ userStore.username }}</h1>
          <p>基于 LLM + Agent + RAG 的智能医疗问诊系统</p>
        </div>
        <div class="welcome-decoration">
          <svg width="120" height="80" viewBox="0 0 120 80" fill="none">
            <path d="M10 50 Q30 20 50 40 Q70 60 90 30 Q110 0 120 20" stroke="url(#welcomeGrad)" stroke-width="2" fill="none" opacity="0.3"/>
            <defs>
              <linearGradient id="welcomeGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#4F8DFF"/>
                <stop offset="100%" stop-color="#7C4DFF"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
      </section>

      <!-- Stats Cards -->
      <section class="stats-grid">
        <div class="stat-card" v-for="(stat, i) in stats" :key="i" :style="{ animationDelay: (0.1 + i * 0.1) + 's' }">
          <div class="stat-icon" :style="{ background: stat.bg }">
            <el-icon :size="22" :color="stat.color"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
          <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
            {{ stat.trend > 0 ? '+' : '' }}{{ stat.trend }}%
          </div>
        </div>
      </section>

      <!-- Quick Actions -->
      <section class="quick-actions">
        <div class="section-header">
          <h3>快捷操作</h3>
        </div>
        <div class="actions-grid">
          <div class="action-card" @click="startNewConsult">
            <div class="action-icon" style="background: linear-gradient(135deg, #4F8DFF 0%, #3A6FD9 100%);">
              <el-icon :size="24" color="white"><Plus /></el-icon>
            </div>
            <span class="action-label">开始新问诊</span>
            <span class="action-desc">描述症状，获取 AI 分析</span>
          </div>
          <div class="action-card" @click="$router.push('/knowledge')">
            <div class="action-icon" style="background: linear-gradient(135deg, #34C759 0%, #28A745 100%);">
              <el-icon :size="24" color="white"><Document /></el-icon>
            </div>
            <span class="action-label">知识库</span>
            <span class="action-desc">查阅医学资料</span>
          </div>
          <div class="action-card">
            <div class="action-icon" style="background: linear-gradient(135deg, #FF9500 0%, #E68600 100%);">
              <el-icon :size="24" color="white"><Memo /></el-icon>
            </div>
            <span class="action-label">我的病历</span>
            <span class="action-desc">查看问诊记录</span>
          </div>
          <div class="action-card">
            <div class="action-icon" style="background: linear-gradient(135deg, #7C4DFF 0%, #651FFF 100%);">
              <el-icon :size="24" color="white"><TrendCharts /></el-icon>
            </div>
            <span class="action-label">健康建议</span>
            <span class="action-desc">个性化健康指导</span>
          </div>
        </div>
      </section>

      <!-- Consultation History -->
      <section class="consult-section">
        <div class="section-header">
          <h3>问诊记录</h3>
          <span class="section-count" v-if="consultations.length > 0">共 {{ consultations.length }} 条</span>
        </div>

        <!-- Empty State -->
        <div v-if="consultations.length === 0" class="empty-state">
          <div class="empty-illustration">
            <svg width="160" height="120" viewBox="0 0 160 120" fill="none">
              <rect x="20" y="30" width="120" height="80" rx="12" fill="#F0F6FF" stroke="#D0E0FF" stroke-width="2"/>
              <path d="M60 70 L70 60 L85 75 L100 55 L105 60" stroke="#4F8DFF" stroke-width="3" stroke-linecap="round"/>
              <circle cx="55" cy="55" r="3" fill="#4F8DFF"/>
              <circle cx="105" cy="50" r="3" fill="#4F8DFF"/>
            </svg>
          </div>
          <h4>暂无问诊记录</h4>
          <p>点击「开始新问诊」体验 AI 医疗咨询</p>
        </div>

        <!-- Table -->
        <div v-else class="consult-table-wrapper">
          <el-table :data="consultations" class="premium-table" style="width: 100%">
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <span :class="['status-tag', row.status]">
                  <span class="status-dot"></span>
                  {{ row.status === 'active' ? '进行中' : '已完成' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" min-width="160">
              <template #default="{ row }">
                <span class="time-text">{{ new Date(row.updated_at).toLocaleString('zh-CN') }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" class="table-action-btn" @click="$router.push(`/consult/${row.id}`)">
                  进入问诊
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/useUserStore'
import { useConsultStore } from '../stores/useConsultStore'
import { Plus, Document, Memo, TrendCharts, Bell, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const consultStore = useConsultStore()

const creating = ref(false)
const consultations = ref([])

const stats = reactive([
  { label: '问诊总数', value: '--', icon: 'ChatLineSquare', bg: 'linear-gradient(135deg, #E8F4FD 0%, #D0EAFC 100%)', color: '#4F8DFF', trend: 0 },
  { label: '进行中', value: '--', icon: 'Clock', bg: 'linear-gradient(135deg, #E8F8E8 0%, #C8F0C8 100%)', color: '#34C759', trend: 0 },
  { label: '知识库', value: '--', icon: 'Document', bg: 'linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%)', color: '#FF9500', trend: 0 },
])

onMounted(async () => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  await userStore.fetchUser()
  await loadConsultations()
})

async function loadConsultations() {
  try {
    await consultStore.fetchConsultations()
    consultations.value = consultStore.consultations
    stats[0].value = consultations.value.length
    stats[1].value = consultations.value.filter(c => c.status === 'active').length
  } catch {
    // handled
  }
}

async function startNewConsult() {
  creating.value = true
  try {
    const data = await consultStore.createConsultation()
    router.push(`/consult/${data.id}`)
  } catch {
    // handled
  } finally {
    creating.value = false
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f7fa;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ========= Premium Header ========= */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  padding: 0 32px;
  height: 64px;
  border-bottom: 1px solid rgba(0,0,0,0.04);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo-mini {
  display: flex;
  align-items: center;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #4F8DFF, #7C4DFF);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: #f5f7fa;
  border-radius: 10px;
  font-size: 18px;
  transition: all 0.3s;
}
.header-icon-btn:hover {
  background: #e8ecf1;
}

.notification-badge :deep(.el-badge__content) {
  background: #FF3B30;
  border: 2px solid white;
  font-size: 10px;
  height: 18px;
  min-width: 18px;
  line-height: 14px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #4F8DFF, #7C4DFF);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}
.user-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(79,141,255,0.3);
}
.avatar-text {
  color: white;
  font-size: 16px;
  font-weight: 600;
}

/* ========= Main ========= */
.app-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 24px 60px;
}

/* ========= Welcome Section ========= */
.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 40px 48px;
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.6s ease-out;
}
.welcome-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 80% 50%, rgba(255,255,255,0.08) 0%, transparent 50%);
}
.welcome-text {
  position: relative;
  z-index: 1;
}
.welcome-text h1 {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 8px;
}
.welcome-text p {
  font-size: 15px;
  color: rgba(255,255,255,0.75);
}
.welcome-decoration {
  position: relative;
  z-index: 1;
  opacity: 0.6;
}

/* ========= Stats Grid ========= */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  animation: fadeInUp 0.6s ease-out forwards;
  opacity: 0;
  position: relative;
}
.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
}
.stat-label {
  font-size: 13px;
  color: #8E8E93;
}

.stat-trend {
  position: absolute;
  right: 20px;
  top: 20px;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
}
.stat-trend.up { background: #E8F8E8; color: #34C759; }
.stat-trend.down { background: #FFF0F0; color: #FF3B30; }

/* ========= Quick Actions ========= */
.quick-actions {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
}
.section-count {
  font-size: 13px;
  color: #8E8E93;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  animation: fadeInUp 0.6s ease-out forwards;
  opacity: 0;
}
.action-card:nth-child(1) { animation-delay: 0.1s; }
.action-card:nth-child(2) { animation-delay: 0.2s; }
.action-card:nth-child(3) { animation-delay: 0.3s; }
.action-card:nth-child(4) { animation-delay: 0.4s; }

.action-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(0,0,0,0.08);
}

.action-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.action-label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.action-desc {
  font-size: 12px;
  color: #8E8E93;
}

/* ========= Consult Section ========= */
.consult-section {
  animation: fadeInUp 0.6s ease-out;
  animation-delay: 0.3s;
}

.consult-table-wrapper {
  background: white;
  border-radius: 16px;
  padding: 4px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  overflow: hidden;
}

/* Premium Table */
.premium-table :deep(.el-table__header th) {
  background: #f8f9fc;
  color: #555;
  font-weight: 600;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}
.premium-table :deep(.el-table__row) {
  transition: all 0.2s;
}
.premium-table :deep(.el-table__row:hover) {
  background: #f5f8ff !important;
}
.premium-table :deep(.el-table__body td) {
  border-bottom: 1px solid #f5f5f5;
  padding: 14px 0;
}

/* Status Tags */
.status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}
.status-tag.active {
  background: linear-gradient(135deg, #E8F8E8, #D0F0D0);
  color: #2E7D32;
}
.status-tag.completed {
  background: #f0f0f0;
  color: #666;
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}
.status-tag.active .status-dot { background: #34C759; }
.status-tag.completed .status-dot { background: #999; }

.time-text {
  font-size: 13px;
  color: #666;
}

.table-action-btn {
  border-radius: 8px;
  font-weight: 500;
  padding: 6px 16px;
  background: linear-gradient(135deg, #4F8DFF, #7C4DFF);
  color: white;
  border: none;
  transition: all 0.3s;
}
.table-action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79,141,255,0.3);
}

/* ========= Empty State ========= */
.empty-state {
  background: white;
  border-radius: 16px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.empty-illustration {
  margin-bottom: 20px;
  animation: float 6s ease-in-out infinite;
}
.empty-state h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}
.empty-state p {
  font-size: 14px;
  color: #8E8E93;
}
</style>
