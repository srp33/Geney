module.exports = {
  create: 'CREATE TABLE IF NOT EXISTS `users` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `username` TEXT NOT NULL UNIQUE, `email` TEXT NOT NULL, `passhash` TEXT NOT NULL, `firstname` TEXT NOT NULL, `lastname` TEXT NOT NULL, `privileges` TEXT NOT NULL, `email_reset_id` TEXT, `failed_attempts` INTEGER NOT NULL );',
  getUser: 'SELECT * FROM `users` WHERE `username` = (?);',
  incrementFailedAttempts: 'UPDATE `users` SET failed_attempts = failed_attempts + 1 WHERE username = (?);',
  resetFailedAttempts: 'UPDATE `users` SET failed_attempts = 0 WHERE username = (?);',
  getAllUsers: 'SELECT username, email, firstname, lastname, privileges FROM `users`;',
  addUser: 'INSERT INTO `users` (username, firstname, lastname, email, passhash, privileges, failed_attempts) VALUES((?),(?),(?),(?),(?),(?),(?));',
  updateUser: 'UPDATE `users` SET firstname = (?), lastname = (?), email = (?), privileges = (?) WHERE username = (?);',
  updateUserWithPassword: 'UPDATE `users` SET firstname = (?), lastname = (?), email = (?), privileges = (?), passhash = (?) WHERE username = (?);',
  deleteUser: 'DELETE FROM `users` WHERE username = (?);',
};
