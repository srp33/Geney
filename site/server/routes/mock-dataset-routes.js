const router = require('express').Router();

const datasets = require('./api/datasets.json');
const lincslevel2 = require('./api/lincslevel2.json');
const lincslevel2Genes = require('./api/lincslevel2_genes.json');
const lincslevel2CompoundId = require('./api/lincslevel2_compoundid.json');

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

router.get('/api/datasets/lincslevel2/meta/genes/search/:str', (req, res) => {
  res.json(lincslevel2Genes.filter(gene => gene.indexOf(req.params.str) >= 0));
});

router.get('/api/datasets/lincslevel2/meta/SM_Center_Compound_ID/search/:str', (req, res) => {
  res.json(lincslevel2CompoundId.filter(ops => ops.indexOf(req.params.str) >= 0));
});

module.exports = router;
