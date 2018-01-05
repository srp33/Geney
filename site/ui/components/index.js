module.exports = {
  Home: require('./main/Home'),
  Description: require('./main/Description'),
  Filter: require('./main/Filter'),
  Download: require('./main/Download'),
  Error404: require('./shared/Error404'),
  Contact: require('./shared/Contact'),
  // The below components are disabled until we have need for the admin login
  // Login: require('./shared/Login'),
  // Admin: require('./admin/Admin'),
  // ManageDatasets: require('./admin/datasets/ManageDatasets'),
  // AddDataset: require('./admin/datasets/AddDataset'),
  // EditDataset: require('./admin/datasets/EditDataset'),
  // ManageUsers: require('./admin/users/ManageUsers'),
  // AddUser: require('./admin/users/AddUser'),
  // EditUser: require('./admin/users/EditUser'),
};
