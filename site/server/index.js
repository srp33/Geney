let path = require('path')
let express = require('express')
let sqlite3 = require('sqlite3')
let queries = require('./sql-queries')
let config = require('../config')
let jwt = require('express-jwt')
let token = require('jsonwebtoken')
let bcrypt = require('bcryptjs')
let bodyParser = require('body-parser')
let datasets = require('../ui/api/datasets.json')
let lincslevel2 = require('../ui/api/lincslevel2.json')

const tokenConfig = {algorithm: 'HS512', expiresIn: '30m'}

let db = new sqlite3.Database(path.join(__dirname, 'geney.db'))
db.run(queries.create, err => {
  if (err) {
    console.error(err)
    process.exit(1)
  }
})

if (!process.env.NODE_ENV) {
  process.env.NODE_ENV = JSON.parse(config.dev.env.NODE_ENV)
}

var port = process.env.NODE_ENV === 'development'
  ? config.dev.backendPort
  : config.prod.port

let app = express()

app.use(bodyParser.urlencoded({ extended: false }))
app.use(bodyParser.json())

app.use(jwt({secret: config.dev.secret, credentialsRequired: false}))

// TODO: REMOVE THESE
app.get('/api/datasets', (req, res, next) => {
  res.json(datasets)
})

app.get('/api/meta/lincslevel2', (req, res, next) => {
  res.json(lincslevel2)
})

app.get('/api/admin/validate/id', (req, res, next) => {
  res.json(req.query.val !== 'lincslevel2')
})

app.post('/api/admin/newdataset/', (req, res, next) => {
  res.end()
})

app.post('/api/:id/samples', (req, res, next) => {
  res.json(428)
})

app.post('/api/:id/download', (req, res, next) => {
  let query = JSON.parse(req.body.query)
  let filename = query.options.filename + '.' + query.options.fileformat
  res.header({
    "Content-Type": 'text/plain',
    "Content-disposition": "attachment; filename="+filename
  })
  res.send('YAY!')
  res.end()
})

app.post('/api/:id/update', (req, res, next) => {
  console.log(req.body)
  res.send(true)
  res.end()
})
// END TODO

app.post('/auth/login', (req, res, next) => {
  if (req.user) console.error('TOKEN EXISTS')
  db.get(queries.getUser, {$username: req.body.username}, (err, user) => {
    if (err) console.error(err)
    // check if user exists
    if (user) {
      bcrypt.compare(req.body.password, user.passhash, (err, valid) => {
        if (err) console.error(err)
        // check if password was right
        if (valid === true) {
          let userObj = {
            username: user.username,
            firstname: user.firstname,
            lastname: user.lastname,
            email: user.email,
            privileges: JSON.parse(user.privileges)
          }
          token.sign(userObj, config.dev.secret, tokenConfig, (err, jwt) => {
            if (err) console.error(err)
            console.log('Authenticated')
            res.json({'jwt': jwt})
          })
        } else {
          db.run(queries.updateFailedAttempts, {$fails: (user['failed_attempts'] + 1), $username: user.username})
          res.json({})
        }
      })
    } else {
      res.json({})
    }
  })
  // bcrypt.hash('password', 10, (err, hash) => {
  //   if (err) console.log(err)
  //   console.log(hash)
  // })
})

module.exports = app.listen(port, (err) => {
  if (err) {
    console.log(err)
    return
  }
  console.log('Listening on port ' + port)
})
