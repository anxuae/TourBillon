import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    redirect: { name: 'admin-tournament' },
    children: [
      {
        path: 'tournament',
        name: 'admin-tournament',
        component: () => import('@/views/admin/AdminTournament.vue'),
      },
      {
        path: 'teams',
        name: 'admin-teams',
        component: () => import('@/views/admin/AdminTeams.vue'),
      },
      {
        path: 'round',
        name: 'admin-round',
        component: () => import('@/views/admin/AdminRound.vue'),
      },
      {
        path: 'draw',
        name: 'admin-draw',
        component: () => import('@/views/admin/AdminDraw.vue'),
      },
      {
        path: 'rankings',
        name: 'admin-rankings',
        component: () => import('@/views/admin/AdminRankings.vue'),
      },
    ],
  },
  {
    path: '/display',
    name: 'display',
    component: () => import('@/views/display/DisplayLayout.vue'),
    redirect: { name: 'display-rankings' },
    children: [
      {
        path: 'teams',
        name: 'display-teams',
        component: () => import('@/views/display/DisplayTeams.vue'),
      },
      {
        path: 'rankings',
        name: 'display-rankings',
        component: () => import('@/views/display/DisplayRankings.vue'),
      },
      {
        path: 'round',
        name: 'display-round',
        component: () => import('@/views/display/DisplayRound.vue'),
      },
    ],
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('@/views/history/HistoryLayout.vue'),
    redirect: { name: 'history-players' },
    children: [
      {
        path: 'players',
        name: 'history-players',
        component: () => import('@/views/history/HistoryPlayers.vue'),
      },
      {
        path: 'players/:name',
        name: 'history-player',
        component: () => import('@/views/history/HistoryPlayerDetail.vue'),
        props: true,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Admin tabs other than "Tournament" require a loaded tournament. Guard direct
// URL access: if none is loaded, redirect to the tournament create/load view.
const ADMIN_OPEN_ROUTES = new Set(['admin', 'admin-tournament'])

router.beforeEach(async (to) => {
  if (!to.name || !String(to.name).startsWith('admin')) return true
  if (ADMIN_OPEN_ROUTES.has(to.name)) return true

  const { useTournamentStore } = await import('@/stores/tournament')
  const store = useTournamentStore()
  if (!store.tournament) {
    await store.refreshTournament()
  }
  if (!store.tournament) {
    return { name: 'admin-tournament' }
  }

  if (
    (to.name === 'admin-round' || to.name === 'admin-draw')
    && store.tournament.nb_teams < store.tournament.teams_by_match
  ) {
    return { name: 'admin-teams' }
  }

  if (to.name === 'admin-draw') {
    if (!store.rounds.length) {
      await store.refreshRounds()
    }
    if (store.rounds.length) {
      const lastRound = store.rounds[store.rounds.length - 1]
      if (!['complete', 'finished'].includes(lastRound.status)) {
        return { name: 'admin-round' }
      }
    }
  }

  if (to.name === 'admin-rankings') {
    if (!store.rounds.length) {
      await store.refreshRounds()
    }
    const canOpenRankings = store.rounds.some((round) =>
      ['complete', 'finished'].includes(round.status),
    )
    if (!canOpenRankings) {
      return { name: 'admin-round' }
    }
  }

  return true
})

export default router
