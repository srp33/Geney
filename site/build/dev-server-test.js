var webpack = require('webpack')
var webpackDevServer = require('webpack-dev-server')


var webpackConfig = process.env.NODE_ENV === 'testing'
  ? require('./webpack.prod.conf')
  : require('./webpack.dev.conf')

var compiler = webpack(webpackConfig);
var server = new webpackDevServer(compiler, {
  hot: true,
  quiet: true
});
server.listen(8080);