import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api/index.js'

export const useConsultStore = defineStore('consult', () => {
  const consultations = ref([])
  const currentConsultation = ref(null)
  const messages = ref([])

  async function fetchConsultations() {
    const res = await api.get('/api/v1/consult/')
    consultations.value = res.data
    return res
  }

  async function createConsultation(title = '新问诊') {
    const res = await api.post('/api/v1/consult/', { title })
    consultations.value.unshift(res.data)
    return res.data
  }

  async function fetchConsultation(id) {
    const res = await api.get(`/api/v1/consult/${id}`)
    currentConsultation.value = res.data
    messages.value = res.data.messages || []
    return res.data
  }

  function addMessage(message) {
    messages.value.push(message)
  }

  return {
    consultations, currentConsultation, messages,
    fetchConsultations, createConsultation, fetchConsultation, addMessage,
  }
})
