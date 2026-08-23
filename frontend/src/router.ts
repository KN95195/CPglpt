import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

export const knowledgeCenters = [
  { key: 'products', path: '/products', label: '产品中心' },
  { key: 'software', path: '/software', label: '软件中心' },
  { key: 'algorithms', path: '/algorithms', label: '算法中心' },
  { key: 'model-capabilities', path: '/model-capabilities', label: '模型能力中心' },
  { key: 'scenes', path: '/scenes', label: '场景中心' },
  { key: 'solutions', path: '/solutions', label: '方案中心' },
] as const

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: { template: '<span />' } },
  ...knowledgeCenters.flatMap((center) => [
    { path: center.path, name: center.key, component: { template: '<span />' } },
    { path: `${center.path}/:id`, name: `${center.key}-detail`, component: { template: '<span />' }, props: true },
  ]),
  { path: '/system-admin', name: 'system-admin', component: { template: '<span />' } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({ history: createWebHistory(), routes })
