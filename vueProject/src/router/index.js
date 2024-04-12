import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MaxsticView from '../components/Statisticians/maxstic-Statician.vue'
import CommunityDetectionMult from '../components/Community-Detection-Mult.vue'
import layerStatistician from '@/components/Statisticians/layer-Statistician.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    // {
    //   path: '/about',
    //   name: 'about',
    //   component: () => import('../views/AboutView.vue')
    // }
    {
      path: '/maxstic',
      name: 'maxstic',
      component: MaxsticView
    },
    {
      path: '/communitymult',
      name: 'communitymult',
      component: CommunityDetectionMult
    },
    {
      path: '/layer',
      name: 'layer',
      component: layerStatistician
    }
  ]
})

export default router
