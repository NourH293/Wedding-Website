import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // This path loads the WelcomeView component (your wedding page)
      path: '/',
      name: 'home',
      component: WelcomeView, // Use the imported component here
    },
    {
      path: '/rsvp',
      name: 'rsvp',
      // route level code-splitting
      // this generates a separate chunk (rsvp.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/rsvpView.vue'),
    },
  ],
})

export default router
