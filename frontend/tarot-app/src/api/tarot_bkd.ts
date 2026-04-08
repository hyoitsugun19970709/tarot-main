// src/api/tarot_bkd.ts
import Taro from '@tarojs/taro'

const BASE_URL = "http://127.0.0.1:8000"

// =====================
// 通用 request 封装
// =====================
async function request<T>(
  url: string,
  method: "GET" | "POST",
  data?: any
): Promise<T> {

  const res = await Taro.request({
    url: `${BASE_URL}${url}`,
    method,
    data
  })

  if (res.statusCode !== 200) {
    throw new Error(`HTTP ${res.statusCode}: ${res.errMsg}`)
  }

  return res.data as T
}

// =====================
// Tarot API
// =====================
type DrawRequest = {
  name: string
  arcana?: string
  orientation?: string
}

type DrawResponse = any

type HealthResponse = {
  status: string
}

type SpreadResponse = {
  spreads: string[]
}


export const tarotApi = {

  // GET /health
  health: () => {
    return request<HealthResponse>("/health", "GET")
  },

  // GET /spreads
  spreads: () => {
    return request<SpreadResponse>("/spreads", "GET")
  },

  // POST /draw
  draw: (req: DrawRequest) => {
    const {
      name,
      arcana = "full",
      orientation = "random"
    } = req

    return request<DrawResponse>("/draw", "POST", {
      id: `taro-${Date.now()}`,
      name,
      arcana,
      orientation
    })
  },

  // POST /cleanup
  cleanup: () => {
    return request("/cleanup", "POST")
  }
}