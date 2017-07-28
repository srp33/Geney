const router = require('express').Router();

const datasets = require('../../ui/api/datasets.json');
const lincslevel2 = require('../../ui/api/lincslevel2.json');


router.get('/api/datasets', (req, res, next) => {
  res.json(datasets);
});

router.get('/api/datasets/lincslevel2/meta', (req, res, next) => {
  res.json(lincslevel2);
});

router.get('/api/datasets/validate', (req, res, next) => {
  res.json(req.query.val !== 'lincslevel2');
});

router.put('/api/datasets', (req, res, next) => {
  res.sendStatus(202);
  console.log(req);
});

router.post('/api/datasets/:id/samples', (req, res, next) => {
  res.json(428);
});

router.post('/api/datasets/:id/download', (req, res, next) => {
  let query = JSON.parse(req.body.query);
  let filename = query.options.filename + '.' + query.options.fileformat;
  res.header({
    'Content-Type': 'text/plain',
    'Content-disposition': 'attachment; filename=' + filename,
  });
  res.send('YAY!');
  res.end();
});

router.patch('/api/datasets/:id', (req, res, next) => {
  res.json(true);
});

module.exports = router;
