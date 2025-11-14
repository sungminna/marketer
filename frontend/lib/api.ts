import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor to handle errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async register(data: { email: string; password: string; company_name: string }) {
    const response = await this.client.post('/api/v1/users/register', data)
    return response.data
  }

  async login(data: { email: string; password: string }) {
    const response = await this.client.post('/api/v1/users/login', data)
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
    }
    return response.data
  }

  async getMe() {
    const response = await this.client.get('/api/v1/users/me')
    return response.data
  }

  // API Keys endpoints
  async getApiKeys() {
    const response = await this.client.get('/api/v1/users/api-keys')
    return response.data.api_keys || []
  }

  async createApiKey(data: { provider: string; api_key: string }) {
    const response = await this.client.post('/api/v1/users/api-keys', data)
    return response.data
  }

  async deleteApiKey(provider: string) {
    const response = await this.client.delete(`/api/v1/users/api-keys/${provider}`)
    return response.data
  }

  // Analytics endpoints
  async getUsageSummary() {
    const response = await this.client.get('/api/v1/analytics/summary')
    return response.data
  }

  async getCostBreakdown() {
    const response = await this.client.get('/api/v1/analytics/cost-breakdown')
    return response.data
  }

  async getDailyStats() {
    const response = await this.client.get('/api/v1/analytics/daily')
    return response.data
  }

  async getQuotaUsage() {
    const response = await this.client.get('/api/v1/analytics/quota')
    return response.data
  }

  // Image generation endpoints
  async generateImage(data: any) {
    const response = await this.client.post('/api/v1/images/generate', data)
    return response.data
  }

  async editImage(data: any) {
    const response = await this.client.post('/api/v1/images/edit', data)
    return response.data
  }

  async prototypeImage(data: any) {
    const response = await this.client.post('/api/v1/images/prototype', data)
    return response.data
  }

  async getImageJob(jobId: string) {
    const response = await this.client.get(`/api/v1/images/jobs/${jobId}`)
    return response.data
  }

  async listImageJobs(page: number = 1, limit: number = 20) {
    const response = await this.client.get('/api/v1/images/jobs', {
      params: { page, limit },
    })
    return response.data
  }

  // Video generation endpoints
  async generateVideo(data: any) {
    const response = await this.client.post('/api/v1/videos/generate', data)
    return response.data
  }

  async generateVideoFromImage(data: any) {
    const response = await this.client.post('/api/v1/videos/from-image', data)
    return response.data
  }

  async removeVideoBackground(data: any) {
    const response = await this.client.post('/api/v1/videos/remove-background', data)
    return response.data
  }

  async getVideoJob(jobId: string) {
    const response = await this.client.get(`/api/v1/videos/jobs/${jobId}`)
    return response.data
  }

  async listVideoJobs(page: number = 1, limit: number = 20) {
    const response = await this.client.get('/api/v1/videos/jobs', {
      params: { page, limit },
    })
    return response.data
  }

  // Batch endpoints
  async createBatch(data: any) {
    const response = await this.client.post('/api/v1/batches', data)
    return response.data
  }

  async listBatches(page: number = 1, limit: number = 20) {
    const response = await this.client.get('/api/v1/batches', {
      params: { page, limit },
    })
    return response.data
  }

  async getBatch(batchId: string) {
    const response = await this.client.get(`/api/v1/batches/${batchId}`)
    return response.data
  }

  async getBatchProgress(batchId: string) {
    const response = await this.client.get(`/api/v1/batches/${batchId}/progress`)
    return response.data
  }

  async getBatchJobs(batchId: string, page: number = 1, limit: number = 20) {
    const response = await this.client.get(`/api/v1/batches/${batchId}/jobs`, {
      params: { page, limit },
    })
    return response.data
  }

  async cancelBatch(batchId: string) {
    const response = await this.client.post(`/api/v1/batches/${batchId}/cancel`)
    return response.data
  }

  // Template endpoints
  async createTemplate(data: any) {
    const response = await this.client.post('/api/v1/templates', data)
    return response.data
  }

  async listTemplates(page: number = 1, limit: number = 20) {
    const response = await this.client.get('/api/v1/templates', {
      params: { page, limit },
    })
    return response.data
  }

  async getPopularTemplates() {
    const response = await this.client.get('/api/v1/templates/popular')
    return response.data
  }

  async getTemplate(templateId: string) {
    const response = await this.client.get(`/api/v1/templates/${templateId}`)
    return response.data
  }

  async updateTemplate(templateId: string, data: any) {
    const response = await this.client.patch(`/api/v1/templates/${templateId}`, data)
    return response.data
  }

  async deleteTemplate(templateId: string) {
    const response = await this.client.delete(`/api/v1/templates/${templateId}`)
    return response.data
  }

  async useTemplate(data: any) {
    const response = await this.client.post('/api/v1/templates/use', data)
    return response.data
  }

  // Team endpoints
  async createTeam(data: { name: string; description?: string }) {
    const response = await this.client.post('/api/v1/teams', data)
    return response.data
  }

  async listTeams() {
    const response = await this.client.get('/api/v1/teams')
    return response.data
  }

  async inviteTeamMember(teamId: string, data: { email: string; role: string }) {
    const response = await this.client.post(`/api/v1/teams/${teamId}/invite`, data)
    return response.data
  }

  async acceptTeamInvitation(data: { token: string }) {
    const response = await this.client.post('/api/v1/teams/accept-invitation', data)
    return response.data
  }

  async getTeamMembers(teamId: string) {
    const response = await this.client.get(`/api/v1/teams/${teamId}/members`)
    return response.data
  }

  async removeTeamMember(teamId: string, userId: string) {
    const response = await this.client.delete(`/api/v1/teams/${teamId}/members/${userId}`)
    return response.data
  }

  // Webhook endpoints
  async createWebhook(data: { url: string; events: string[]; secret?: string }) {
    const response = await this.client.post('/api/v1/webhooks', data)
    return response.data
  }

  async listWebhooks() {
    const response = await this.client.get('/api/v1/webhooks')
    return response.data
  }

  async getWebhook(webhookId: string) {
    const response = await this.client.get(`/api/v1/webhooks/${webhookId}`)
    return response.data
  }

  async updateWebhook(webhookId: string, data: { url?: string; events?: string[]; secret?: string; is_active?: boolean }) {
    const response = await this.client.patch(`/api/v1/webhooks/${webhookId}`, data)
    return response.data
  }

  async deleteWebhook(webhookId: string) {
    const response = await this.client.delete(`/api/v1/webhooks/${webhookId}`)
    return response.data
  }

  async getWebhookDeliveries(webhookId: string, page: number = 1, limit: number = 20) {
    const response = await this.client.get(`/api/v1/webhooks/${webhookId}/logs`, {
      params: { page, limit },
    })
    return response.data
  }
}

export const apiClient = new ApiClient()
