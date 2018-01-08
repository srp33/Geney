import Vue from 'vue';
import Router from 'vue-router';
import Components from 'components';
Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Components.Home,
    },
    {
      path: '/404',
      name: 'DatasetNotFound',
      component: Components.Error404,
    },
    {
      path: '/about',
      name: 'About',
      component: Components.About,
    },
    {
      path: '/dataset/:dataset/',
      name: 'Description',
      component: Components.Description,
    },
    {
      path: '/dataset/:dataset/filter/',
      name: 'Filter',
      component: Components.Filter,
    },
    {
      path: '/dataset/:dataset/filter/download',
      name: 'Download',
      component: Components.Download,
    },
    // {
    //   path: '/login',
    //   name: 'Login',
    //   component: Components.Login,
    // },
    // {
    //   path: '/admin',
    //   name: 'Admin',
    //   component: Components.Admin,
    //   children: [
    //     {
    //       path: 'datasets',
    //       name: 'ManageDatasets',
    //       component: Components.ManageDatasets,
    //     },
    //     {
    //       path: 'datasets/add',
    //       name: 'AddDataset',
    //       component: Components.AddDataset,
    //     },
    //     {
    //       path: 'datasets/:dataset',
    //       name: 'EditDataset',
    //       component: Components.EditDataset,
    //     },
    //     {
    //       path: 'users',
    //       name: 'ManageUsers',
    //       component: Components.ManageUsers,
    //     },
    //     {
    //       path: 'users/add',
    //       name: 'AddUser',
    //       component: Components.AddUser,
    //     },
    //     {
    //       path: 'users/:user',
    //       name: 'EditUser',
    //       component: Components.EditUser,
    //     },
    //   ],
    // },
    {
      path: '*',
      name: '404',
      component: Components.Error404,
    },

  ],
});
