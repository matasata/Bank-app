import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error(`[API Error] ${error.response.status}: ${error.response.data?.detail || error.message}`);
    } else if (error.request) {
      console.error('[API Error] No response received from server');
    } else {
      console.error(`[API Error] ${error.message}`);
    }
    return Promise.reject(error);
  }
);

// ─── Character Endpoints ──────────────────────────────────────────────────────

export const characterAPI = {
  rollAbilities: (method: string) =>
    api.post('/characters/roll-abilities', { method }),
  create: (data: Record<string, unknown>) =>
    api.post('/characters', data),
  get: (id: string) =>
    api.get(`/characters/${id}`),
  list: () =>
    api.get('/characters'),
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/characters/${id}`, data),
  delete: (id: string) =>
    api.delete(`/characters/${id}`),
};

// ─── Party Endpoints ──────────────────────────────────────────────────────────

export const partyAPI = {
  create: (data: Record<string, unknown>) =>
    api.post('/party', data),
  get: (id: string) =>
    api.get(`/party/${id}`),
  updateMarchingOrder: (id: string, order: Record<string, unknown>) =>
    api.put(`/party/${id}/marching-order`, order),
};

// ─── Dungeon Endpoints ────────────────────────────────────────────────────────

export const dungeonAPI = {
  generate: (params: Record<string, unknown>) =>
    api.post('/dungeon/generate', params),
  get: (id: string) =>
    api.get(`/dungeon/${id}`),
  move: (dungeonId: string, direction: string) =>
    api.post(`/dungeon/${dungeonId}/move`, { direction }),
  interact: (dungeonId: string, action: Record<string, unknown>) =>
    api.post(`/dungeon/${dungeonId}/interact`, action),
  searchRoom: (dungeonId: string) =>
    api.post(`/dungeon/${dungeonId}/search`),
};

// ─── Combat Endpoints ─────────────────────────────────────────────────────────

export const combatAPI = {
  start: (data: Record<string, unknown>) =>
    api.post('/combat/start', data),
  rollInitiative: (combatId: string) =>
    api.post(`/combat/${combatId}/initiative`),
  action: (combatId: string, action: Record<string, unknown>) =>
    api.post(`/combat/${combatId}/action`, action),
  nextTurn: (combatId: string) =>
    api.post(`/combat/${combatId}/next-turn`),
  endCombat: (combatId: string) =>
    api.post(`/combat/${combatId}/end`),
};

// ─── Game Session Endpoints ───────────────────────────────────────────────────

export const sessionAPI = {
  save: (data: Record<string, unknown>) =>
    api.post('/session/save', data),
  load: (slotId: string) =>
    api.get(`/session/load/${slotId}`),
  listSaves: () =>
    api.get('/session/saves'),
  deleteSave: (slotId: string) =>
    api.delete(`/session/saves/${slotId}`),
};

// ─── Module Endpoints ─────────────────────────────────────────────────────────

export const moduleAPI = {
  list: () =>
    api.get('/modules'),
  get: (id: string) =>
    api.get(`/modules/${id}`),
  load: (id: string) =>
    api.post(`/modules/${id}/load`),
};

// ─── Equipment Endpoints ──────────────────────────────────────────────────────

export const equipmentAPI = {
  list: (category?: string) =>
    api.get('/equipment', { params: { category } }),
  get: (id: string) =>
    api.get(`/equipment/${id}`),
};

// ─── Dice Endpoints ───────────────────────────────────────────────────────────

export const diceAPI = {
  roll: (notation: string) =>
    api.post('/dice/roll', { notation }),
};

export default api;
