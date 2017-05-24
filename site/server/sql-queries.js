module.exports = {
  create: 'CREATE TABLE IF NOT EXISTS `users` (`id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, `username` TEXT NOT NULL UNIQUE, `email` TEXT NOT NULL, `passhash` TEXT NOT NULL, `firstname` TEXT NOT NULL, `lastname` TEXT NOT NULL, `privileges` TEXT NOT NULL, `email_reset_id` TEXT, `failed_attempts` INTEGER NOT NULL );',
  getUser: 'SELECT * FROM `users` WHERE `username` = $username;',
  updateFailedAttempts: 'UPDATE `users` SET failed_attempts = $fails WHERE username = $username;'
}
